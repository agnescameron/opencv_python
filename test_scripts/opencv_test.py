import numpy as np
import cv2
import sys

# To read image from disk, we use
# cv2.imread function, in below method,
# img = cv2.imread("test_image.png")
fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=1, detectShadows=True)
print(fgbg.getShadowThreshold())
cap = cv2.VideoCapture('living_room.mp4')

while(1):
	ret, frame = cap.read()
	fgmask = fgbg.apply(frame)
	cv2.imshow('frame',fgmask)
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break

cap.release()

cv2.destroyAllWindows()