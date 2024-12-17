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


class Forcer:
    def __init__(self, url: str, wordlist:str, port: int=0, user='admin'):
        self.url = url
        self.wordlist = wordlist
        if port:
            self.url += ":" + str(port)
        self.user = user
  
def args_to_class():
    example_usage = '''example usage:
        ./xmlforcer.py -u john https://example.com /opt/wordlists/rockyou.txt -p 8443
        python3 xmlforcer.py http://example.com /opt/wordlists/rockyou.txt'''

    parser = argparse.ArgumentParser(prog='xmlforcer',
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

def main():
    forcer = args_to_class()
    print(forcer.__dict__)

if __name__ == "__main__":
    main()
