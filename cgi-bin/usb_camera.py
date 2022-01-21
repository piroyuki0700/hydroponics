#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# USBカメラ利用
#
import os
import glob
import subprocess
import datetime
import hydro_db
import shutil
import fasteners

LOCK_FILE = "/tmp/hydro_camera_lock_file"
SAVE_PICTURE_DIR = './picture/'
TMP_PICTURE_DIR = './tmp/'
TMP_PICTURE_INFO = TMP_PICTURE_DIR + 'picture_info_' + hydro_db.DATABASE_ID + '.txt'

def insert_db(dic):
	conn = hydro_db.start()
	no = hydro_db.insert(conn, 'picture', dic)
	hydro_db.end(conn)
	return no

@fasteners.interprocess_locked(LOCK_FILE)
def exec_fswebcam(picture_dir):
	now = datetime.datetime.now()
	filename = "image_" + now.strftime('%Y%m%d_%H%M%S') + '.jpg'
	cmd = 'fswebcam -r 1280x720 --no-banner ' + picture_dir + filename
	ret = subprocess.run(cmd, shell=True)

	dic = {}
	if ret.returncode == 0:
		dic['taken'] = str(now.strftime('%Y-%m-%d %H:%M:%S'))
		dic['filename'] = filename
		dic['filepath'] = picture_dir + filename

	return dic

def take_tmp_picture():
	for filename in  glob.glob(TMP_PICTURE_DIR + '*.jpg'):
		os.remove(filename)

	data = exec_fswebcam(TMP_PICTURE_DIR)

	if len(data) == 0:
		return {}

	try:
		with open(TMP_PICTURE_INFO, mode='w') as f:
			f.write(data['filename'])
			f.write('\n')
			f.write(data['taken'])
			f.write('\n')
			f.close()
			return data

	except Exception as e:
		print(e)
		return {}

def save_tmp_picture():
	if not os.path.isfile(TMP_PICTURE_INFO):
		return False

	dic = {}
	try:
		with open(TMP_PICTURE_INFO, mode='r') as f:
			striped = [line.strip() for line in f.readlines()]
			f.close()
			dic['filename'] = striped[0]
			dic['taken'] = striped[1]

			shutil.move(TMP_PICTURE_DIR + dic['filename'], SAVE_PICTURE_DIR)
			no = insert_db(dic)
			ret = True if no > 0 else False
			return ret

	except Exception as e:
		print(e)
		return False

	finally:
		os.remove(TMP_PICTURE_INFO)

def discard_tmp_picture():
	if os.path.isfile(TMP_PICTURE_INFO):
		os.remove(TMP_PICTURE_INFO)
	return True

def take_picture(dir = SAVE_PICTURE_DIR):
	data = exec_fswebcam(dir)
#
#	if len(data) != 0:
#		data['no'] = insert_db(data)
#
	return data
#
# テスト用
#
if __name__ == '__main__':
	print(exec_fswebcam('./'))

