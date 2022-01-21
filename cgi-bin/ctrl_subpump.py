#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# サブポンプ処理
# 
import io
import sys
import cgi
import hydro_http
import hydro_db
import hydro_operation
import threading
import util_line
import time
from datetime import datetime

SUBP_START_LIMIT = 20 # サブポンプ動作開始レベル
SUBP_TIME_ON = 160	# 基本動作時間（秒）
SUBP_TIME_MIN = 5	# 最短動作時間（秒）

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

event_subp = 0

def sub_pump_end(gpio_pin):
	global event_subp
	print("empty. event set")
	event_subp.set()

#
# 水を補充する
#
def refill_water():
	global event_subp
	dic = hydro_operation.measure_water_level()
	level = dic ['water_level']
	message = ""

	if 0 < level and level < SUBP_START_LIMIT:
		available = hydro_operation.sub_level_check()

		if available:
			event_subp = threading.Event()
			hydro_operation.sub_pump_set_end_cb(sub_pump_end)

			seconds = SUBP_TIME_ON - level
			if seconds < SUBP_TIME_MIN:
				seconds = SUBP_TIME_MIN

			start_time = datetime.now()
			hydro_operation.sub_pump_start()
			ret = event_subp.wait(seconds)
			if ret == True:
				time.sleep(SUBP_TIME_MIN) # センサー感知から最短動作させて停止
			hydro_operation.sub_pump_stop()
			end_time = datetime.now()

			past = int((end_time - start_time).total_seconds()) + 1

			event_subp.clear()
			dic = hydro_operation.measure_water_level()
			level_after = dic ['water_level']
			level_plus = level_after - level
			message = f"{past}秒間、水を追加しました。\n水位{level}％→{level_after}％（+{level_plus}％）"
			if ret == True:
				message += "\nサブタンクの水がなくなりました"
		else:
			message = f"## 危険 ##\n 水位{level}％、サブタンクの水がありません。"

		conn = hydro_db.start()
		token = hydro_db.getcolumn(conn, 'sns_token', 'line_access_token')
		hydro_db.end(conn)
		util_line.notify(token, message)
	else:
		message = f"水位{level}％、問題なし"

	print(message)
	result = {}
	result['message'] = message
	return result

print("----- start -----")
form = cgi.FieldStorage()
request = form.getfirst('request')

result = {}
if request == 'level':
	result['available'] = hydro_operation.sub_level_check()
elif request == 'refill':
	try:
		result = refill_water()
	except Exception as e:
		print(e, file=sys.stderr)
		result['message'] = e

elif request == 'on':
	result['result'] = hydro_operation.sub_pump_start()
elif request == 'off':
	result['result'] = hydro_operation.sub_pump_stop()
else:
	result['message'] = f'unknown request {request}'

hydro_http.send_json(result)

