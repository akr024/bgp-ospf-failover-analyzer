import json
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path
from poller import poll_all_routers

def main():
    password = getpass("SSH Password: ")

    allRoutersInfo = poll_all_routers(password)

    time = datetime.now(timezone.utc)
    isoTime = time.isoformat()
    resTime = isoTime.replace(" ", "")

    snapshot = {"timestamp": resTime,"routers": allRoutersInfo}

    dir_path = Path('~/bgp-ospf-failover-analyzer/data/snapshots').expanduser()
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f'snapshot_{resTime}.json'

    with open(file=file_path,mode='w', encoding='utf-8') as file:
        json.dump(snapshot,file,indent=4)

    print(f"Successfully saved router snapshot to: {file_path}")

if __name__ == "__main__":
    main()
