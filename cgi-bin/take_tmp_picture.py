#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# テンポラリ写真ファイルとして写真撮影
#
import io
import sys
import usb_camera
import hydro_http

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

dic = usb_camera.take_tmp_picture()
hydro_http.send_json(dic)

