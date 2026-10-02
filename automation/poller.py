import json

from devices import BGP_COMMAND, OSPF_COMMAND, ROUTERS
from ssh_client import run_command


def poll_router(name: str, device: dict, password: str) -> dict:
    state = {name}
    try:
        if(device["ospf"]):
            ospfOutput = run_command(host=device["host"],username="root",password=password,command=OSPF_COMMAND)
            state[name]["ospf"] = json.loads(ospfOutput)

        if(device["bgp"]):
            bgpOutput = run_command(host=device["host"],username="root",password=password,command=BGP_COMMAND)
            state[name]["bgp"] = json.loads(bgpOutput)
    except Exception as e:
        state[name]["error"] = e
        raise RuntimeError(str(e))

    return state


def poll_all_routers(password: str) -> dict:
    results = {}

    for router,routerInfo in ROUTERS.items():
        state = poll_router(name=router,device=routerInfo,password=password)
        results.append(state)

    return results
