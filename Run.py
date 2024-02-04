import requests
from bs4 import BeautifulSoup
import json
import urllib3
import time
import sys
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def write_to_file(filename, data):
    with open(filename, 'a', encoding='utf-8') as file:
        for item in data:
            file.write(f"{item}\n")

def http_write_to_file(filename, data):
    with open(filename, 'a', encoding='utf-8') as file:
        for item in data:
            file.write(f"{item}")

def fetch_data(url, page, headers):
    response = requests.get(f"{url}&page={page}", verify=False, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        return json_data.get('data', {}).get('result', [])
    else:
        print(f"[!] SORRY, you have been blocked. Please change the agent after the script is finished. Status code: {response.status_code}")
        return []

def fetch_a_tags(url, headers):
    response = requests.get(url, verify=False, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a', string=lambda text: text and 'faw.cn' in text)
        return [tag.text for tag in a_tags]
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return []

def check_domains(domains_file,url):
    with open(domains_file, 'r', encoding='utf-8') as file:
        domains = file.readlines()

    for domain in domains:
        domain = domain.strip()  # Remove leading and trailing whitespace characters, such as newlines
        http_url = f"http://{domain}"
        https_url = f"https://{domain}"

        try:
            # Check HTTP protocol
            check_protocol(http_url,url)
            # Check HTTPS protocol
            check_protocol(https_url,url)

        except requests.RequestException as e:
             pass


def check_protocol(urls,url):
    result_filename = f"{url}_status_output.txt"
    response = requests.get(urls, timeout=5)
    try:
        title,response_length = extract_title(response.content, 'utf-8')
        if (response.status_code!=503):
            print(f"Domain: {urls} | Status: {response.status_code} | Title: {title} | Length: {response_length}\n")
            http_write_to_file(result_filename,urls + " - " + title + " - " + str(response.status_code) + "\n")
        pass
    except Exception as e:
        print(f"{e}\n")
    # if(response.status_code!=503):
    #     http_write_to_file(result_filename,urls + " - " + title + " - " + str(response.status_code) + "\n")

def extract_title(html,encoding='utf-8'):
    soup = BeautifulSoup(html, 'html.parser', from_encoding=encoding)
    title_tag = soup.title
    return title_tag.string.strip() if title_tag else "N/A",len(html)

def main():

    fingerprint()

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('url', type=str, help='python3 Run.py xxx.com')
    parser.add_argument('--check', action='store_true', help='Optional, perform status detection on the collection results at the same time, and output the title')
    args = parser.parse_args()

    url = args.url
    check_option = args.check

    print("[*]ಠಿ⁠_⁠ಠThe task is being executed, please wait... The waiting time depends on the network conditions. Generally, the results will be available within 10 seconds. If there are many assets, it will take longerಠಿ⁠_⁠ಠ")

    proxy = {
        'http': 'http://localhost:8080',
        'https': 'http://localhost:8080'
    }

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    }

    headers_weixin = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G9300 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 Mobile Safari/537.36 MicroMessenger/6.6.7.1321(0x26060739) NetType/WIFI Language/zh_CN'
    }

    headers_weixinIOS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1 MicroMessenger/6.6.7 NetType/WIFI Language/zh_CN'
    }

    headers_firefox = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    }

    headers_safari = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15'
    }

    result_filename = f"{url}_output.txt"

    response = requests.get("https://crt.sh/?q=" + url, verify=False, headers=headers)

    if response.status_code == 200:
        soup1 = BeautifulSoup(response.text, 'html.parser')

        matching_cells = soup1.find_all('td', string=lambda text: text and url in text)

        # When traversing the results, exclude the <td> tag of the specified class, because there is a tag that also contains the target character, but it is junk information, so don’t forget about it. By the way, the results will be deduplicated.
        unique_matching_cells = set()
        for cell in matching_cells:
            if 'outer' not in cell.get('class', []):
                unique_matching_cells.add(cell.text)
        print("[+](⁠●⁠_⁠_⁠●⁠)First round of collection(⁠✿⁠⁠)")
        for unique_cell in unique_matching_cells:
            print(unique_cell)
            write_to_file(result_filename, [unique_cell])
        print("\n")
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")

    page = 2
    all_results = []
    while True:
    	#This interface only has data starting from the second page, and the first page is not displayed
    	results = fetch_data(f"https://chaziyu.com/ipchaxun.do?domain={url}", page, headers_weixin)
    	if results:
    		all_results.extend(results)
    		page += 1
    		time.sleep(3)  #To prevent being blocked, slow down a bit
    	else:
    		break
    print("[+](⁠｡⁠☬⁠０⁠☬⁠｡⁠)Second round of collection(⁠｡⁠☬⁠０⁠☬⁠｡⁠)")
    for result in all_results:
    	print(result)
    	write_to_file(result_filename, [result])
    print("\n")

    #The first page results above are directly output to HTML, so there is no data on the first page of the above interface. Here is the missing data on the first page
    a_tags = fetch_a_tags(f"https://chaziyu.com/{url}/", headers_weixin)
    print("[+](⁠✿⁠☉⁠｡⁠☉⁠)The third round of collection(⁠✿⁠☉⁠｡⁠☉⁠)")
    for tag in a_tags:
    	print(tag)
    	write_to_file(result_filename, [tag])
    print("\n")
    print(f"…⁠ᘛ⁠⁐̤⁠ᕐ⁠ᐷThe collection is completed.If there are any results, they will be generated in the current directory….(⁠☞ﾟ⁠∀ﾟ⁠)⁠☞{result_filename}file\n")

    if check_option:
        print("[*] Status check in progress(Skip 503 errors)...")
        print("__________________________________________________________________\n")
        check_domains(f"{url}_output.txt",url)
    print("\n")
    print("[+] Mission ended")

def fingerprint():
	author = '''

   _____       __        __                      _                                     
  / ___/__  __/ /_  ____/ /___  ____ ___  ____ _(_)___     
  \__ \/ / / / __ \/ __  / __ \/ __ `__ \/ __ `/ / __ \   
 ___/ / /_/ / /_/ / /_/ / /_/ / / / / / / /_/ / / / / /  
/____/\__,_/_.___/\__,_/\____/_/ /_/ /_/\__,_/_/_/ /_/     
                                                           

Develop by 
© VICTOR is GEEK ©
(⁠✪⁠㉨⁠✪⁠)FASTSSH MYANMAR GROUP(⁠✪⁠㉨⁠✪⁠)
________________________________________________________
	'''
	print(author)

if __name__ == "__main__":
    main()
