import pyqrcode

qr = pyqrcode.create("HORN O.K. PLEASE.")
qr.png("horn.png", scale=6)

from qrtools import qrtools

qr2 = qrtools.QR()
qr2.decode("horn.png")
print(qr.data)
