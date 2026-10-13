import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from sources import parse_source, merge, canonical, public_url, fetch
from workspace import Workspace
from agent import plan, instant, business_hours
from report import render
ROOT=Path(__file__).resolve().parents[1]
AT='2026-01-07T12:00:00Z'

class SourceTests(unittest.TestCase):
 def test_json_and_dedup_discard(self):
  rows=parse_source('json',(ROOT/'examples/sources/listings.json').read_text(),'https://example.invalid/feed',AT)
  d={'properties':[]};merge(d,rows,'feed');d['properties'][0]['state']='discarded';merge(d,rows,'feed')
  self.assertEqual(len(d['properties']),2);self.assertEqual(d['properties'][0]['state'],'discarded')
 def test_page_metadata(self):
  p=parse_source('page','<title>A</title><meta name="keywords" content="Dormitorios: 2 Dormitorios"><script type="application/ld+json">{"@type":"House","offers":{"price":120,"priceCurrency":"ARS"}}</script>','https://example.invalid/a',AT)[0]
  self.assertEqual(p['bedrooms'],2);self.assertEqual(p['price'],'120');self.assertEqual(p['evidence'][0]['kind'],'listing')
 def test_rss(self):
  text='<rss><channel><item><title>Casa</title><link>https://example.invalid/c</link><pubDate>Mon, 5 Jan 2026 12:00:00 GMT</pubDate></item></channel></rss>'
  self.assertEqual(len(parse_source('rss',text,'https://example.invalid/rss',AT)),1)
 def test_entities(self):
  with self.assertRaises(ValueError):parse_source('rss','<!DOCTYPE a><rss/>','https://example.invalid/rss',AT)
 def test_tracking_and_credentials(self):
  self.assertEqual(canonical('https://example.invalid/a?utm_source=x#hi'),'https://example.invalid/a')
  with self.assertRaises(ValueError):canonical('https://user:pass@example.invalid/a')
 def test_private_network(self):
  addresses=[(2,1,6,'',('127.0.0.1',80))]
  with patch('sources.socket.getaddrinfo',return_value=addresses):
   with self.assertRaises(ValueError):public_url('https://example.invalid/a')
 def test_robots_denial(self):
  with patch('sources.public_url',side_effect=lambda x:x),patch('sources.get',return_value='User-agent: *\nDisallow: /') as get:
   with self.assertRaises(ValueError):fetch('https://example.invalid/a')
   self.assertEqual(get.call_count,1)

class AgentTests(unittest.TestCase):
 def data(self):return {'preferences':{'timezone':'UTC','holidays':['2026-01-05'],'followup_hours':48,'minimum_bedrooms':2},'conversations':[],'properties':[],'sources':[]}
 def test_business_days_and_holiday(self):
  self.assertEqual(business_hours(instant('2026-01-02T12:00:00Z'),instant('2026-01-06T12:00:00Z'),self.data()['preferences']),24)
 def test_receipt_and_wait(self):
  d=self.data();d['conversations']=[{'id':'c','last_outgoing':{'at':'2026-01-01T12:00:00Z','receipt_id':'manual-r'}}]
  self.assertEqual(plan(d,AT)['for_today'][0]['state'],'corresponde_retomar')
  d['conversations'][0]['wait_until']='2026-01-10T12:00:00Z'
  self.assertEqual(plan(d,AT)['for_today'],[])
 def test_draft_no_receipt(self):
  d=self.data();d['conversations']=[{'id':'c','draft':'Hola','last_outgoing':{'at':'2026-01-01T12:00:00Z'}}]
  self.assertEqual(plan(d,AT)['for_today'][0]['state'],'borrador_no_enviado')
 def test_stop_repeated_followups(self):
  d=self.data();d['conversations']=[{'id':'c','followups':2,'last_outgoing':{'at':'2026-01-01T12:00:00Z','receipt_id':'r'}}]
  self.assertIsNone(plan(d,AT)['for_today'][0]['draft'])
 def test_closed_and_offsets(self):
  d=self.data();d['conversations']=[{'id':'c','closed_reason':'respondido','draft':'hola'}]
  self.assertEqual(plan(d,AT)['for_today'],[])
  self.assertEqual(instant('2026-01-01T09:00:00-03:00'),instant('2026-01-01T12:00:00Z'))
 def test_report_escapes(self):
  d=self.data();d['conversations']=[{'id':'c','contact':'<script>alert(1)</script>','draft':'<img src=x>'}]
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'board.html';render(plan(d,AT),path)
   self.assertNotIn('<script>',path.read_text());self.assertIn('&lt;script&gt;',path.read_text())

class FreshUserTests(unittest.TestCase):
 def cli(self,*args,ok=True):
  r=subprocess.run(['python3',str(ROOT/'bin/mudanza'),*args],text=True,capture_output=True)
  self.assertEqual(r.returncode,0 if ok else 1,r.stderr)
  return json.loads(r.stdout if ok else r.stderr)
 def test_full_flow_from_zero(self):
  with tempfile.TemporaryDirectory() as tmp:
   w=str(Path(tmp)/'new-user')
   self.cli('init','--workspace',w,'--city','Ciudad de ejemplo')
   self.cli('source-add','--workspace',w,'--id','f','--adapter','json','--url','https://example.invalid/feed')
   self.cli('collect','--workspace',w,'--source','f','--snapshot',str(ROOT/'examples/sources/listings.json'))
   d=self.cli('export','--workspace',w);identifier=d['properties'][0]['id']
   self.cli('decide','--workspace',w,'--property',identifier,'--state','discarded')
   self.cli('collect','--workspace',w,'--source','f','--snapshot',str(ROOT/'examples/sources/listings.json'))
   self.cli('decide','--workspace',w,'--property',identifier,'--state','interested',ok=False)
   self.cli('conversation-add','--workspace',w,'--id','agencia','--contact','Agencia de ejemplo','--url','https://example.invalid/chat','--draft','Hola! ¿Sigue en alquiler?')
   result=self.cli('agent','--workspace',w,'--at',AT,'--report')
   self.assertEqual(result['for_today'][0]['state'],'borrador_no_enviado');self.assertTrue(Path(result['report_path']).is_file())
   self.cli('message-log','--workspace',w,'--conversation','agencia','--direction','outgoing','--text','Hola','--at',AT,ok=False)
   self.cli('message-log','--workspace',w,'--conversation','agencia','--direction','outgoing','--text','Hola','--at',AT,'--receipt','manual-export-r1')
   self.cli('message-log','--workspace',w,'--conversation','agencia','--direction','incoming','--text','Te paso fotos mañana','--at','2026-01-07T13:00:00Z')
   self.cli('wait','--workspace',w,'--conversation','agencia','--until','2026-01-09T12:00:00Z')
   self.assertEqual(self.cli('agent','--workspace',w,'--at','2026-01-08T12:00:00Z')['for_today'],[])
   self.cli('conversation-close','--workspace',w,'--conversation','agencia','--reason','No interesa')
   self.assertEqual(self.cli('agent','--workspace',w,'--at','2026-01-12T12:00:00Z')['for_today'],[])
   self.cli('init','--workspace',w,'--city','Otra',ok=False)
 def test_reject_repository_workspace(self):
  with self.assertRaises(ValueError):Workspace(ROOT/'private',create=True)
 def test_transaction_rollback(self):
  with tempfile.TemporaryDirectory() as tmp:
   w=Workspace(tmp,create=True,city='Ejemplo')
   def bad(d):d['properties'].append({'id':'bad'});raise ValueError('fail')
   with self.assertRaises(ValueError):w.change('test',bad)
   self.assertEqual(w.read()['properties'],[]);w.close()

class RegressionTests(unittest.TestCase):
 def test_manual_bedrooms_survive_refresh(self):
  row=parse_source('json',(ROOT/'examples/sources/listings.json').read_text(),'https://example.invalid/feed',AT)[0]
  old=dict(row);old['bedrooms']=3;old['bedrooms_override']=3
  d={'properties':[old]};merge(d,[row],'f');self.assertEqual(old['bedrooms'],3)
 def test_known_nonfit_not_shown(self):
  d={'preferences':{'minimum_bedrooms':2},'sources':[],'conversations':[],'properties':[{'id':'p','state':'visual_pending','bedrooms':1}]}
  self.assertEqual(plan(d,AT)['candidates'],[])
 def test_snapshot_label(self):
  d={'preferences':{},'conversations':[],'properties':[],'sources':[{'id':'f','adapter':'json','check_mode':'snapshot','last_checked':AT}]}
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'board.html';render(plan(d,AT),path)
   self.assertIn('Importación de snapshot',path.read_text());self.assertNotIn('Consulta HTTP',path.read_text())

class PersistenceRegressions(unittest.TestCase):
 def test_latest_incoming_invalidates_old_draft(self):
  helper=FreshUserTests()
  with tempfile.TemporaryDirectory() as tmp:
   w=str(Path(tmp)/'w');helper.cli('init','--workspace',w,'--city','Ejemplo')
   helper.cli('conversation-add','--workspace',w,'--id','c','--contact','Ejemplo','--url','https://example.invalid/chat','--draft','Borrador anterior')
   helper.cli('message-log','--workspace',w,'--conversation','c','--direction','incoming','--at',AT,'--text','Datos nuevos')
   d=helper.cli('export','--workspace',w);self.assertIsNone(d['conversations'][0]['draft'])
 def test_invalid_timezone_does_not_create_workspace(self):
  helper=FreshUserTests()
  with tempfile.TemporaryDirectory() as tmp:
   w=str(Path(tmp)/'w');helper.cli('init','--workspace',w,'--city','Ejemplo','--timezone','Invalid/Zone',ok=False)
   self.assertFalse(Path(w).exists())
 def test_existing_nonempty_directory_untouched(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'keep';path.write_text('original')
   with self.assertRaises(ValueError):Workspace(tmp,create=True)
   self.assertEqual(path.read_text(),'original');self.assertFalse((Path(tmp)/'state.db').exists())
