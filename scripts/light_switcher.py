import sys
import os

import RPi.GPIO as GPIO

def switch_light(configuration, state):
	GPIO.setmode(GPIO.BCM)
	print(configuration)
	for light_name in configuration.keys():
		pin = configuration[light_name]
		print(pin)
		GPIO.setup(pin, GPIO.OUT)
		if state == 'on':
			GPIO.output(pin, GPIO.HIGH)
		elif state == 'off':
			GPIO.output(pin, GPIO.LOW)
		print("Pin %d in %s\n" % (pin, state))
	
