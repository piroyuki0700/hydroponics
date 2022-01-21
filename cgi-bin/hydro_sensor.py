#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# LINE利用
#
import sys
import hydro_db

def evaluate(report):
	conn = hydro_db.start()
	sensor = hydro_db.getone(conn, 'setting_sensor')
	hydro_db.end(conn)
	status = {}
	danger = False
	warning = False

	# 個別ステータス
	items = ['air_temp', 'humidity', 'water_temp', 'water_level', 'tds_level'];
	for item in items:
		vlow = item + '_vlow'
		if (vlow in sensor):
			if (report[item] < sensor[vlow]):
				status[item + '_status'] = 'danger'
				danger = True
				continue
		low = item + '_low'
		if (low in sensor):
			if (report[item] < sensor[low]):
				status[item + '_status'] = 'warning'
				warning = True
				continue
		vhigh = item + '_vhigh'
		if (vhigh in sensor):
			if (report[item] > sensor[vhigh]):
				status[item + '_status'] = 'danger'
				danger = True
				continue
		high = item + '_high'
		if (high in sensor):
			if (report[item] > sensor[high]):
				status[item + '_status'] = 'warning'
				warning = True
				continue
		status[item + '_status'] = 'normal'

	# 全体ステータス
	if danger == True:
		status['total_status'] = 'danger'
	elif warning == True:
		status['total_status'] = 'warning'
	else:
		status['total_status'] = 'normal'

	return status

#
# テスト用
#
if __name__ == '__main__':
	conn = hydro_db.start()
	report = hydro_db.getlatest(conn, 'report_routine')
	hydro_db.end(conn)
	status = evaluate(report)
	report.update(status)
	print(report)

