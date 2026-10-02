import base64,json
from .common import Fault
from .security import digest

def page(request,items,scope):
    if set(request.query_params)-{'cursor','limit'}:raise Fault('VALIDATION_FAILED')
    try:
        limit=int(request.query_params.get('limit','50'))
        if not 1<=limit<=100:raise ValueError()
        offset=0;token=request.query_params.get('cursor')
        if token:
            encoded,signature=token.split('.')
            if digest(request.app.state.settings.secret,encoded)!=signature:raise ValueError()
            value=json.loads(base64.urlsafe_b64decode(encoded))
            if value['scope']!=scope:raise ValueError()
            offset=value['offset']
            if not isinstance(offset,int) or offset<0:raise ValueError()
    except (ValueError,KeyError,TypeError):raise Fault('VALIDATION_FAILED')
    end=offset+limit;next_cursor=None
    if end<len(items):
        encoded=base64.urlsafe_b64encode(json.dumps({'scope':scope,'offset':end}).encode()).decode()
        next_cursor=encoded+'.'+digest(request.app.state.settings.secret,encoded)
    return {'items':items[offset:end],'next_cursor':next_cursor}
