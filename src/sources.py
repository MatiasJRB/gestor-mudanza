"""Bounded public HTTP sources; no logins, bypasses, recursive crawling or actions."""
import hashlib
import http.client
import ssl
import ipaddress
import json
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode, urljoin
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

UA='GestorMudanza/0.2'
LIMIT=1500000

def canonical(url):
    p=urlsplit(url)
    if p.scheme not in {'http','https'} or not p.hostname or p.username or p.password:
        raise ValueError('Only public HTTP(S) URLs without credentials')
    if p.port not in {None,80,443}: raise ValueError('Only standard web ports')
    query=urlencode([(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith('utm_') and k not in {'fbclid','gclid'}])
    return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path or '/',query,''))

def public_url(url):
    url=canonical(url); host=urlsplit(url).hostname
    if host.lower()=='localhost' or host.lower().endswith(('.local','.internal')): raise ValueError('Private hosts blocked')
    addresses=socket.getaddrinfo(host,None,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('Non-public network addresses blocked')
    return url

def get(url):
    url=public_url(url);p=urlsplit(url);port=p.port or (443 if p.scheme=='https' else 80)
    # Resolve once, validate every result, then connect to that exact numeric IP.
    addresses=socket.getaddrinfo(p.hostname,port,type=socket.SOCK_STREAM)
    if any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):raise ValueError('Non-public address blocked')
    peer=addresses[0][4][0]
    conn=http.client.HTTPSConnection(p.hostname,port,timeout=15,context=ssl.create_default_context()) if p.scheme=='https' else http.client.HTTPConnection(p.hostname,port,timeout=15)
    conn._create_connection=lambda address, timeout=15, source_address=None:socket.create_connection((peer,port),timeout,source_address)
    try:
        target=p.path or '/'
        if p.query:target+='?'+p.query
        conn.request('GET',target,headers={'User-Agent':UA,'Accept':'text/html,application/json,application/xml,text/xml'})
        r=conn.getresponse()
        if 300<=r.status<400:raise ValueError('Redirect blocked; register the final public URL explicitly')
        if r.status>=400:raise HTTPError(url,r.status,r.reason,r.headers,None)
        raw=r.read(LIMIT+1)
        if len(raw)>LIMIT:raise ValueError('Source exceeds response size limit')
        mime=r.headers.get_content_type()
        if mime not in {'text/html','application/json','application/xml','text/xml','application/rss+xml','text/plain'}:raise ValueError('Unsupported response type')
        return raw.decode(r.headers.get_content_charset() or 'utf-8','replace')
    finally:conn.close()

def fetch(url):
    url=public_url(url);p=urlsplit(url)
    robots_url=urlunsplit((p.scheme,p.netloc,'/robots.txt','',''))
    try: rules=get(robots_url)
    except HTTPError as e:
        if e.code==404: rules=''
        else: raise ValueError('Robots unavailable; refusing automatic fetch')
    robot=RobotFileParser();robot.parse(rules.splitlines())
    if not robot.can_fetch(UA,url): raise ValueError('robots.txt disallows this URL')
    return get(url)

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.meta={};self.title='';self.in_title=False;self.ld=[];self.in_ld=False;self.current='';self.text=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='meta': self.meta[a.get('property',a.get('name',''))]=a.get('content','')
        if tag=='title': self.in_title=True
        if tag=='script' and a.get('type')=='application/ld+json': self.in_ld=True;self.current=''
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
        if tag=='script' and self.in_ld:self.ld.append(self.current);self.in_ld=False
    def handle_data(self,text):
        if self.in_title:self.title+=text
        if self.in_ld:self.current+=text
        self.text.append(text)

def record(title,url,observed,published=None,bedrooms=None,price=None,currency=None,images=None):
    url=canonical(url)
    if not isinstance(title,str) or not title.strip(): raise ValueError('Source entry needs a title')
    if bedrooms is not None and (isinstance(bedrooms,bool) or not isinstance(bedrooms,int) or bedrooms<0): bedrooms=None
    if price is not None:
        from decimal import Decimal, InvalidOperation
        try:
            v=Decimal(str(price))
            if not v.is_finite() or v<0: raise ValueError('Bad price')
            price=str(v)
        except (ValueError,InvalidOperation): price=None
    return {'id':'p-'+hashlib.sha256(url.encode()).hexdigest()[:16], 'title':title[:250], 'url':url,'state':'visual_pending','bedrooms':bedrooms,'price':price,'currency':currency,'images':images or [],'published_at':published,'evidence':[{'kind':'listing','source':url,'observed_at':observed,'published_at':published}]}

def parse_source(kind, text, url, observed):
    if kind=='json':
        obj=json.loads(text); rows=obj.get('listings',[]) if isinstance(obj,dict) else obj
        if not isinstance(rows,list):raise ValueError('JSON source expects listings[]')
        return [record(r['title'],r['url'],observed,r.get('published_at'),r.get('bedrooms'),r.get('price'),r.get('currency'),r.get('images')) for r in rows[:50]]
    if kind=='rss':
        if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper(): raise ValueError('XML entities blocked')
        root=ET.fromstring(text)
        if root.tag!='rss': raise ValueError('Expected RSS 2.0; Atom not implemented')
        return [record(x.findtext('title'),x.findtext('link'),observed,x.findtext('pubDate')) for x in root.findall('./channel/item')[:50]]
    if kind=='page':
        p=Page();p.feed(text);title=p.meta.get('og:title') or p.title
        images=[]
        if p.meta.get('og:image'):
            try: images=[canonical(urljoin(url,p.meta['og:image']))]
            except ValueError:pass
        beds=None;price=None;currency=None;published=None
        for raw in p.ld:
            try: obj=json.loads(raw)
            except ValueError:continue
            nodes=obj if isinstance(obj,list) else [obj]
            for node in nodes:
                if not isinstance(node,dict):continue
                for n in node.get('@graph',[node]):
                    if not isinstance(n,dict):continue
                    if n.get('@type') not in {'House','Apartment','SingleFamilyResidence','Residence','RealEstateListing','Product'}:continue
                    beds=n.get('numberOfBedrooms',beds);published=n.get('datePosted',published)
                    offer=n.get('offers',{})
                    if isinstance(offer,dict):price=offer.get('price',price);currency=offer.get('priceCurrency',currency)
        if beds is None:
            match=re.search(r'Dormitorios:\s*(\d+)\s+Dormitorios',p.meta.get('keywords',''),re.I)
            if match:beds=int(match.group(1))
        return [record(title,url,observed,published,beds,price,currency,images)]
    raise ValueError('Unknown adapter; use page, rss or json')

def merge(data, rows, source_id):
    index={p['url']:p for p in data['properties'] if p.get('url')}; changes=[]
    for row in rows:
        row['source_id']=source_id
        if row['url'] in index:
            old=index[row['url']]
            if 'bedrooms_override' in old:row['bedrooms']=old['bedrooms_override']
            changed=[k for k in ('title','price','currency','bedrooms') if row.get(k)!=old.get(k)]
            # Never turn a discarded or closed lead back into a candidate.
            for key in ('title','price','currency','bedrooms','images','published_at'):old[key]=row.get(key)
            old['evidence']=(old.get('evidence',[])+row['evidence'])[-20:]
            old['changed_fields']=changed
            if changed:changes.append({'id':old['id'],'changed_fields':changed})
        else:data['properties'].append(row);index[row['url']]=row;changes.append({'id':row['id'],'new':True})
    return changes
