#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# テンポラリ写真ファイルの破棄
#
import io
import sys
import usb_camera
import hydro_http

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ret = usb_camera.discard_tmp_picture()
hydro_http.send_result(ret)

