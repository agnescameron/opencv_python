import numpy as np
import cv2
import os
import traceback
import random

# To read image from disk, we use
# cv2.imread function, in below method,
# img = cv2.imread("test_image.png")
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
fgbg.setShadowThreshold(0.1)
print(fgbg.getShadowThreshold())
cap = cv2.VideoCapture('../test_footage/samples/lumiere-clip-walking.mov')

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_array = []
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

print(frame_width, frame_height)
params = cv2.SimpleBlobDetector_Params()
params.filterByInertia = True
params.minInertiaRatio = 0.01
params.maxInertiaRatio = 0.9
params.filterByArea = True
params.minArea = 500
params.filterByCircularity = True
params.minCircularity = 0.01
params.filterByConvexity = True
params.minConvexity = 0.01

detector = cv2.SimpleBlobDetector_create(params)

for i in range(frame_count-4):
	if i%50 == 0:
		print("frame", i)
		colour = [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]
	# print('frame %d of %d', (i, frame_count))
	ret, frame = cap.read()
	mask = fgbg.apply(frame)

	#merge foreground and background
	mask = np.where(mask==255, 0, mask)

	#bring out shadows
	mask = np.where(mask==127, 255, mask)

	mask_inv = cv2.bitwise_not(mask)
	frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# filter the mask, then threshold
	# cv2.fastNlMeansDenoising(mask_inv, mask_inv, 50, 7, 21)
	# filt = cv2.bilateralFilter(mask_inv, 21, 200.0, 8.0)
	filt = cv2.GaussianBlur(mask,(7,7),0)
	ret, thresh = cv2.threshold(filt, 130, 255, cv2.THRESH_BINARY)

	m = np.zeros((frame_height+2, frame_width+2), np.uint8)

	# apply mask to frame
	masked_frame = cv2.bitwise_and(frame_grey, frame_grey, mask=thresh)
	w_masked_frame = np.where(masked_frame==0, 255, masked_frame)
	col_masked_frame = cv2.cvtColor(w_masked_frame, cv2.COLOR_GRAY2BGR)

	#create colour mask
	col_img = np.zeros(frame.shape, frame.dtype)
	col_img[:,:] = (colour[0], colour[1], colour[2])
	col_mask = cv2.bitwise_and(col_img, col_img, mask=thresh)
	bgr_mask = np.where(col_mask < 10, 255, col_mask)

	cv2.addWeighted(bgr_mask, 0.65, col_masked_frame, 0.35, 0, frame)

	frame_array.append(frame)
	cv2.imshow('frame', frame)
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break

cap.release()

print('writing...', fps, frame_width, frame_height, len(frame_array))
out = cv2.VideoWriter('../test_footage/opencv/blobs.avi', cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_width, frame_height))

for i in range(len(frame_array)):
	out.write(np.uint8(255*frame_array[i]))

out.release()

cv2.destroyAllWindows()