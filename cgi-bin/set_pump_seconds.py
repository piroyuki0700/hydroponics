#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# �|���v����̎c��b����ݒ肷��
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
		# ���쒆�̒�~
		ret = hydro_operation.pump_stop()
		if ret == True:
			sql = 'update work_pump set active = 0, end_time = cast(0 as datetime) where no = 1;'
			ret = hydro_db.exec(conn, sql)
	else:
		# ��~���̒�~�͏����Ȃ��Ő�������
		ret = True

else:

	if record['active'] == 1:
		# ���쒆�̊J�n�́A���쎞�Ԃ̕ύX�̂�
		ret = True
	else:
		ret = hydro_operation.pump_start()

	if ret == True:
		if seconds < 0:
			# �A������
			sql = 'update work_pump set active = 1, end_time = cast(0 as datetime) where no = 1;'
		else:
			# ���Ԏw�蓮��
			sql = f'update work_pump set active = 1, end_time = now() + interval {seconds} second where no = 1;'

		ret = hydro_db.exec(conn, sql)

hydro_db.end(conn)

hydro_http.send_result(ret)

