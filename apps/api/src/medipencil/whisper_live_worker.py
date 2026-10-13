"""Persistent, offline Whisper preview worker; PCM input and output stay in memory."""
import base64,hashlib,json,socket,sys
from pathlib import Path

def denied(*args,**kwargs):raise RuntimeError('Worker network disabled')
socket.socket.connect=denied
socket.create_connection=denied
import numpy as np
import torch,whisper
path=Path(sys.argv[1]);torch.set_num_threads(4)
with path.open('rb') as file:digest=hashlib.file_digest(file,'sha256').hexdigest()
model=whisper.load_model(str(path),device='cpu')
for line in sys.stdin:
    request=json.loads(line)
    audio=np.frombuffer(base64.b64decode(request['pcm']),dtype='<i2').astype(np.float32)/32768.0
    result=model.transcribe(audio,language=request['language'],fp16=False,verbose=None,condition_on_previous_text=False,temperature=0)
    print(json.dumps({'text':result['text'].strip(),'metadata':{'provider_id':'whisper','model':path.name,'model_sha256':digest,'runtime_version':whisper.__version__,'execution_mode':'LIVE','ai_executed':True,'task':'streaming_preview','final':False}},ensure_ascii=False),flush=True)
    del request,audio,result,line
