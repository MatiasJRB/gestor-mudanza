"""Generate the public, synthetic demo from real core outputs; no network."""
import html
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from core import validate, property_status, conversation_status, cost_summary

data = validate(json.loads((ROOT / 'examples/demo.json').read_text()))
if data.get('fictional') is not True:
    raise ValueError('Public demo requires the synthetic fixture')
status = {'properties': [property_status(p) for p in data['properties']],
          'conversations': [conversation_status(c) for c in data['conversations']]}
costs = cost_summary(data['costs'], 'ARS')
outputs = json.dumps({'status': status, 'costs': costs}, ensure_ascii=False, indent=2)
markup = '''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>Gestor de mudanza · demo ficticia</title>
<style>:root{color-scheme:dark;background:#101c20;color:#eff5f2;font-family:system-ui,sans-serif}*{box-sizing:border-box}body{margin:0}main{max-width:1050px;margin:auto;padding:50px 28px}nav{display:flex;gap:24px;flex-wrap:wrap;margin-bottom:55px}a{color:#91dfc7;text-underline-offset:5px}h1{font-family:Georgia,serif;font-weight:400;font-size:clamp(42px,7vw,82px);line-height:1.05;max-width:820px;margin:0 0 28px}p{line-height:1.65;max-width:720px;color:#b9ccc7}h2{font-size:28px;font-weight:500;margin-top:44px}strong{color:#eff5f2}.notice{padding:14px 0;border-block:1px solid #3c5655;margin-block:30px}table{border-collapse:collapse;width:100%;font-size:16px}th,td{text-align:left;padding:18px 0;border-bottom:1px solid #3c5655;vertical-align:top}th{color:#b9ccc7;font-weight:400}td:first-child{width:36%;padding-right:18px}pre{background:#081317;padding:22px;overflow:auto;border:1px solid #3c5655;line-height:1.6;border-radius:12px;font-size:14px}summary{cursor:pointer;padding:20px 0;color:#91dfc7}footer{margin-top:48px;color:#b9ccc7;border-top:1px solid #3c5655;padding-top:20px}:focus-visible{outline:2px solid #91dfc7;outline-offset:5px}@media(max-width:550px){main{padding:30px 20px}nav{margin-bottom:38px}td,th{font-size:14px;padding:15px 0}td:first-child{width:40%}pre{padding:14px}}</style>
<main><nav aria-label="Secciones"><a href="#demo">La muestra</a><a href="#uso">Cómo probar</a><a href="#limites">Qué falta</a></nav>
<h1>Retomá la mudanza.<br>Sin reconstruir todo.</h1><p>Tu agente prepara el próximo paso con viviendas, conversaciones y cuentas que podés revisar. <strong>Vos decidís qué te gusta y qué se envía.</strong></p>
<p class="notice"><strong>Demo ficticia · núcleo experimental.</strong> Todos los datos son inventados. Esta página es una salida estática del código Python, no un agente ni un servicio conectado.</p>
<h2 id="demo">Esto devuelve el núcleo</h2><table><thead><tr><th scope="col">En la muestra</th><th scope="col">Qué sabemos / próximo paso</th></tr></thead><tbody><tr><td>Casa de ejemplo<br><small>2 dormitorios</small></td><td>Disponibilidad sin confirmar. El aviso es una pista.<br>Te toca revisar las fotos antes de avanzar.</td></tr><tr><td>Departamento de ejemplo</td><td>Descartado. No vuelve al pool activo.</td></tr><tr><td>Conversación de ejemplo</td><td>Borrador, no enviado: «Hola! ¿Las fotos son actuales de esa unidad?»<br>No hay recibo de envío.</td></tr><tr><td>Costos de ejemplo</td><td>ARS @CASH@ efectivo · ARS @CARD@ tarjeta.<br>Traslado sin importe. La suma está incompleta; solvencia no evaluada.</td></tr></tbody></table>
<details><summary>Ver JSON generado por el núcleo</summary><pre>@JSON@</pre></details>
<h2 id="uso">Sin cuentas, sin instalar paquetes</h2><p>Desde el checkout, con Python 3.9 o posterior:</p><pre>python3 bin/mudanza status --input examples/demo.json
python3 bin/mudanza costs --input examples/demo.json --currency ARS</pre><p>Pedile a tu agente: «Mostrame qué nos toca responder y qué plata falta confirmar. Prepará los mensajes juntos, pero no envíes nada». Dale acceso sólo a tu instancia privada y a los conectores que autorices.</p>
<h2 id="limites">Una base pequeña y explícita</h2><p>Hoy hay CLI de sólo lectura, estados con evidencia y sumas decimales. No hay agente embebido, scrapers, conectores, recordatorios automáticos, envíos, cuotas ni cálculo legal. Las fechas de revisión son datos, no una alarma.</p><p>Guardá tu instancia real fuera del checkout. Un aviso no prueba disponibilidad y una suma no prueba que puedas pagar. Las acciones externas requieren tu aprobación y verificación posterior.</p><footer>Python · sin dependencias · MIT · preparado localmente, no publicado.</footer></main></html>'''
markup = markup.replace('@JSON@', html.escape(outputs)).replace('@CASH@', costs['known_totals']['cash']).replace('@CARD@', costs['known_totals']['card'])
(ROOT / 'docs/demo/index.html').write_text(markup, encoding='utf-8')
print('Generated docs/demo/index.html from examples/demo.json and src/core.py')
