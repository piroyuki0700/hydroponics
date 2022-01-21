#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ポンプ動作の残り秒数を設定する
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
seconds = int(query.getfirst('seconds'))

conn = hydro_db.start()
record = hydro_db.getone(conn, 'work_pump')

ret = False
if seconds == 0:

	if record['active'] == 1:
		# 動作中の停止
		ret = hydro_operation.pump_stop()
		if ret == True:
			sql = 'update work_pump set active = 0, end_time = cast(0 as datetime) where no = 1;'
			ret = hydro_db.exec(conn, sql)
	else:
		# 停止中の停止は処理なしで成功扱い
		ret = True

else:

	if record['active'] == 1:
		# 動作中の開始は、動作時間の変更のみ
		ret = True
	else:
		ret = hydro_operation.pump_start()

	if ret == True:
		if seconds < 0:
			# 連続動作
			sql = 'update work_pump set active = 1, end_time = cast(0 as datetime) where no = 1;'
		else:
			# 時間指定動作
			sql = f'update work_pump set active = 1, end_time = now() + interval {seconds} second where no = 1;'

		ret = hydro_db.exec(conn, sql)

hydro_db.end(conn)

hydro_http.send_result(ret)

