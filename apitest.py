#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json,time,hashlib
import requests
from urllib import urlencode
from base64 import b64encode
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from hashlib import md5

APP_KEY = '1d8b6e7d45233436'
APP_SECRET = '560c52ccd288fed045859ed18bffd973'

def getSign(params):
    items = params.items()
    items.sort()
    return md5(urlencode(items) + APP_SECRET).hexdigest()

def get_access_key(userid,password):
	baseurl="https://account.bilibili.com/api/login/v2?"
	sign_temp = hashlib.md5()
	url = 'http://passport.bilibili.com/login?act=getkey'
	getKeyRes = requests.get(url)
	token = json.loads(getKeyRes.content.decode('utf-8'))
	key = token['key'].encode('ascii')
	_hash=token['hash'].encode('ascii')
	key = RSA.importKey(key)
	cipher = PKCS1_v1_5.new(key)
	password =  b64encode(cipher.encrypt(_hash + password))
	item = {'appkey': APP_KEY, 
			'actionKey': "appkey", 
			'build': "414000",
			'platform':'android',
			'pwd':password,
			'ts':int(time.time()),
			'userid':userid}
	item['sign']=getSign(item)
	page_temp =json.loads(requests.get(baseurl,params=item).text)
	print page_temp
	if(page_temp['code'] != 0):
		return '-1'
	access_key = page_temp["access_key"]
	return access_key

def get_cookies(access_key):
	session = requests.Session()
	url ="http://passport.bilibili.com/api/login/sso?"
	url_tmp = url
	item = {'access_key':access_key,
			'appkey': APP_KEY, 
			'gourl':'https://account.bilibili.com/account/home',
			'ts':str(int(time.time()))}
	item['sign']=getSign(item)
	session.get(url,params=item)
	for key,value in item.items():
		url_tmp = url_tmp+key+"="+value+"&"
	print url_tmp
	return session.cookies.get_dict()

print get_cookies(get_access_key("15824397397","zsj0911*"))