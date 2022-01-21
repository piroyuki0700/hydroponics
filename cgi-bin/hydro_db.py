#!/usr/bin/python3
#
# データベース操作モジュール
#
import mariadb
import os
import sys
import datetime
import hydro_http

# データベース名はこれを使っている。
DATABASE_ID = 'hydro2021summer'

def start():
	try:
		# Connect to MariaDB Platform
		conn = mariadb.connect(
			user = 'hydroponics',
			password = 'hydro0700',
			host = 'localhost',
			port = 3306,
			database = DATABASE_ID
		)
		return conn

	except mariadb.Error as e:
		print(f"mariadb.Error: {e}", file=sys.stderr)
		sys.exit(1)

def end(conn):
	# Close Connection
	conn.close()

def exec(conn, sql):
	try:
		cur = conn.cursor()
		cur.execute(sql)
		cur.close()
		conn.commit()
		return True

	except mariadb.Error as e:
		print(f"mariadb.Error: {e}", file=sys.stderr)
		return False

def getcolumn(conn, table, column):
	try:
		cur = conn.cursor()
		sql = 'select ' + column + ' from ' + table + ' where no = 1;'
		cur.execute(sql)
		row = cur.fetchone()
		cur.close()
		return row[0]

	except mariadb.Error as e:
		print(f"mariadb.Error: {e}", file=sys.stderr)
		return ""

def getkeys(cur, table):
	sql = 'desc ' + table + ';'
	cur.execute(sql)
	keys = []
	for row in cur.fetchall():
		keys.append(row[0])

	return keys

def getone(conn, table):
	return get(conn, table, "no = 1")

def getlatest(conn, table):
	return get(conn, table, "no = (select max(no) from " + table + ")")

def get(conn, table, condition = None):
	try:
		cur = conn.cursor()
		keys = getkeys(cur, table)

		where = ''
		if condition != None:
			where = ' where ' + condition

		sql = 'select * from ' + table + where + ';'
		cur.execute(sql)

		dic = {}
		row = cur.fetchone()
		for i in range(1, len(row)):
			if isinstance(row[i], datetime.datetime):
				dic[keys[i]]=row[i].strftime('%Y/%m/%d %H:%M:%S')
#				dic[keys[i]]=row[i].timestamp()
			else:
				dic[keys[i]]=row[i]

		cur.close()
		return dic

	except mariadb.Error as e:
		print(f"mariadb.Error: {e}", file=sys.stderr)
		return {}

def insert(conn, table, data):
	try:
		cur = conn.cursor()
		keys = getkeys(cur, table)

		column = []
		value = []
		for key in keys:
			if key in data:
				column.append(key)
				value.append(f'"{data[key]}"')

		columns = ','.join(column)
		values = ','.join(value)
		sql = 'insert into ' + table + '(' + columns + ') values (' + values + ');'

		cur.execute(sql)
		cur.close()
		conn.commit()

		return cur.lastrowid

	except mariadb.Error as e:
		print(f"mariadb.Error: {e}", file=sys.stderr)
		return -1

def updateone(conn, table, form):
	try:
		cur = conn.cursor()
		keys = getkeys(cur, table)

		column = []
		for key in keys:
			if key in form:
				column.append(key + '=' + form.getfirst(key))

		columns = ','.join(column)
		sql = 'update ' + table + ' set ' + columns + ' where no = 1;'
		cur.execute(sql)
		cur.close()
		conn.commit()
		return True

	except mariadb.Error as e:
		print(f"mariadb.Error: {e}", file=sys.stderr)
		return e

#
# テスト用
#
#if os.environ['REQUEST_METHOD'] == 'GET':
if __name__ == '__main__':
	conn = start()
	dic = getlatest(conn, 'setting_sensor')
	end(conn)

	hydro_http.send_json(dic)

