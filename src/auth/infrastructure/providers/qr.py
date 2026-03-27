import io
import secrets
import uuid

import qrcode
from base64 import b64encode, b64decode


class QrCodeProvider:

    def create_qr_code(self, data: str = None) -> bytes:
        if not data:
            data = self._generate_url()

        qr = qrcode.QRCode()
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image()
        img_bytes = self._get_bytes(img)

        return img_bytes

    def _generate_url(self) -> str:
        token = secrets.token_urlsafe(32).upper()
        url = f"http://localhost:8000/auth/qr?token={token}"
        print(url)
        return url

    def _get_bytes(self, img) -> bytes:
        f = io.BytesIO()
        img.save(f)
        img_bytes = f.getvalue()

        return img_bytes
