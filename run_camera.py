import numpy as np
import cv2
import random
import picamera
import subprocess
import RPi.GPIO as GPIO
import time
import os
from glob import glob
import board
import neopixel

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 10
GPIO.setmode(GPIO.BCM)
pixels = neopixel.NeoPixel(board.D18, 12, brightness=0.9)

#setup LEDs
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
GPIO.output(green_led, GPIO.LOW)

def record_and_write():
	GPIO.output(green_led, GPIO.HIGH)
	GPIO.output(yellow_led, GPIO.LOW)

	try:
		os.remove('./temp/video.h264')
	except OSError:
		pass

	try:
		os.remove('./temp/video.mp4')
	except OSError:
		pass

	open('./temp/vid_1.txt', 'w').close()
	open('./temp/vid_2.txt', 'w').close()

	for f in glob ('./temp/*.avi'):
	   os.remove(f)

	#make output path with recording timestamp
	timestamp = round(time.time())
	output_path = os.path.join('./output/', str(timestamp))
	os.mkdir(output_path)

	print("started recording")
	pixels.fill((255, 255, 255))
	pixels.show()
	camera.start_recording('./temp/video.h264')
	camera.wait_recording(1)

	while True:
	    camera.wait_recording(0.05)
	    if GPIO.input(button_in) == GPIO.HIGH:
	        break

	print("finished filming")
	pixels.fill((0, 0, 0))
	pixels.show()

	GPIO.output(yellow_led, GPIO.HIGH)
	GPIO.output(red_led, GPIO.LOW)

	camera.stop_recording()
	command = "MP4Box -add ./temp/video.h264 ./temp/video.mp4"
	subprocess.call([command], shell=True)

	#copy the output video to the folder
	command2 = "cp ./temp/video.mp4 ./output/video_orig.mp4"
	subprocess.call([command2], shell=True)

	print("written recording, now converting frames")

	shadow_threshold = 0.5
	filter_size = (9,9)
	filter_threshold = 105

	# To read image from disk, we use
	# cv2.imread function, in below method,
	# img = cv2.imread("test_image.png")
	fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
	fgbg.setShadowThreshold(shadow_threshold)
	print(fgbg.getShadowThreshold())

	cap = cv2.VideoCapture('./temp/video.mp4')

	frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	fps = int(cap.get(cv2.CAP_PROP_FPS))

	# separate films
	frame_array_1 = []
	frame_array_2 = []

	frame_width = int(cap.get(3))
	frame_height = int(cap.get(4))

	clip_count = 0

	for i in range(frame_count-4):
		if i%50 == 0:
			print("frame", i, "of", frame_count)
			colour = [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]

		GPIO.output(red_led, GPIO.HIGH)
		time.sleep(0.2)
		GPIO.output(red_led, GPIO.LOW)

		ret, frame = cap.read()
		mask_raw = fgbg.apply(frame)

		#merge foreground and background
		mask = np.where(mask_raw==255, 0, mask_raw)

		#bring out shadows
		mask = np.where(mask==127, 255, mask)

		mask_inv = cv2.bitwise_not(mask)
		frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# filter the mask, then threshold
		filt = cv2.GaussianBlur(mask,filter_size,0)
		ret, thresh = cv2.threshold(filt, filter_threshold, 255, cv2.THRESH_BINARY)

		m = np.zeros((frame_height+2, frame_width+2), np.uint8)

		contours, hierarchy = cv2.findContours(cv2.bitwise_not(thresh), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cv2.drawContours(thresh, contours, -1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
		dilated = cv2.dilate(thresh, kernel)
		thresh=cv2.erode(dilated,kernel)

		cv2.floodFill(thresh, m, (0,0), 255)
		frame_cont = frame

		# apply mask to frame
		masked_frame = cv2.bitwise_and(frame_grey, frame_grey, mask=cv2.bitwise_not(thresh))
		w_masked_frame = np.where(masked_frame==0, 255, masked_frame)
		col_masked_frame = cv2.cvtColor(w_masked_frame, cv2.COLOR_GRAY2BGR)

		#create colour mask
		col_img = np.zeros(frame.shape, frame.dtype)
		col_img[:,:] = (colour[0], colour[1], colour[2])
		col_mask_1 = cv2.bitwise_and(col_img, col_img, mask=cv2.bitwise_not(thresh))
		bgr_mask_1 = np.where(col_mask_1 < 10, 255, col_mask_1)

		frame_1 = cv2.addWeighted(bgr_mask_1, 0.4, col_masked_frame, 0.6, 0)
		frame_array_1.append(frame_1)

		col_mask_2 = cv2.bitwise_and(col_img, col_img, mask=thresh)
		bgr_mask_2 = np.where(col_mask_2 < 10, 255, col_mask_2)

		frame_2 = cv2.addWeighted(bgr_mask_2, 0.4, col_masked_frame, 0.6, 0)
		frame_array_2.append(frame_2)

		if i%100 == 0 and i != 0:
			print('writing video out, wait a sec...')

			#write out clip in style 1
			out_1 = cv2.VideoWriter(os.path.join('./temp/', 'video_1_' + str(clip_count) 
				+ '.avi'),cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_width, frame_height))

			for j in range(len(frame_array_1)):
				out_1.write(frame_array_1[j])

			out_1.release()

			with open('./temp/vid_1.txt', 'a') as file:
			        file.write(f"file 'video_1_{str(clip_count)}.avi'\n")

			# write out clip in style 2
			out_2 = cv2.VideoWriter(os.path.join('./temp/', 'video_2_' + str(clip_count) 
				+ '.avi'),cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_width, frame_height))

			for j in range(len(frame_array_2)):
				out_2.write(frame_array_2[j])

			out_2.release()

			with open('./temp/vid_2.txt', 'a') as file:
			        file.write(f"file 'video_2_{str(clip_count)}.avi'\n")

			frame_array_1 = []
			frame_array_2 = []
			clip_count = clip_count + 1

	cap.release()

	#write out remaining videos
	out_1 = cv2.VideoWriter(os.path.join('./temp/', 'video_1_' + str(clip_count) 
		+ '.avi'),cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_width, frame_height))

	for j in range(len(frame_array_1)):
		out_1.write(frame_array_1[j])

	with open('./temp/vid_1.txt', 'a') as file:
		file.write(f"file 'video_1_{str(clip_count)}.avi'")

	out_1.release()

	out_2 = cv2.VideoWriter(os.path.join('./temp/', 'video_2_' + str(clip_count) 
		+ '.avi'),cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_width, frame_height))

	for j in range(len(frame_array_2)):
		out_2.write(frame_array_2[j])

	with open('./temp/vid_2.txt', 'a') as file:
		file.write(f"file 'video_2_{str(clip_count)}.avi'")

	out_2.release()

	cv2.destroyAllWindows()

	print('merging clips, cleaning up...')

	# join video 1
	subprocess.call(["ffmpeg -f concat -safe 0 -i ./temp/vid_1.txt -c copy " + os.path.join(output_path, "video_1.mp4")], 
		stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)

	# join video 2
	subprocess.call(["ffmpeg -f concat -safe 0 -i ./temp/vid_2.txt -c copy " + os.path.join(output_path, "video_2.mp4")], 
		stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)

	print("output is in", output_path)
	GPIO.output(red_led, GPIO.HIGH)

if __name__ == "__main__":
	run_count = 0
	while True:
		if GPIO.input(button_in) == GPIO.HIGH:
			try:
				record_and_write()
				GPIO.output(green_led, GPIO.LOW)
				run_count = run_count + 1
				print("ready to record, run count is", run_count)
			except Exception as e:
				print("hit exception, cleaning up")
				GPIO.cleanup()
				pixels.fill((0, 0, 0))
				pixels.show()
				sys.exit(1)
	GPIO.cleanup()
