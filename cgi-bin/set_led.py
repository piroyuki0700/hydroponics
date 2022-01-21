#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# LEDのON/OFFテスト
#
import io
import sys
import cgi
import hydro_http
import hydro_operation

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = cgi.FieldStorage()

num = int(form.getfirst('num'))
state = form.getfirst('state')
ret = hydro_operation.set_led(num, state)

hydro_http.send_result(ret)
