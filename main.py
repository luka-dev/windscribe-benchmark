import csv
import io
import os
import subprocess

import requests

def ws_disconnect():
    os.system("windscribe-cli disconnect")

def ws_connect(server):
    try:
        result = subprocess.run(["windscribe-cli", "connect", server, "Wireguard"], timeout=60)
        return result.returncode == 0
    except:
        return False


def ws_servers():
    # get json from #https://api.windscribe.com/WebsiteStatus
    url = "https://api.windscribe.com/WebsiteStatus"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,ru;q=0.8,uk;q=0.7",
        "authorization": "Bearer 1234",
        "origin": "https://windscribe.com",
        "priority": "u=1, i",
        "referer": "https://windscribe.com/",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers).json()

    hosts = []

    for locX in response["data"]["locations"]:
        location = response["data"]["locations"][locX]
        for server in location["pops"]:
            hosts.append(server["name"].split(" - ")[1])

    return hosts

def speed_test():
    result = subprocess.run(["speedtest", "--progress=no", "-f", "csv"], capture_output=True, text=True)
    csv_output = result.stdout

    headers = [
        "server name", "server id", "idle latency", "idle jitter", "packet loss", "download", "upload",
        "download bytes", "upload bytes", "share url", "download server count", "download latency",
        "download latency jitter", "download latency low", "download latency high", "upload latency",
        "upload latency jitter", "upload latency low", "upload latency high", "idle latency low", "idle latency high"
    ]

    csv_reader = csv.DictReader(io.StringIO(csv_output), fieldnames=headers)
    data = list(csv_reader)

    if len(data) > 0:
        print(int(data[0]['download']) / 1024 / 1024)
        return data[0]

    return None


def main():
    ws_disconnect()
    hosts = ws_servers()

    speeds = []
    for host in hosts:
        # print(host)
        if ws_connect(host):
            speeds.append(speed_test())
            ws_disconnect()

    speeds = sorted(speeds, key=lambda x: x["download"], reverse=True)
    print(speeds)

if  __name__ == "__main__":
    main()