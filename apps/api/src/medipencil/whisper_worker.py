"""Executed in the installed Whisper runtime. Reads local checkpoint; writes no artifacts."""
import hashlib,json,socket,sys
from pathlib import Path
# No network is needed: both checkpoint and audio are explicit local files.
def denied(*args,**kwargs):raise RuntimeError('Worker network disabled')
socket.socket.connect=denied
socket.create_connection=denied
import torch,whisper
model_path,audio_path,language=sys.argv[1:]
assert Path(model_path).is_file()
torch.set_num_threads(4)
with open(model_path,'rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
model=whisper.load_model(model_path,device='cpu')
result=model.transcribe(audio_path,language=language,fp16=False,verbose=None,condition_on_previous_text=False,temperature=0)
print(json.dumps({'text':result['text'],'model_sha256':digest,'runtime_version':whisper.__version__},ensure_ascii=False))
