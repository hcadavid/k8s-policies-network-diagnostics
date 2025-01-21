import argparse
import csv
import time
import requests
import psutil
import os
from typing import Any
import json
import socket
import platform
import dns.resolver

from vantage6.algorithm.tools.util import info, warn, error


def get_ip_addresses(family):
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == family:
                yield (interface, snic.address)


def is_proxy_reachable(host: str, port: int):
    try:
        info(f"Checking if the FQDN of the node proxy ({host}:{str(port)}) can be resolved... ")

        ipaddr = socket.gethostbyname(host) 
        
        info(f"FQDN of the node proxy ({host}:{str(port)}) resolved as {ipaddr}... ")
        
        # Set timeout before creating connection
        socket.setdefaulttimeout(5)  # Set default timeout
        
        # Check if the port is listening
        sock = socket.create_connection((ipaddr, int(port)))
        
        info(f"Port {port} can be opened on the proxy ({host}) IP address: {ipaddr}")
        return True
    
    except socket.gaierror:
        info(f"Unreachable proxy: FQDN could not be resolved")
        return False
    except ConnectionRefusedError:
        info(f"Unreachable proxy: Connection refused on port {port}")
        return False
    except socket.timeout:
        info(f"Unreachable proxy: timeout occurred while trying to connecting to port {port}")
        return False
    except Exception as e:
        info(f"Unreachable proxy: Unexpected error: {str(e)}")
        return False
    
    finally:
        # Reset timeout after connection attempt
        socket.setdefaulttimeout(None)


def is_proxy_reachable(host:str,port:int):
    try:
        info(f"Checking if the FQDN of the node proxy ({host}:{str(port)}) can be resolved... ")
        ipaddr = socket.gethostbyname("v6proxy-subdomain.v6-jobs.svc.cluster.local") 
        info(f"FQDN of the node proxy ({host}:{str(port)}) resolved as {ipaddr}... ")    

        # Check if the port is listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ipaddr, int(port)))
        
        if result == 0:
            info(f"Port {port} is open on IP address {ipaddr}")
            return True
        else:
            info(f"Port {port} is closed on IP address {ipaddr}")
            return False


        return True
    except socket.gaierror:
        return False


def check_http_connection():
        try:
            # Attempt to reach www.google.com
            url = "http://www.google.com"
            timeout = 5
            
            # Send a GET request
            response = requests.get(url, timeout=timeout)
            
            # If the request was successful, return True
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error checking HTTP connection: {e}")
            return False


def is_internet_reachable():
    try:
        # Attempt to connect to Google's DNS server
        dns_server = "8.8.8.8"
        port = 53
        
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Set timeout to avoid hanging indefinitely
        sock.settimeout(5)
        
        # Try to send a packet to the DNS server
        result = sock.connect_ex((dns_server, port))
        
        # Close the socket
        sock.close()
        
        # If connection was successful, return True
        if result == 0:
            print(f"Internet access detected on {platform.node()}")
            return True
        else:
            print(f"Internet not reachable on {platform.node()}")
            return False
    
    except socket.error as e:
        print(f"Connection error (can't determine Internet connection status): {e}")
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
    print(f'Internet access (socket connection test) :{"ENABLED" if internet_reachable else "DISABLED"}')    

    http_outbound_connection = check_http_connection()
    print(f'Internet access (http connection test) :{"ENABLED" if http_outbound_connection else "DISABLED"}')    

    proxy_rechable = is_proxy_reachable(proxy_host,proxy_port)
    print(f'V6-proxy status :{f"REACHABLE at {proxy_host}:{proxy_port}" if proxy_rechable else f"DISABLED or unreachable at {proxy_host}:{proxy_port}"}')    

    print(f'Waiting {sleep_time} seconds before finishing the job.')
    time.sleep(int(sleep_time))

    return {
        "proxy":f'{proxy_host}:{proxy_port}',
        "internet_reachable":internet_reachable,
        "http_connection_test_passed":http_outbound_connection,
        "proxy_reachable":proxy_rechable,
        "ipv4s_addresses":ipv4s,
        "ipv6s_addresses":ipv6s
    }