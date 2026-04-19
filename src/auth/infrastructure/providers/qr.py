import uuid
import pyotp
import qrcode

from src.auth.domain.interfaces.qrcode import IQrCodeProvider
from src.core.config import config


class QrCodeProvider(IQrCodeProvider):

    def __init__(self, issuer: str = config.otp.OTP_ISSUER):
        self.qr = None
        self.totp = None
        self.issuer = issuer


    def create_qr_code(self, email: str, secret: str) -> str:
        self.totp = pyotp.TOTP(secret)
        self.qr = qrcode.QRCode()

        uri = self._get_opt_code_uri(email)

        self.qr.add_data(uri)
        self.qr.make(fit=True)

        return self._image()

    def check_otp_code(self, code: str, secret: str) -> bool:
        self.totp = pyotp.TOTP(secret)
        return self.totp.verify(code)

    def _get_opt_code_uri(self, email: str) -> str:
        return self.totp.provisioning_uri(name=email,
                                          issuer_name=self.issuer)

    def _image(self):
        file_path: str = f"static/qr/photo_{uuid.uuid4()}.jpeg"
        img = self.qr.make_image(fill_color="black",
                                 back_color="white")
        img.save(file_path)
        return file_path
