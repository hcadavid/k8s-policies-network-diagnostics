import argparse
import csv
import time
import platform
import socket
import requests
import psutil
import os
from typing import Any
import json
from vantage6.algorithm.tools.util import info, warn, error



def get_ip_addresses(family):
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == family:
                yield (interface, snic.address)


def is_proxy_reachable(host:str,port:int):
    try:
        info(f"Checking if the node proxy ({host}:{str(port)}) is reachable... ")
        requests.get(f'http://{host}:{str(port)}', timeout=1)
        return True
    except requests.exceptions.RequestException:
        return False


def is_internet_reachable():
    try:
        info(f"Testing if internet IP addressess are rechable... ")
        requests.get('https://8.8.8.8', timeout=1)
        info(f"Testing if internet domain names addressess are solved... ")
        requests.get('https://www.google.com', timeout=1)
        return True
    except requests.exceptions.RequestException:
        return False


def partial(
    sleep_time:int
) -> Any:

    ipv4s = list(get_ip_addresses(socket.AF_INET))
    ipv6s = list(get_ip_addresses(socket.AF_INET6))
    proxy_host = os.environ.get("HOST")
    proxy_port = os.environ.get("PORT")

    print(f'Host architecture:{platform.uname()[4]}')
    print("IPv4 Addresses:")
    for interface, ipv4 in ipv4s:
        print(f"{interface}: {ipv4}")

    print("\nIPv6 Addresses:")
    for interface, ipv6 in ipv6s:
        print(f"{interface}: {ipv6}")

    internet_reachable = is_internet_reachable()
    print(f'Internet access :{"ENABLED" if internet_reachable else "DISABLED"}')    

    proxy_rechable = is_proxy_reachable(proxy_host,proxy_port)
    print(f'V6-proxy status :{f"REACHABLE at {proxy_host}:{proxy_port}" if proxy_rechable else f"DISABLED or unreachable at {proxy_host}:{proxy_port}"}')    

    print(f'Waiting {sleep_time} seconds before finishing the job.')
    time.sleep(sleep_time)

    return json.dumps({
        "proxy":f'{proxy_host}:{proxy_port}',
        "internet_reachable":internet_reachable,
        "proxy_reachable":proxy_rechable,
        "ipv4s_addresses":ipv4s,
        "ipv6s_addresses":ipv6s
    })