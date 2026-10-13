"""Run the exact first-user workflow, then expose ONLY its synthetic dashboard."""
import json
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='relocation-synthetic-') as temp:
    w=str(Path(temp)/'workspace')
    def cli(*args):
        result=subprocess.run(['python3',str(ROOT/'bin/mudanza'),*args],capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stderr)
        return json.loads(result.stdout)
    cli('init','--workspace',w,'--city','Ciudad de ejemplo','--bedrooms','2')
    cli('source-add','--workspace',w,'--id','catalogo','--adapter','json','--url','https://example.invalid/feed')
    cli('collect','--workspace',w,'--source','catalogo','--snapshot',str(ROOT/'examples/sources/listings.json'))
    data=cli('export','--workspace',w)
    cli('decide','--workspace',w,'--property',data['properties'][0]['id'],'--state','interested')
    cli('decide','--workspace',w,'--property',data['properties'][1]['id'],'--state','discarded')
    cli('conversation-add','--workspace',w,'--id','agencia','--contact','Agencia de ejemplo','--url','https://example.invalid/chat','--draft','Hola! ¿Las fotos son actuales de esa unidad?')
    cli('conversation-add','--workspace',w,'--id','flete','--contact','Flete de ejemplo','--url','https://example.invalid/flete')
    cli('message-log','--workspace',w,'--conversation','flete','--direction','outgoing','--text','Hola! ¿Me pasás un presupuesto?','--at','2026-01-01T12:00:00Z','--receipt','recibo-ficticio-001')
    result=cli('agent','--workspace',w,'--at','2026-01-07T12:00:00Z','--report')
    markup=Path(result['report_path']).read_text()
    markup=markup.replace('<h1>Para mover hoy</h1>','<h1>Primera búsqueda, desde cero</h1><p><strong>Recorrido ejecutado con datos ficticios.</strong> Instancia nueva, importación de fuente, decisión visual y conversaciones guardadas. Sin envíos. Esta copia no contiene una instancia real.</p>')
    destination=ROOT/'docs/demo/first-run.html';destination.write_text(markup)
    print('PASS: init → register → collect → decide → conversations → receipt → agent → dashboard')
    print('Output: docs/demo/first-run.html (synthetic only)')
