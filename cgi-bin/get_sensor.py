#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# データベースからセンサー閾値設定を取得する
#
import io
import sys
import hydro_db
import hydro_http

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = hydro_db.start()
dic = hydro_db.getone(conn, 'setting_sensor')
hydro_db.end(conn)

hydro_http.send_json(dic)
