#!/usr/bin/python3
#
# 定時処理トリガー（cron登録用）
#
import urllib.request
import os
import hydro_http

url = 'http://localhost:8000/cgi-bin/make_report.py'
with urllib.request.urlopen(url, None, 180) as response:
	print(response.read().decode('utf-8'))

