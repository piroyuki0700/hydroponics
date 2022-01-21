#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# データベースから定時処理設定を取得する
#
import io
import sys
import cgi
import hydro_db
import hydro_http

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = cgi.FieldStorage()

conn = hydro_db.start()
ret = hydro_db.updateone(conn, 'setting_schedule', form)
hydro_db.end(conn)

hydro_http.send_result(ret)

