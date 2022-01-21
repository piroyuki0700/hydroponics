#!/usr/bin/python3
#
# RaspberryPIの操作
#
import sys
import json
import RPi.GPIO as GPIO
import adafruit_dht
from board import *
import smbus
import time
import re
from decimal import *
from gpiozero import LED
from datetime import datetime

#AD/DAモジュール設定
address = 0x48
A0 = 0x40
A1 = 0x41
A2 = 0x42
A3 = 0x43

# GPIO.BCM番号
#gpio_led = [35,36,37,38]
gpio_led = [19,16,26,20]
gpio_dht11 = D18	# 12番のBCM GPIO番号
gpio_ds18 = 4
gpio_pump = 17

gpio_trig = 23
gpio_echo = 24
MAX_DISTANCE = 220
timeOut = MAX_DISTANCE*60
WATER_LEVEL_MAX = 29
WATER_LEVEL_FULL = 20

SYSFILE_DS18B20 = '/sys/bus/w1/devices/28-01204c43b99b/w1_slave'
RETRY_TDS_MAX = 5
RETRY_TDS_DELAY = 0.5
RETRY_DISTANCE_MAX = 30
RETRY_DISTANCE_DELAY = 0.5

gpio_subp_relay = 5
gpio_subp_level = 6

#
# ポンプ動作開始
#
def pump_start():
#	GPIO.setmode(GPIO.BOARD)
	timestr = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	print(f'  {timestr} pump_start', file=sys.stderr)
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(gpio_pump, GPIO.OUT)
	GPIO.output(gpio_pump, GPIO.HIGH)
	return True

#
# ポンプ動作停止
#
def pump_stop():
#	GPIO.setmode(GPIO.BOARD)
	timestr = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	print(f'  {timestr} pump_stop', file=sys.stderr)
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(gpio_pump, GPIO.OUT)
	GPIO.output(gpio_pump, GPIO.LOW)
	return True

#
# センサー値の取得
#
def measure_temp_humid():
	dht11 = adafruit_dht.DHT11(gpio_dht11, use_pulseio=False)
	temperature = dht11.temperature
	humidity = dht11.humidity
	result = {}
	result['air_temp'] = float(f"{temperature:.1f}")
	result['humidity'] = float(f"{humidity:.1f}")
	return result

def measure_water_temp():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(gpio_ds18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	result = {}
	try:
		with open(SYSFILE_DS18B20, mode='r') as f:
			striped = [line.strip() for line in f.readlines()]
			f.close()
			if 'YES' in striped[0]:
				values = re.findall(r't=([0-9]+)', striped[1])
				water_temp = int(values[0]) / 1000
				result['water_temp'] = float(f"{water_temp:.1f}")
			return result

	except Exception as e:
		print(e, file=sys.stderr)
		return result

def pulseIn(pin,level,timeOut):
	t0 = time.time()
	while(GPIO.input(pin) != level):
		if((time.time() - t0) > timeOut * 0.000001):
			return 0;
	t0 = time.time()
	while(GPIO.input(pin) == level):
		if((time.time() - t0) > timeOut * 0.000001):
			return 0;
	pulseTime = (time.time() - t0) * 1000000
	return pulseTime

def getSonar():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(gpio_trig, GPIO.OUT)
	GPIO.setup(gpio_echo, GPIO.IN)
	GPIO.output(gpio_trig, GPIO.HIGH)
	time.sleep(0.00001)
	GPIO.output(gpio_trig, GPIO.LOW)
	pingTime = pulseIn(gpio_echo, GPIO.HIGH, timeOut)
	distance = pingTime * 340.0 / 2.0 / 10000.0
	return distance

def measure_water_level():

	for i in range(RETRY_DISTANCE_MAX):
		distance = getSonar()
#		print(distance, file=sys.stderr)
		if 0 != distance and distance < 100:
			break;
		time.sleep(RETRY_DISTANCE_DELAY)

	# %を計算（0～100に制限）
	water_level = int((WATER_LEVEL_MAX - distance) * 100 / WATER_LEVEL_FULL)
	water_level = min(100, max(water_level, 0))
	result = {}
	result['distance'] = float(f"{distance:.1f}")
	result['water_level'] = water_level
	return result

def measure_tds(temperature):
	AREF = 5
	ADCRANGE = 256
	KVALUE = 1.0274
	bus = smbus.SMBus(1)
	bus.write_byte(address,A2)

	for i in range(RETRY_TDS_MAX):
		value = bus.read_byte(address)
#		print(value, file=sys.stderr)
		if 0 < value and value < 100:
			break;
		time.sleep(RETRY_TDS_DELAY)

	voltage = value * AREF / ADCRANGE
	ecValue = (133.42*voltage**3 - 255.86*voltage**2 + 857.39*voltage) * KVALUE
#	print(ecValue, file=sys.stderr)
	ecValue25 = ecValue / (1.0+0.02*(temperature-25.0))
#	print(ecValue25, file=sys.stderr)
#	print(1413/ecValue25, file=sys.stderr)
	ecResult = ecValue25 / 1000
	result = {}
	result['voltage'] = float(f"{voltage:.2f}")
	result['tds_level'] = float(f"{ecResult:.2f}")
	return result

def measure_brightness():
	bus = smbus.SMBus(1)
	bus.write_byte(address,A0)
	value = bus.read_byte(address)
	time.sleep(0.1)
	value = bus.read_byte(address)	# 2回読まないとあまり変化しない
	bus.close()
	result = {}
	result['brightness'] = 255 - value
	return result

def measure_sensor(num):
	if num == 0:
		return measure_temp_humid()
	elif num == 1:
		return measure_water_temp()
	elif num == 2:
		return measure_water_level()
	elif num == 3:
		result = measure_water_temp()
		return measure_tds(result['water_temp'])
	elif num == 4:
		return measure_brightness()
	else:
		return {}

#
# 全センサー値の取得
#
def measure_sensors_internal():
	result = {}
	dic = measure_temp_humid()
	result.update(dic)
	dic = measure_water_temp()
	result.update(dic)
	dic = measure_water_level()
	result.update(dic)
	dic = measure_tds(result['water_temp'])
	result.update(dic)
	dic = measure_brightness()
	result.update(dic)
	return result

def measure_sensors():
	result = {}
	# exception時のリトライは合計5回まで。
	for i in range(5):
		try:
			result = measure_sensors_internal();
		except Exception as e:
			print(e, file=sys.stderr)
		if len(result) != 0:
			break
	return result

#
# LED ON/OFF
#   num 0:青 1:緑 2:黄 3:赤
#
def set_led(num, state):
	output = GPIO.HIGH if state == "on" else GPIO.LOW
#	GPIO.setmode(GPIO.BOARD)
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(gpio_led[num], GPIO.OUT)
#	print(f'{gpio_led[num]}', file=sys.stderr);
	GPIO.output(gpio_led[num], output)
#	GPIO.cleanup();
	return True

def update_led(color):
	leds = {'blue': 0, 'green': 1, 'yellow': 2, 'red': 3}
	for key, value in leds.items():
		if color == key:
			set_led(value, 'on')
		else:
			set_led(value, 'off')

#
# サブポンプ動作開始
#
def sub_pump_start():
	timestr = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	print(f'  {timestr} sub_pump_start', file=sys.stderr)
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(gpio_subp_relay, GPIO.OUT)
	GPIO.output(gpio_subp_relay, GPIO.HIGH)
	return True

#
# サブポンプ動作停止
#
def sub_pump_stop():
	timestr = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	print(f'  {timestr} sub_pump_stop', file=sys.stderr)
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(gpio_subp_relay, GPIO.OUT)
	GPIO.output(gpio_subp_relay, GPIO.LOW)
	return True

#
# サブタンクの水の状態確認
#
def sub_level_check():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(gpio_subp_level, GPIO.IN)
	reading = GPIO.input(gpio_subp_level)
	result = False
	if reading == GPIO.HIGH:
		result = True
	return result

#
# サブタンクの水終了コールバック登録
#
def sub_pump_set_end_cb(sub_pump_end):
	GPIO.add_event_detect(gpio_subp_level, GPIO.FALLING, sub_pump_end, 1000)
	pass

