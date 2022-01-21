#!/usr/bin/python3
#
# 水補充処理トリガー（cron登録用）
#
import urllib.request
import os
import sys
import hydro_http

try:
	url = 'http://localhost:8000/cgi-bin/ctrl_subpump.py?request=refill'
	with urllib.request.urlopen(url, None, 180) as response:
		print(response.read().decode('utf-8'))
except Exception as e:
	print(e, file=sys.stderr)

