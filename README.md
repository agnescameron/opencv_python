# OpenCV Shadow Camera

This repository contains the code, hardware and software tests, and systemd service file to create a shadow camera on Raspberry Pi OS, running on a Raspberry Pi Zero. It should be compatible with the latest version of Raspberry Pi OS.

In order to install and run this code, you will need to install the Python packages in the conda environment file. I've used Anaconda to manage packages, but pip is also fine if that's preferred. To get the pi ready to use, you will also need to install ffmpeg.

## Software tests

These are in `test_scripts`. 

## Hard tests

These are in `hardware_tests`.

## Main code

The file that runs the shadow camera is in `run_camera.py`. The code listens for input from the button. When the button is pressed, the camera will record, until the button is pressed a second time, at which point the recording is stopped and the video is processed. So as to not lose everything in case of an issue in the code, the video is processed in a series of 100-clip chunks, then stitched together at the end.
