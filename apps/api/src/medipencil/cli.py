import argparse,json
from .config import Settings
from .db import Store
from .seed import seed

def main():
    parser=argparse.ArgumentParser(description='Local synthetic demo only')
    parser.add_argument('command',choices=['check-environment','migrate','seed-demo'])
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--confirm')
    args=parser.parse_args();settings=Settings.env();store=Store(settings.root)
    if args.command=='check-environment':
        print(json.dumps({'mode':'local_demo','data_root_outside_repo':True,'external_ai':False,'stt':'not_configured','llm':'not_configured'}));return
    store.migrate()
    if args.command=='migrate':print('migration=001');return
    if not args.dry_run and args.confirm!='TEAM_SYNTHETIC':parser.error('Use --dry-run or --confirm TEAM_SYNTHETIC')
    print(json.dumps(seed(store,dry_run=args.dry_run)))
if __name__=='__main__':main()
