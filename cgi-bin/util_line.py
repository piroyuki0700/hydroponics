#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# LINE利用
#
import sys
import requests
import hydro_db

def notify(token, message, filename=""):
	# line api
	payload = {'message': message}  
	headers = {'Authorization': 'Bearer ' + token}
	files = {}
	print(filename, file=sys.stderr)
	if filename != "":
		files['imageFile'] = open(filename, "rb")
	ret = requests.post('https://notify-api.line.me/api/notify', data=payload, headers=headers, files=files)

#
# テスト用
#
if __name__ == '__main__':
	conn = hydro_db.start()
	token = hydro_db.getcolumn(conn, 'sns_token', 'line_access_token')
	hydro_db.end(conn)
	notify(token, '通知テスト from Raspberry PI')

