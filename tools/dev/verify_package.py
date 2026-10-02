"""Install a built wheel in a clean venv, run CLI and real TCP restart checks."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,socket,urllib.request
from pathlib import Path

parser=argparse.ArgumentParser();parser.add_argument('--uv',required=True);parser.add_argument('--wheel',required=True);args=parser.parse_args()
repo=Path(__file__).resolve().parents[2]
def run(command,env=None,success=True):
    result=subprocess.run(command,cwd=repo,env=env,text=True,capture_output=True)
    if (result.returncode==0)!=success:raise RuntimeError(result.stdout+result.stderr)
    return result.stdout.strip()
with tempfile.TemporaryDirectory(prefix='medipencil-package-') as directory:
    base=Path(directory).resolve();venv=base/'venv';root=base/'data'
    run([args.uv,'venv','--python',str(repo/'.venv/bin/python'),str(venv)])
    python=str(venv/'bin/python')
    run([args.uv,'pip','sync','--python',python,str(repo/'apps/api/requirements.lock.txt')])
    run([args.uv,'pip','install','--python',python,'--no-deps',args.wheel])
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    origin=f'http://127.0.0.1:{port}'
    env=os.environ|{'MEDIPENCIL_DATA_ROOT':str(root),'MEDIPENCIL_SESSION_SECRET':secrets.token_urlsafe(48),'MEDIPENCIL_ORIGIN':origin}
    cli=[python,'-m','medipencil.cli']
    for command in [['check-environment'],['migrate'],['seed-demo','--dry-run'],['seed-demo','--confirm','TEAM_SYNTHETIC']]:
        print('CLI',command[0],run(cli+command,env))
    run(cli+['seed-demo','--confirm','TEAM_SYNTHETIC'],env,success=False)
    for attempt in range(2):
        process=subprocess.Popen([python,'-m','uvicorn','medipencil.main:app','--host','127.0.0.1','--port',str(port),'--workers','1','--no-access-log'],cwd=repo,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            for _ in range(100):
                if process.poll() is not None:raise RuntimeError(process.stderr.read().decode())
                try:
                    response=urllib.request.urlopen(origin+'/api/v1/health',timeout=.2)
                    assert json.load(response)['data']['status']=='ok';break
                except (OSError,TimeoutError):time.sleep(.05)
            else:raise RuntimeError('Server failed to start')
            assert b'<div id="root">' in urllib.request.urlopen(origin).read()
            # Active run must be protected from cleanup.
            run(cli+['clean-run','--dry-run'],env,success=False)
        finally:
            process.terminate();process.wait(timeout=10)
        print('TCP_START_STOP',attempt+1,'PASS')
    planned=json.loads(run(cli+['clean-run','--dry-run'],env));assert planned['deleted_count']==0
    run(cli+['clean-run','--confirm',planned['run_id']],env)
    assert not (root/'demo.sqlite').exists()
    print('WHEEL_CLI_RESTART_CLEANUP=PASS')
