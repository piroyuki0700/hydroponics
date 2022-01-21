#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# テンポラリレポートを取得する
#
import io
import sys
import cgi
import hydro_operation
import hydro_sensor
import hydro_http

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

query = cgi.FieldStorage()

# データベースには保存しない一時的なセンサー情報
report = hydro_operation.measure_sensors()


# センサー値の状態判定を追加
evaluate = query.getvalue('evaluate')
if evaluate == 'on':
	status = hydro_sensor.evaluate(report)
	report.update(status)

hydro_http.send_json(report)

