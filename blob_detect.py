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


	# find edges of shapes in image
	#img_mop = cv2.morphologyEx(filt, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
	#img_mop = cv2.morphologyEx(filt, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
	# img_mop = cv2.morphologyEx(img_mop, cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)))
	ret, thresh = cv2.threshold(filt, 130, 255, cv2.THRESH_BINARY)
	# contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	# cv2.drawContours(thresh, contours, -1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
	# edges = cv2.Canny(thresh,100,200)
	# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
	# dilated = cv2.dilate(edges, kernel)
	# eroded=cv2.erode(dilated,kernel)

	m = np.zeros((frame_height+2, frame_width+2), np.uint8)
	# cv2.floodFill(thresh, m, (0,0), 255)
	# bw_mask = cv2.bitwise_not(thresh)

	# apply mask to frame
	masked_frame = cv2.bitwise_and(frame_grey, frame_grey, mask=thresh)
	w_masked_frame = np.where(masked_frame==0, 255, masked_frame)
	col_masked_frame = cv2.cvtColor(w_masked_frame, cv2.COLOR_GRAY2BGR)

	col_img = np.zeros(frame.shape, frame.dtype)
	col_img[:,:] = (colour[0], colour[1], colour[2])
	col_mask = cv2.bitwise_and(col_img, col_img, mask=thresh)
	bgr_mask = np.where(col_mask < 10, 255, col_mask)

	cv2.addWeighted(bgr_mask, 0.65, col_masked_frame, 0.35, 0, frame)

	#col_mask[np.where((col_mask==[0,0,0]).all(axis=2))] = [255,255,255]

	# keypoints = detector.detect(bgr_mask)
	# im_with_keypoints = cv2.drawKeypoints(bgr_mask, keypoints, np.array([]), (0,0,255), 
	# 	cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	# cv2.addWeighted(bgr_mask, 0.65, frame_grey, 0.35, 0, image)
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