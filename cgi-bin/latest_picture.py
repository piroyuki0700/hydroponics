#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# データベースから基本情報を取得する
#
import io
import sys
import hydro_db
import hydro_http

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = hydro_db.start()
dic = hydro_db.getlatest(conn, 'picture')
hydro_db.end(conn)

hydro_http.send_json(dic)
