from glob import glob
import os

# clean up temp files
os.remove('./temp/video.h264')
os.remove('./temp/video.mp4')
# os.remove('./temp/*.avi')

for f in glob ('./temp/*.avi'):
   os.remove(f)


open('./temp/vid_1.txt', 'w').close()
open('./temp/vid_2.txt', 'w').close()
