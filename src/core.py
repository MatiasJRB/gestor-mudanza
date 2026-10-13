"""Local, read-only tools for an external relocation agent. No network or actions."""
from decimal import Decimal, InvalidOperation

STATES = {'lead', 'visual_pending', 'interested', 'discarded', 'closed'}

def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Input must be a JSON object')
    for key in ('properties', 'conversations', 'costs'):
        records = data.get(key, [])
        if not isinstance(records, list) or any(not isinstance(x, dict) for x in records):
            raise ValueError(key + ' must be a list of objects')
        ids = [x.get('id') for x in records]
        if any(not isinstance(x, str) or not x.strip() for x in ids) or len(set(ids)) != len(ids):
            raise ValueError(key + ' ids must be unique nonempty strings')
    if data.get('schema_version') != 1:
        raise ValueError('schema_version must be 1')
    seen = set()
    for p in data.get('properties', []):
        if not p.get('id') or p['id'] in seen:
            raise ValueError('Property ids must be unique and nonempty')
        seen.add(p['id'])
        if p.get('state') not in STATES:
            raise ValueError('Unknown property state')
        beds = p.get('bedrooms')
        if beds is not None and (isinstance(beds, bool) or not isinstance(beds, int) or beds < 0):
            raise ValueError('Bedrooms must be a nonnegative integer or null')
        if not isinstance(p.get('evidence', []), list) or any(not isinstance(e, dict) for e in p.get('evidence', [])):
            raise ValueError('Evidence must be a list')
    return data

def property_status(p, minimum_bedrooms=2):
    closed = p['state'] in {'discarded', 'closed'}
    beds = p.get('bedrooms')
    confirmed = any(e.get('kind') == 'direct_confirmation' and e.get('available') is True
                    and e.get('unit_id') == p['id'] and e.get('observed_at') and e.get('source')
                    for e in p.get('evidence', []))
    return {'id': p['id'], 'state': p['state'],
            'objective_fit': not closed and beds is not None and beds >= minimum_bedrooms,
            'availability': 'closed' if closed else 'confirmation_recorded_revalidate' if confirmed else 'unconfirmed',
            'next_step': 'none' if closed else 'human_visual_review' if p['state'] in {'lead','visual_pending'} else 'validate_exact_unit_and_cost'}

def conversation_status(c):
    """Prepared messages are not receipts. Follow-up timing belongs to the runtime."""
    sent = c.get('last_outgoing')
    inbound = c.get('last_incoming')
    receipt = bool(sent and sent.get('receipt_id') and sent.get('at'))
    if c.get('closed_reason'):
        state = 'closed'
    elif inbound and inbound.get('at') and (not receipt or inbound['at'] > sent['at']):
        state = 'review_incoming'
    elif receipt:
        state = 'waiting_external'
    elif c.get('draft'):
        state = 'draft_not_sent'
    else:
        state = 'not_started'
    return {'id': c['id'], 'state': state, 'outgoing_confirmed': receipt,
            'conversation_url': c.get('conversation_url'), 'draft': c.get('draft'),
            'review_at': c.get('review_at')}

def cost_summary(items, currency):
    """Only known amounts in one currency; cash, card and unknown method stay separate."""
    totals = {k: Decimal(0) for k in ('cash','card','unknown_method')}
    missing = []
    for item in items:
        if item.get('currency') != currency:
            raise ValueError('Do not sum currencies without an explicit conversion model')
        if item.get('amount') is None:
            missing.append(item['id']); continue
        try:
            amount = Decimal(str(item['amount']))
        except InvalidOperation:
            raise ValueError('Amounts must be valid decimals')
        if not amount.is_finite() or amount < 0:
            raise ValueError('Amounts must be finite and nonnegative')
        method = item.get('method', 'unknown_method')
        if method not in totals:
            raise ValueError('Unknown payment method')
        totals[method] += amount
    return {'currency': currency, 'known_totals': {k: str(v) for k,v in totals.items()},
            'missing_amounts': missing, 'complete': not missing,
            'solvency_assessment': 'not_assessed'}
