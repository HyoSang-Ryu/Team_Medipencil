"""Deterministic synthetic observations; no clinical inference."""
from datetime import datetime
from .common import Fault
from .domain import timestamp

def intervals(events, window_start, window_end, coverage='complete'):
    start=timestamp(window_start);end=timestamp(window_end)
    if start>=end:raise Fault('VALIDATION_FAILED')
    seen=set();opened=None;pairs=[];incomplete=coverage!='complete'
    for event in sorted(events,key=lambda e:timestamp(e['at'])):
        at=timestamp(event['at']);kind=event['kind']
        if kind not in ('enter','leave') or not start<=at<=end:raise Fault('VALIDATION_FAILED')
        if (at,kind) in seen:continue
        seen.add((at,kind))
        if kind=='enter':
            if opened:incomplete=True
            opened=at
        elif opened:
            pairs.append([opened,at]);opened=None
        else:incomplete=True
    if opened:incomplete=True
    return {'window_start':start,'window_end':end,'coverage_state':'incomplete' if incomplete else 'complete','intervals':pairs,'seconds':sum((datetime.fromisoformat(b)-datetime.fromisoformat(a)).total_seconds() for a,b in pairs),'algorithm_version':'intervals-v1'}
