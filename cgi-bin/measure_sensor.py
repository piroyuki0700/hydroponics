#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# センサー値の取得テスト
#
import io
import sys
import cgi
import hydro_http
import hydro_operation

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = cgi.FieldStorage()

num = int(form.getfirst('num'))
dic = hydro_operation.measure_sensor(num)

hydro_http.send_json(dic)
