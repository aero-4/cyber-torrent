import cv2
import numpy
import deqr

image_data = cv2.imread("horn.png")

decoder = deqr.QRdecDecoder()

decoded_codes = decoder.decode(image_data)

print(decoded_codes)