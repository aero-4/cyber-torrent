import secrets
import uuid

import qrcode


class QrCodeProvider:

    def create_qr_code(self, data: str = None) -> bytes:
        _random_name = f"{uuid.uuid4()}.png"
        if not data:
            data = self._generate_url_token()

        qr = qrcode.QRCode()
        qr.add_data(data)

        img = qr.make_image()
        return img.save(_random_name)

    def _generate_url_token(self) -> str:
        token = secrets.token_urlsafe(32)
        url = f"http://localhost:8000/api/auth/qr?token={token}"
        return url
