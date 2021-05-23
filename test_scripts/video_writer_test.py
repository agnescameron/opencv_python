import numpy as np
import cv2
import os

# To read image from disk, we use
# cv2.imread function, in below method,
# img = cv2.imread("test_image.png")
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
print(fgbg.getShadowThreshold())
cap = cv2.VideoCapture('../test_footage/samples/cherry-blossom-trim.mov')

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_array = []
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

print(frame_width, frame_height)

for i in range(frame_count-4):
	print('frame %d of %d', (i, frame_count))
	ret, frame = cap.read()
	mask = fgbg.apply(frame)
	frame_inv = cv2.bitwise_not(frame)
	mask_inv = cv2.bitwise_not(mask)
	masked_frame_inv = cv2.bitwise_and(frame_inv, frame_inv, mask = mask_inv)
	masked_frame = cv2.bitwise_not(masked_frame_inv)
	cv2.imshow('frame', mask)
	frame_array.append(masked_frame)
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break

cap.release()

print('writing...')
out = cv2.VideoWriter('../test_footage/opencv/check.avi',cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_width, frame_height))
for i in range(len(frame_array)):
	out.write(frame_array[i])

out.release()

cv2.destroyAllWindows()