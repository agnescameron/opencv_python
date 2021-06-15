import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.D18, 30, brightness=0.1)

pixels.fill((255, 255, 255))
pixels.show()
time.sleep(1)
pixels.fill((0, 0, 0))
pixels.show()
