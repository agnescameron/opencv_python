import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
red_led = 13
yellow_led = 6
green_led = 5
button_in = 19


GPIO.setup(button_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(yellow_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)

GPIO.output(red_led, GPIO.HIGH)
GPIO.output(yellow_led, GPIO.HIGH)
GPIO.output(green_led, GPIO.HIGH)


GPIO.output(green_led, GPIO.LOW)
time.sleep(1)
GPIO.output(green_led, GPIO.HIGH)
GPIO.output(yellow_led, GPIO.LOW)
time.sleep(1)
GPIO.output(yellow_led, GPIO.HIGH)
GPIO.output(red_led, GPIO.LOW)
time.sleep(1)
GPIO.output(red_led, GPIO.HIGH)
