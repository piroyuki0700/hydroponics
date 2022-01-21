#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# twitter利用
#
import sys
import twitter
import usb_camera
import hydro_db

def tweet(token, message, file = ""):
	try:
		# twitter api
		api = twitter.Api(token['twitter_api_key'], token['twitter_api_secret_key'], token['twitter_access_token'], token['twitter_access_token_secret'])
		if len(file) == 0:
			api.PostUpdate(message)
		else:
			api.PostUpdate(message, media=file)
#		print(message + ", filename = " + file)
	except twitter.error.TwitterError as e:
		print(e, file=sys.stderr)


#
# テスト用
#
if __name__ == '__main__':
	conn = hydro_db.start()
	token = hydro_db.getone(conn, 'sns_token')
	hydro_db.end(conn)
	message = 'pythonでRaspberryPIのUSBカメラ撮影してそのままtweet'
	pict = usb_camera.take_picture('../picture/')
	tweet(token, message, data['filepath'])

