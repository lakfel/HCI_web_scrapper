import requests, re
from bs4 import BeautifulSoup
import json




def load_txt_proxies():
    filename = 'proxies_list.txt'
    proxies = []
    with open(filename, 'r', encoding='utf-8', errors='replace') as file:
        for line in file:
            # Remove any leading/trailing whitespace characters
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            # Split the IP and port based on the colon
            ip, port = line.split(':')
            # Add the proxy in the required format
            proxies.append({
                'ip': ip,
                'port': port,
                'protocols': ['http'],  # Assuming HTTP proxies (adjust as needed)
            })
    return proxies
    

def load_proxies(filename):
 
    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as file:
            proxies = json.load(file)
        return proxies
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []
    except UnicodeDecodeError as e:
        print(f"Unicode decoding error: {e}")
        return []

def format_proxy(proxy):
    # Format the proxy based on its protocol and IP address
    protocol = proxy['protocols'][0]  # Using the first available protocol (e.g., 'socks4')
    #protocol = proxy['protocol'] # Using the first available protocol (e.
    return {
        "http": f"{protocol}://{proxy['ip']}:{proxy['port']}",
        "https": f"{protocol}://{proxy['ip']}:{proxy['port']}"
    }



def create_proxies_file():
    regex = r"[0-9]+(?:\.[0-9]+){3}:[0-9]+"
    c = requests.get("https://spys.me/proxy.txt")
    test_str = c.text
    a = re.finditer(regex, test_str, re.MULTILINE)
    with open("proxies_list.txt", 'w') as file:
        for i in a:
            print(i.group(),file=file)
    e =  requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text")
    test_str = e.text
    a = re.finditer(regex, test_str, re.MULTILINE)
    with open("proxies_list.txt", 'a') as file:
        for i in a:
            print(i.group(),file=file)
    e =  requests.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt")
    test_str = e.text
    a = re.finditer(regex, test_str, re.MULTILINE)
    with open("proxies_list.txt", 'a') as file:
        for i in a:
            print(i.group(),file=file)
    '''e =  requests.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt")
    test_str = e.text
    a = re.finditer(regex, test_str, re.MULTILINE)
    with open("proxies_list.txt", 'a') as file:
        for i in a:
            print(i.group(),file=file)
    e =  requests.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt")
    test_str = e.text
    a = re.finditer(regex, test_str, re.MULTILINE)
    with open("proxies_list.txt", 'a') as file:
        for i in a:
            print(i.group(),file=file)'''
    d = requests.get("https://free-proxy-list.net/")
    soup = BeautifulSoup(d.content, 'html.parser')
    td_elements = soup.select('.fpl-list .table tbody tr td')
    ips = []
    ports = []
    for j in range(0, len(td_elements), 8):
        ips.append(td_elements[j].text.strip())
        ports.append(td_elements[j + 1].text.strip())
    with open("proxies_list.txt", "a") as myfile:
        for ip, port in zip(ips, ports):
            proxy = f"{ip}:{port}"
            print(proxy, file=myfile)

