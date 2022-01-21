#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# 定時処理実施
# センサー情報を取得してデータベースへ最新の定時処理レポートを保存する
#
import io
import sys
from datetime import datetime
import hydro_db
import hydro_http
import hydro_operation
import hydro_sensor
import usb_camera
import util_twitter
import util_line

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 現在時刻の取得
now = datetime.now()

# 定時処理設定の取得
conn = hydro_db.start()
basic = hydro_db.getone(conn, 'setting_basic')
schd = hydro_db.getone(conn, 'setting_schedule')
pict = {}

# 動作判定
if schd['active'] == 1 and schd['routine_start'] <= now.hour and now.hour <= schd['routine_end']:
	#
	# センサー値の取得
	#
	report = hydro_operation.measure_sensors()
	report['report_time'] = now.strftime('%Y/%m/%d %H:%M:%S')

	#
	# 写真撮影
	#
	if now.hour in (schd['camera1'], schd['camera2'], schd['camera3']):
		pict = usb_camera.take_picture()
		if len(pict) != 0:
			no = hydro_db.insert(conn, 'picture', pict)
			report['picture_no'] = no

	#
	# レポート保存
	#
	no = hydro_db.insert(conn, 'report_routine', report)

	#
	# ポンプ動作
	#
	record = hydro_db.getone(conn, 'work_pump')

	# 動いていなければ動かす。とりあえず止める方はブラウザ側に任せる。
	if record['active'] == 1:
		print('pump is already active', file=sys.stderr)
#	if record['active'] == 0:
	hydro_operation.pump_start()

	# 動作時刻の更新
	seconds = schd["routine_time"] * 60
	if now.hour < 8:	# 早朝は30分
		seconds = 30 * 60
	elif 17 < now.hour:	# 夜も30分で充分
		seconds = 30 * 60
	sql = f'update work_pump set active = 1, end_time = now() + interval {seconds} second where no = 1;'
	ret = hydro_db.exec(conn, sql)

	#
	# 状態判定 ok/warning/danger
	#
	status = hydro_sensor.evaluate(report)
	symbol = {'normal': '〇', 'warning': '△', 'danger': '×'}

	message = "【自動送信】"
	message += f"気温 {report['air_temp']}℃({symbol[status['air_temp_status']]})、"
	message += f"湿度 {report['humidity']}％({symbol[status['humidity_status']]})、"
	message += f"水温 {report['water_temp']}℃({symbol[status['water_temp_status']]})、"
	message += f"水位 {report['water_level']}％({symbol[status['water_level_status']]})、"
	message += f"濃度 EC{report['tds_level']}({symbol[status['tds_level_status']]})、"
	message += f"明るさ {report['brightness']}"

	# 報告時間ならtwitter通知
	if schd['report_active'] == 1 and schd['report_time'] == now.hour:
		token = hydro_db.getone(conn, 'sns_token')
		if len(pict) == 0:
			util_twitter.tweet(token, message)
		else:
			util_twitter.tweet(token, message, pict['filepath'])

	# 危険な項目があればline通知
	if schd['emergency_active'] and status['total_status'] == 'danger':
		token = hydro_db.getcolumn(conn, 'sns_token', 'line_access_token')
		if len(pict) == 0:	# 定時写真がなければ撮影
			pict = usb_camera.take_picture('/tmp/')
		util_line.notify(token, "## 危険 ##\n" + message, pict['filepath'])

	# 状態をLEDに反映
	led_color = "green"
	if status['total_status'] == 'danger':
		led_color = 'red'
	elif status['total_status'] == 'warning':
		led_color = 'yellow'
	hydro_operation.update_led(led_color)

elif schd['active'] == 1:
	hydro_operation.update_led('blue')
	ret = True

	if now.hour == 21 or now.hour == 0 or now.hour == 3:
		hydro_operation.pump_start()

		# 動作時刻の更新
		seconds = 10 * 60	# 夜中に3回動作
		sql = f'update work_pump set active = 1, end_time = now() + interval {seconds} second where no = 1;'
		ret = hydro_db.exec(conn, sql)

else:
	# 処理なしの場合は成功扱いとする
	hydro_operation.update_led('none')
	ret = True

hydro_db.end(conn)
#
# 結果を送信
#
hydro_http.send_result(ret)

