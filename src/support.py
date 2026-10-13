"""Minimal specialist handoffs; no remote calls and no legal/solvency verdicts."""
from decimal import Decimal, InvalidOperation

TAX_REPO='https://github.com/MatiasJRB/monotributo-copilot-ar'
FIELDS={
 'legal':{'jurisdiction','contract_date','clauses','questions','proposed_actions','deadlines'},
 'financial':{'currency','costs','liquidity','commitments','protected_reserves','income','scenarios','questions','coverage'},
 'tax':{'jurisdiction','documents','requirements','questions','missing_documents'},
}
SKILLS={'legal':'skills/apoyo-legal-mudanza/SKILL.md','financial':'skills/apoyo-financiero-mudanza/SKILL.md'}
AXES={'new_home','current_home','moving'}

def amount(value):
 try: result=Decimal(str(value))
 except InvalidOperation:raise ValueError('Amount must be a decimal')
 if not result.is_finite() or result<0:raise ValueError('Amount must be finite and nonnegative')
 return result

def financial_numbers(context):
 """Arithmetic on declared entries only; not independent source verification."""
 currency=context.get('currency')
 if not isinstance(currency,str) or not currency:raise ValueError('Financial context needs a currency')
 totals={axis:{method:Decimal(0) for method in ('cash','card','unknown_method')} for axis in sorted(AXES)}
 monthly=Decimal(0); uncertain=[];seen=set()
 costs=context.get('costs',[])
 if not isinstance(costs,list):raise ValueError('Costs must be a list')
 for row in costs:
  if not isinstance(row,dict) or not row.get('id'):raise ValueError('Each cost needs an id')
  if row['id'] in seen:raise ValueError('Cost ids must be unique')
  seen.add(row['id'])
  if row.get('currency')!=currency:raise ValueError('Do not mix currencies')
  if row.get('axis') not in AXES:raise ValueError('Cost axis must be new_home, current_home or moving')
  method=row.get('method','unknown_method')
  if method not in {'cash','card','unknown_method'}:raise ValueError('Unknown payment method')
  timing=row.get('timing','entry')
  if timing not in {'entry','monthly'}:raise ValueError('Cost timing must be entry or monthly')
  v=amount(row['amount']) if row.get('amount') is not None else None
  if v is None or row.get('certainty')!='confirmed' or not row.get('source_id'):
   uncertain.append(row['id']);continue
  if timing=='monthly':monthly+=v
  else:totals[row['axis']][method]+=v
 return {'currency':currency,'entry_by_axis':{a:{k:str(v) for k,v in t.items()} for a,t in totals.items()},
         'entry_by_method':{m:str(sum(t[m] for t in totals.values())) for m in ('cash','card','unknown_method')},
         'known_monthly_total':str(monthly),'uncertain_cost_ids':uncertain,
         'basis':'only_costs_declared_confirmed_with_source_id','source_verification':'not_performed',
         'solvency_assessment':'not_assessed','financing_executed':False}

def prepare(role,packet):
 if role not in FIELDS:raise ValueError('Unknown support role')
 if not isinstance(packet,dict):raise ValueError('Support packet must be an object')
 request=packet.get('request')
 if not isinstance(request,str) or not request.strip():raise ValueError('A concrete request is required')
 context=packet.get('context',{})
 if not isinstance(context,dict):raise ValueError('Support context must be an object')
 sources=packet.get('sources',[])
 if not isinstance(sources,list) or any(not isinstance(s,dict) or not s.get('id') or not s.get('reference') or not s.get('observed_at') for s in sources):
  raise ValueError('Sources need id, reference and observed_at')
 if len({s['id'] for s in sources})!=len(sources):raise ValueError('Source ids must be unique')
 filtered={key:context[key] for key in sorted(FIELDS[role]) if key in context}
 # Source summaries may contain private data: no network transmission is performed.
 out={'role':role,'status':'request_prepared_not_reviewed','request':request,'context':filtered,
      'sources':[{key:s[key] for key in ('id','reference','observed_at','certainty') if key in s} for s in sources],
      'omitted_context_fields':sorted(set(context)-FIELDS[role]),
      'target':{'kind':'referenced_external_repo','url':TAX_REPO} if role=='tax' else {'kind':'included_skill','path':SKILLS[role]},
      'expected_response':['findings_with_evidence','assumptions','missing_information','options','suggested_next_steps','review_limits'],
      'external_transmission_performed':False,'human_approval_required_for_actions':True,
      'sensitive_data_notice':'Review all text before sharing; allowlisted fields can still contain sensitive data'}
 if role=='financial':
  numbers=financial_numbers(filtered)
  source_ids={s['id'] for s in sources}
  used={r.get('source_id') for r in filtered.get('costs',[]) if r.get('certainty')=='confirmed' and r.get('amount') is not None}
  if not used.issubset(source_ids):raise ValueError('Confirmed costs must reference a source in this packet')
  out['arithmetic']=numbers
 return out
