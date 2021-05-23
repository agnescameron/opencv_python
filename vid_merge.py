import os
import time

#make output path with recording timestamp
timestamp = round(time.time())
output_path = os.path.join('./output/', str(timestamp))
os.mkdir(output_path)

# join video 1
os.system("ffmpeg -f concat -safe 0 -i ./temp/vid_1.txt -c copy " + os.path.join(output_path, "video_1.mp4"))

# join video 2
os.system("ffmpeg -f concat -safe 0 -i ./temp/vid_2.txt -c copy " + os.path.join(output_path, "video_2.mp4"))


