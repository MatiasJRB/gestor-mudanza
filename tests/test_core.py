import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from core import *
class CoreTests(unittest.TestCase):
    def test_listing_is_not_availability(self):
        p={'id':'a','state':'lead','bedrooms':2,'evidence':[{'kind':'listing'}]}
        self.assertEqual(property_status(p)['availability'],'unconfirmed')
    def test_closed_never_returns_to_pool(self):
        self.assertFalse(property_status({'id':'a','state':'discarded','bedrooms':3})['objective_fit'])
    def test_mismatched_unit_is_not_confirmed(self):
        p={'id':'a','state':'interested','bedrooms':2,'evidence':[{'kind':'direct_confirmation','available':True,'unit_id':'b','source':'x','observed_at':'x'}]}
        self.assertEqual(property_status(p)['availability'],'unconfirmed')
    def test_confirmation_is_not_permanent(self):
        p={'id':'a','state':'interested','bedrooms':2,'evidence':[{'kind':'direct_confirmation','available':True,'unit_id':'a','source':'x','observed_at':'x'}]}
        self.assertEqual(property_status(p)['availability'],'confirmation_recorded_revalidate')
    def test_draft_is_not_sent(self):
        self.assertEqual(conversation_status({'id':'c','draft':'hi','last_outgoing':{'at':'2026-01-01'}})['state'],'draft_not_sent')
    def test_wait_requires_receipt(self):
        self.assertEqual(conversation_status({'id':'c','last_outgoing':{'at':'2026-01-01','receipt_id':'r'}})['state'],'waiting_external')
    def test_unknown_not_zero(self):
        r=cost_summary([{'id':'x','currency':'ARS','amount':None}],'ARS')
        self.assertFalse(r['complete']);self.assertEqual(r['missing_amounts'],['x'])
    def test_no_currency_mix(self):
        with self.assertRaises(ValueError):cost_summary([{'id':'x','currency':'USD','amount':1}],'ARS')
    def test_cash_and_card_separate(self):
        r=cost_summary([{'id':'a','currency':'ARS','amount':'1.1','method':'cash'},{'id':'b','currency':'ARS','amount':'2.2','method':'card'}],'ARS')
        self.assertEqual(r['known_totals']['cash'],'1.1');self.assertEqual(r['known_totals']['card'],'2.2')
    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):validate({'schema_version':1,'properties':[{'id':'a','state':'lead'},{'id':'a','state':'lead'}]})
if __name__=='__main__': unittest.main()
