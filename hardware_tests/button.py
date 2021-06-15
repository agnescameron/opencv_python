import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

button_in = 19

GPIO.setup(button_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
	if GPIO.input(button_in) == GPIO.HIGH:
		print('button pressed')
	else:
		print('button released')
