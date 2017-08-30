import pyqrcode
qr = pyqrcode.create("HORN O.K. PLEASE.")
qr.png("horn.png", scale=6)

from qrtools import QR
myCode = QR("horn.png")
# myCode = QR(filename=u"/home/psutton/Documents/Python/qrcodes/qrcode.png")
if myCode.decode():
    print(myCode.data)
    print(myCode.data_type)
    print(myCode.data_to_string())