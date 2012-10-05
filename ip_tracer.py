#!/usr/bin/python

import sys
import socket
import urllib
import urllib2
import os

try:
	internal = socket.gethostbyname(socket.gethostname())
	external = urllib2.urlopen('http://automation.whatismyip.com/n09230945.asp').read()
except:
	sys.exit(0)

if os.path.exists("/tmp/ip_tracer.txt"):
	f = file("/tmp/ip_tracer.txt", "r+")
	prev_ip = []
	for ip in f:
		prev_ip.append(ip.rstrip())
	print prev_ip
else:
	f = file("/tmp/ip_tracer.txt", "w")

def pastebin():
	my_api_dev_key 			= 'xxxxxxxx' # your api_developer_key
	my_api_paste_code 		= "internal ip: "+ internal + "\nexternal ip: "+ external + "\n"
	my_api_paste_private 		= '2' # 0=public 1=unlisted 2=private
	my_api_paste_name			= 'ip_tracing'
	my_api_paste_expire_date 		= '1D'
	my_api_paste_name			= urllib.quote(my_api_paste_name)
	my_api_paste_code			= urllib.quote(my_api_paste_code)
	my_api_user_name = 'username'
	my_api_user_password = 'password'

	auth_response = urllib2.urlopen('http://pastebin.com/api/api_login.php', 'api_dev_key=%s&api_user_name=%s&api_user_password=%s' %(my_api_dev_key, my_api_user_name, my_api_user_password))
	my_api_user_key = auth_response.read()

	response = urllib2.urlopen('http://pastebin.com/api/api_post.php', 'api_option=paste&api_user_key=%s&api_paste_private=%s&api_dev_key=%s&api_paste_name=%s&api_paste_expire_date=%s&api_paste_code=%s' %(my_api_user_key, my_api_paste_private, my_api_dev_key, my_api_paste_name, my_api_paste_expire_date, my_api_paste_code))

if not prev_ip:
	pastebin()
	f.write(internal+"\n")
	f.write(external+"\n")
	f.close
elif prev_ip[0] != internal or prev_ip[1] != external:
	pastebin()
	f.seek(0)
	f.write(internal+"\n")
	f.write(external+"\n")
	f.close
