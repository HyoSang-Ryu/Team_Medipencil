"""Independent, reproducible synthetic observations; no hospital connection."""
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from .common import Fault

def records(subject,end,days):
    if subject!='aino':raise Fault('PROVIDER_NOT_CONFIGURED',503)
    result=[]
    for offset in range(days-1,-1,-1):
        day=end-timedelta(days=offset);n=day.toordinal()
        at=day.isoformat()+'T08:00:00';occurred=datetime.fromisoformat(at).replace(tzinfo=ZoneInfo('Europe/Helsinki')).isoformat()
        texts=[('meals',f'Aino söi aamupalasta {[50,75,100][n%3]} prosenttia.','observation'),('movement',f'Aino käveli hoitajan kanssa {[5,10,15][n%3]} minuuttia.','observation'),('sleep',f'Yövuoron kirjauksen mukaan Aino heräsi yön aikana {[2,1,0][n%3]} kertaa.','observation'),('outdoors','Iltapäivälle on suunniteltu ulkoilu. Toteutumista ei ole vahvistettu.','plan')]
        for topic,text,kind in texts:result.append({'key':f'{day}-{topic}','text':text,'topic':topic,'type':kind,'speaker':'carer','occurred_at':occurred,'required_scopes':[topic]})
    return result
