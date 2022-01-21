#!/usr/bin/python3
#
# httpの定型文送信
#
import json
from datetime import datetime

def send_plane(text):
	print('Content-Type: text/plane charset=utf-8')
	print('Access-Control-Allow-Origin: *')
	print('')
	print(text)

def send_json(dic):
	print('Content-Type: text/json; charset=utf-8')
	print('Access-Control-Allow-Origin: *')
	print('')
	print(json.dumps(dic))

def send_result(ret):
	result = "success" if ret == True else "failed"
	dic = {}
	dic['result'] = result
	dic['datetime'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	send_json(dic)
#	send_plane(result)

