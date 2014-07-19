#!/usr/bin/python

from Crypto.Cipher import AES
import base64
import getopt
import sys
import socket
import urllib
import urllib2
import os
import re

def usage():
	print "ip_tracer.py [options]"
	print "\t-h/--help: This listing"
	print "\t-p/--password: AES encode IP address with password"
	print "\t-r/--retrieve: AES decode (this is the value from pastebin)"
	print "EXAMPLES:"
	print "-just paste IP:"
	print "\tpython ip_tracer.py"
	print "-AES encode with password of 'nodns' and paste"
	print "\tpython ip_tracer.py -p nodns"
	print "-Decode an encrypted paste from pastebin that used nodns as password"
	print "\tpython ip_tracer.py -p nodns -r astringofbase64textfrompastebin=="

def encode(address):
	BLOCK_SIZE = 32
	PADDING = '#'	#just the padding char I chose to use
	#This command will pad for you
	pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
	EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))	#one-liner that encrypts
	cipher = AES.new(pad(password)) 								#init the cipher obj
	address = EncodeAES(cipher, address)							#do the encryption
	return address													#return result

#Very similar to encode routine, but with decryption and immediately exit
def getip():
	BLOCK_SIZE = 32
	PADDING = '#'
	pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
	DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
	cipher = AES.new(pad(password))
	decoded = DecodeAES(cipher, crypted)
	print decoded
	sys.exit(2)	

#Getopts routines
try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:r:h', ['password=','retrieve=' 'help'])
except getopt.GetoptError:
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt in ('-h', '--help'):
        usage()
        sys.exit(2)
    elif opt in ('-p', '--password'):
        password = arg
    elif opt in ('-r', '--retrieve'):
        crypted = arg        
    else:
        usage()
        sys.exit(2)

#If we just want to decode, check this first and only decode
try:
	crypted
except:
	next
else:
	getip()

#Routines for getting our public IP, with some regex magic.
try:
	internal = socket.gethostbyname(socket.gethostname())
	ip = urllib2.build_opener()
	ip.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0')]
	response = ip.open('http://www.whatismyip.com/')
	data = response.read()

	#It doesn't seem whatismyip supports automation anymore? Owell, regex! Below is the type of html we are dealing with
	#<div class="center-ip"><div class="ip">Your IP:</div><div class="the-ip"><label id="a526317">&#54;</label><span id="f694853">&#56;</span><label id="c840526">&#46;</label><label id="b446476">&#50;</label><span id="e372719">&#50;</span><label id="f725930">&#53;</label><span id="g781322">&#46;</span><label id="a322244">&#49;</label><label id="e483024">&#57;</label><span id="c817554">&#53;</span><span id="g879085">&#46;</span><label id="c625611">&#49;</label><span id="g925342">&#54;</span><span id="g184751">&#53;</span></div>
	digits=re.compile('Your IP(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?(.+?&#(\d+))?.+$',re.DOTALL|re.M)
	address = ''
	#Note that the html has each digit (and period) encoded as &#number. Our regex parses all of these chars into an array
	#Due to the () capturing, actual digits will be every other element, which is why we init i to 2 and i+=2 on each iteration
	#The actual "digit" is 48 less than the number in html (54 is actually a '6').
	#Other than that, we do a few string and integer conversions and glue back together our IP address
	i = 2
	while (digits.search(data).group(i)):
		if digits.search(data).group(i) == '46':	#46 is a period...
			address = address + '.'
		else:
			address = address + str(int(digits.search(data).group(i)) - 48)
		i += 2

except:
	sys.exit(0)

#Check what the most recent IP was
if os.path.exists("/tmp/ip_tracer.txt"):
	f = file("/tmp/ip_tracer.txt", "r+")
	prev_ip = []
	for ip in f:
		prev_ip.append(ip.rstrip())
	print prev_ip
else:
	f = file("/tmp/ip_tracer.txt", "w")

#If the user wants to use a password to encrypt, encode the address first
try:
	password
except:
	next
else:
	address = encode(address)

#Routine to paste on pastebin
def pastebin():
	my_api_dev_key 			= 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' # your api_developer_key
	my_api_paste_code 		= "internal ip: "+ internal + "\nexternal ip: "+ address + "\n"
	my_api_paste_private 		= '2' # 0=public 1=unlisted 2=private
	my_api_paste_name			= 'ip_tracing'
	my_api_paste_expire_date 		= '1D'
	my_api_paste_name			= urllib.quote(my_api_paste_name)
	my_api_paste_code			= urllib.quote(my_api_paste_code)
	my_api_user_name = 'your_user_id'
	my_api_user_password = 'your_password'

	auth_response = urllib2.urlopen('http://pastebin.com/api/api_login.php', 'api_dev_key=%s&api_user_name=%s&api_user_password=%s' %(my_api_dev_key, my_api_user_name, my_api_user_password))
	my_api_user_key = auth_response.read()

	response = urllib2.urlopen('http://pastebin.com/api/api_post.php', 'api_option=paste&api_user_key=%s&api_paste_private=%s&api_dev_key=%s&api_paste_name=%s&api_paste_expire_date=%s&api_paste_code=%s' %(my_api_user_key, my_api_paste_private, my_api_dev_key, my_api_paste_name, my_api_paste_expire_date, my_api_paste_code))

#Check to see if the IP has changed, otherwise, no need to use a limited private paste
if not prev_ip:
	pastebin()
	f.write(internal+"\n")
	f.write(address+"\n")
	f.close
elif prev_ip[0] != internal or prev_ip[1] != address:
	pastebin()
	f.seek(0)
	f.write(internal+"\n")
	f.write(address+"\n")
	f.close
