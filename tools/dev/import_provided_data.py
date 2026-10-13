"""Import user-supplied scenarios into an explicitly local runtime directory."""
import argparse
import json
from pathlib import Path
from medipencil.provided_data import import_bundle

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--personas', type=Path, required=True)
    parser.add_argument('--data-root', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(import_bundle(args.archive,args.personas,args.data_root)))
