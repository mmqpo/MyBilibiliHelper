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
	baseurl="https://passport.bilibili.com/api/v2/oauth2/login?"
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
			'password':password,
			'username':userid}
	item['sign']=getSign(item)
	page_temp =json.loads(requests.post(baseurl,data=item).text)
	if(page_temp['code'] != 0):
		print(page_temp['data'])
		return '-1'
	access_key = page_temp["data"]['token_info']['access_token']
	return access_key

def get_cookies(access_key):
	session = requests.Session()
	url ="http://passport.bilibili.com/api/login/sso?"
	item = {'access_key':access_key,
			'appkey': APP_KEY, 
			'gourl':'https://account.bilibili.com/account/home',
			'ts':str(int(time.time()))}
	item['sign']=getSign(item)
	session.get(url,params=item)
	return session.cookies.get_dict()
