import abc


class IQrCodeProvider(abc.ABC):

    @abc.abstractmethod
    def create_qr_code(self, email: str) -> str:
        pass

    @abc.abstractmethod
    def check_otp_code(self, code: str) -> bool:
        pass
