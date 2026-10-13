"""Bundled deterministic coordinator. A portable skill adds conversational reasoning."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

def instant(value):
    dt=datetime.fromisoformat(value.replace('Z','+00:00'))
    if dt.tzinfo is None: raise ValueError('Timestamps must include a timezone')
    return dt.astimezone(timezone.utc)

def business_hours(start, end, preferences):
    """24h per business date, excluding weekends and user-configured holidays."""
    zone=ZoneInfo(preferences.get('timezone','UTC'));start=start.astimezone(zone);end=end.astimezone(zone)
    total=0.0;holidays=set(preferences.get('holidays',[]))
    while start<end:
        next_day=(start+timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
        stop=min(end,next_day)
        if start.weekday()<5 and start.date().isoformat() not in holidays:total+=(stop-start).total_seconds()/3600
        start=stop
    return total

def plan(data, at):
    current=instant(at);prefs=data['preferences'];actions=[]
    for c in data['conversations']:
        if c.get('closed_reason'):continue
        if c.get('wait_until') and instant(c['wait_until'])>current:continue
        sent=c.get('last_outgoing');incoming=c.get('last_incoming')
        receipt=bool(sent and sent.get('receipt_id') and sent.get('at'))
        inbound=bool(incoming and (not receipt or instant(incoming['at'])>instant(sent['at'])))
        draft=c.get('draft')
        if inbound:
            state='nos_toca_responder';reason='Último entrante: '+incoming['at']
            next_step='Revisar el intercambio y preparar respuesta' if not draft else 'Revisar y aprobar el borrador'
            rank=0
        elif draft:
            state='borrador_no_enviado';reason='No hay recibo de envío para este borrador';next_step='Revisar y aprobar el texto';rank=1
        elif receipt and business_hours(instant(sent['at']),current,prefs)>=prefs.get('followup_hours',48):
            state='corresponde_retomar';reason='Sin respuesta desde '+sent['at'];rank=2
            if c.get('followups',0)>=2:
                next_step='Elegir cambio de canal o bajar prioridad; no insistir automáticamente';draft=None
            else:
                next_step='Revisar y aprobar seguimiento';draft='Hola! ¿Pudiste ver mi consulta? Gracias!'
        else:continue
        if c.get('review_at') and instant(c['review_at'])>current and not inbound:continue
        actions.append({'id':c['id'],'contact':c.get('contact',c['id']),'state':state,'reason':reason,'next_step':next_step,'draft':draft,'conversation_url':c.get('conversation_url'),'rank':rank,'requires_approval':True})
    actions.sort(key=lambda x:(x['rank'],x['id']))
    minimum=prefs.get('minimum_bedrooms',2)
    candidates=[{'id':p['id'],'title':p.get('title',p['id']),'url':p.get('url'),'bedrooms':p.get('bedrooms'),'state':p['state'],'availability':'unconfirmed','objective_fit':None if p.get('bedrooms') is None else p['bedrooms']>=minimum,'price':p.get('price'),'currency':p.get('currency'),'images':p.get('images',[]),'freshness':'publication_date_recorded_not_verified' if p.get('published_at') else 'publication_date_unknown'} for p in data['properties'] if p['state'] not in {'discarded','closed'} and (p.get('bedrooms') is None or p['bedrooms']>=minimum)]
    return {'generated_at':at,'mode':'local_rules_no_llm','for_today':actions[:3],'other_pending':actions[3:],'candidates':candidates,'sources':[{'id':s['id'],'adapter':s['adapter'],'last_checked':s.get('last_checked'),'check_mode':s.get('check_mode'),'error':s.get('error'),'last_changes':s.get('last_changes',[])} for s in data['sources']],'guardrails':['No messages, reservations, payments or calendar changes are executed','A listing never confirms availability','Human visual review before financial or visit analysis']}
