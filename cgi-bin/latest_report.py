#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# データベースから最新の定時処理レポートを取得する
#
import io
import sys
import cgi
import hydro_db
import hydro_sensor
import hydro_http

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

query = cgi.FieldStorage()

conn = hydro_db.start()
report = hydro_db.getlatest(conn, 'report_routine')
hydro_db.end(conn)

# センサー値の状態判定を追加
evaluate = query.getvalue('evaluate')
if evaluate == 'on':
	status = hydro_sensor.evaluate(report)
	report.update(status)

hydro_http.send_json(report)

