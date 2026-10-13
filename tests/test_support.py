import json
from pathlib import Path
import subprocess
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from support import prepare
ROOT=Path(__file__).resolve().parents[1]

class SupportTests(unittest.TestCase):
 def financial(self):return json.loads((ROOT/'examples/support-financial.json').read_text())
 def test_three_axes_and_uncertainty(self):
  r=prepare('financial',self.financial());a=r['arithmetic']
  self.assertEqual(a['entry_by_method']['cash'],'100000')
  self.assertEqual(a['entry_by_method']['card'],'30000')
  self.assertEqual(a['uncertain_cost_ids'],['flete'])
  self.assertEqual(a['solvency_assessment'],'not_assessed')
  self.assertFalse(r['external_transmission_performed'])
 def test_context_minimized_for_legal(self):
  r=prepare('legal',{'request':'Revisar','context':{'jurisdiction':'Ejemplo','liquidity':'sensitive-value'},'sources':[]})
  self.assertNotIn('sensitive-value',json.dumps(r));self.assertEqual(r['omitted_context_fields'],['liquidity'])
 def test_external_tax_reference_only(self):
  r=prepare('tax',json.loads((ROOT/'examples/support-tax.json').read_text()))
  self.assertEqual(r['target']['kind'],'referenced_external_repo');self.assertFalse(r['external_transmission_performed'])
 def test_missing_source(self):
  data=self.financial();data['sources']=[]
  with self.assertRaises(ValueError):prepare('financial',data)
 def test_no_currency_mix(self):
  data=self.financial();data['context']['costs'][0]['currency']='USD'
  with self.assertRaises(ValueError):prepare('financial',data)
 def test_estimates_not_confirmed(self):
  data=self.financial();data['context']['costs'][0]['certainty']='estimated'
  r=prepare('financial',data)['arithmetic']
  self.assertEqual(r['entry_by_method']['cash'],'0');self.assertIn('ingreso',r['uncertain_cost_ids'])
 def test_monthly_not_double_counted_entry(self):
  data=self.financial();data['context']['costs'][0]['timing']='monthly'
  r=prepare('financial',data)['arithmetic'];self.assertEqual(r['entry_by_method']['cash'],'0');self.assertEqual(r['known_monthly_total'],'100000')
 def test_duplicates_rejected(self):
  data=self.financial();data['context']['costs'].append(data['context']['costs'][0])
  with self.assertRaises(ValueError):prepare('financial',data)
 def test_all_bundled_skills_exist(self):
  for role in ['legal','financial']:
   r=prepare(role,json.loads((ROOT/f'examples/support-{role}.json').read_text()))
   self.assertTrue((ROOT/r['target']['path']).is_file())
 def test_cli_packets(self):
  for role in ['legal','financial','tax']:
   r=subprocess.run(['python3',str(ROOT/'bin/mudanza'),'support','--role',role,'--input',str(ROOT/f'examples/support-{role}.json')],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr)
   self.assertEqual(json.loads(r.stdout)['status'],'request_prepared_not_reviewed')
