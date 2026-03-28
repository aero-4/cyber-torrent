from src.auth.infrastructure.providers.qr import QrCodeProvider


async def generate_qr_code() -> bytes:
    qr_provider = QrCodeProvider()

    qr_data = qr_provider.create_qr_code()
    return qr_data


async def authenticate_with_qr(token: str):
    pass
