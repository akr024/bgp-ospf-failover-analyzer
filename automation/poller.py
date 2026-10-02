import json

from devices import BGP_COMMAND, OSPF_COMMAND, ROUTE_COMMAND, ROUTERS
from ssh_client import run_command


def poll_router(device: dict, password: str) -> dict:
    state = {"ospf":None,"bgp":None,"routes":None,"error":None}
    try:
        routeOutput = run_command(host=device["host"],username="root",password=password,command=ROUTE_COMMAND)
        state["routes"] = json.loads(routeOutput)
        if(device.get("ospf")):
            ospfOutput = run_command(host=device["host"],username="root",password=password,command=OSPF_COMMAND)
            state["ospf"] = json.loads(ospfOutput)

        if(device.get("bgp")):
            bgpOutput = run_command(host=device["host"],username="root",password=password,command=BGP_COMMAND)
            state["bgp"] = json.loads(bgpOutput)
    except Exception as e:
        state["error"] = str(e)

    return state


def poll_all_routers(password: str) -> dict:
    results = {}

    for router,routerInfo in ROUTERS.items():
        state = poll_router(device=routerInfo,password=password)
        results[router] = state

    return results
