#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ポンプ動作の残り秒数を取得する
#
import io
import sys
import cgi
import hydro_db
import hydro_http
import hydro_operation
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

query = cgi.FieldStorage()

conn = hydro_db.start()
record = hydro_db.getone(conn, 'work_pump')

dic = {}
if record['active'] == 1:
	if record['end_time'] == None:
		seconds = -1
	else:
		end = datetime.strptime(record['end_time'], '%Y/%m/%d %H:%M:%S')
#		start = datetime.strptime(query.getfirst('start_time'), '%Y/%m/%d %H:%M:%S')
		start = datetime.fromtimestamp(int(query.getfirst('start_time')))
		td = end - start
		seconds = td.total_seconds()
		if (seconds <= 0):
			seconds = 0
			ret = hydro_operation.pump_stop()
			if ret == True:
				sql = 'update work_pump set active = 0, end_time = cast(0 as datetime) where no = 1;'
				ret = hydro_db.exec(conn, sql)

else:
	seconds = 0

hydro_db.end(conn)
#print(seconds, file=sys.stderr)
dic['seconds'] = seconds

hydro_http.send_json(dic)
