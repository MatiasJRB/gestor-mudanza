"""Private static actionable dashboard; escapes all untrusted source text."""
import html
import json
from urllib.parse import urlsplit
from pathlib import Path

LABELS={'nos_toca_responder':'Nos toca responder','borrador_no_enviado':'Borrador no enviado','corresponde_retomar':'Corresponde retomar','interested':'Te interesa','visual_pending':'Pendiente de tu filtro visual','publication_date_recorded_not_verified':'Fecha de publicación declarada, sin verificar','publication_date_unknown':'Fecha de publicación desconocida'}
def label(x):return LABELS.get(x,x)

def esc(x):return html.escape(str(x if x is not None else 'Sin dato'))
def link(url,label):
    if not url or urlsplit(url).scheme not in {'http','https'}:return '<span>Sin acceso registrado</span>'
    return '<a target="_blank" rel="noopener noreferrer" href="'+esc(url)+'">'+esc(label)+'</a>'

def render(result,path):
    actions=''
    for a in result['for_today']+result['other_pending']:
        actions+='<article><h3>'+esc(a['contact'])+'</h3><p>'+esc(label(a['state']))+' · '+esc(a['reason'])+'</p><p>'+esc(a['next_step'])+'</p>'
        if a.get('draft'):actions+='<blockquote>'+esc(a['draft'])+'</blockquote>'
        actions+=link(a.get('conversation_url'),'Abrir conversación')+'<p>Preparado, no enviado. Requiere aprobación.</p></article>'
    props=''
    for p in result['candidates']:
        props+='<article><h3>'+esc(p['title'])+'</h3><p>'+esc(p['bedrooms'])+' dormitorios · '+esc(label(p['state']))+'</p><p>'+esc(p['price'])+' '+esc(p['currency'])+' · costo mensual incompleto</p><p>Disponibilidad sin confirmar · '+esc(label(p['freshness']))+'</p>'+link(p.get('url'),'Ver publicación')+'</article>'
    errors=''.join('<li>'+esc(s['id'])+': '+esc(s.get('error') or (('Importación de snapshot · ' if s.get('check_mode')=='snapshot' else 'Consulta HTTP · ')+str(s.get('last_checked'))))+'</li>' for s in result['sources'])
    text='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>Mi mudanza · para mover hoy</title><style>:root{color-scheme:dark;background:#101c20;color:#eff5f2;font-family:system-ui}*{box-sizing:border-box}body{max-width:960px;margin:auto;padding:32px 22px}h1{font-family:Georgia,serif;font-size:clamp(36px,7vw,60px);font-weight:400}p,li{line-height:1.6;color:#b9ccc7}a{color:#91dfc7;overflow-wrap:anywhere}article{border-top:1px solid #3c5655;padding:20px 0}blockquote{margin:16px 0;padding:16px;background:#081317;white-space:pre-wrap}pre{overflow:auto;padding:16px;background:#081317}h2{margin-top:40px}:focus-visible{outline:2px solid #91dfc7}</style><h1>Para mover hoy</h1><p>Agente local por reglas. No se envió ningún mensaje ni se asumió un compromiso.</p>'''
    text+=actions or '<p>No hay conversaciones que requieran movimiento según lo registrado. La cobertura depende de tus importaciones.</p>'
    text+='<h2>Viviendas por revisar</h2>'+props+'<h2>Cobertura de fuentes</h2><ul>'+errors+'</ul><details><summary>Resultado técnico</summary><pre>'+esc(json.dumps(result,ensure_ascii=False,indent=2))+'</pre></details></html>'
    path=Path(path);path.write_text(text,encoding='utf-8');path.chmod(0o600);return str(path)
