import io
import secrets
import uuid
import pyotp
import qrcode
from base64 import b64encode, b64decode

from src.core.config import config


class QrCodeProvider:

    def __init__(self, issuer: str = config.otp.OTP_ISSUER, secret: str = config.otp.OTP_SECRET):
        self.issuer = issuer
        self.secret = secret

        self.totp = pyotp.totp.TOTP(self.secret)

    def create_qr_code(self, email: str) -> bytes:
        qr = qrcode.QRCode()
        uri = self._get_opt_code_uri(email)

        qr.add_data(uri)

        qr.make(fit=True)

        img = qr.make_image(fill_color="black",
                            back_color="white")
        return self._get_bytes(img)

    def check_otp_code(self, code: str) -> bool:
        return self.totp.verify(code)

    def _get_opt_code_uri(self, email: str) -> str:
        uri = self.totp.provisioning_uri(name=email,
                                         issuer_name=self.issuer)
        return uri

    def _get_bytes(self, img) -> bytes:
        f = io.BytesIO()
        img.save(f)
        img_bytes = f.getvalue()

        return img_bytes
