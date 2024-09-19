import os
from pydantic_settings import BaseSettings


class ProxySettings(BaseSettings):
    API_PORT: int = 8000
    API_HOST: str = '0.0.0.0'
    INTERCOM_API_URL: str = 'https://api.intercom.io'
    DEFAULT_VERSION: str = '1.0'
    ALLOWED_PREFIX: list = ['/messages', '/contacts', '/conversations', '/version']
    CLIENT_VERSION: dict = {}

    class Config:
        env_file = ".env"

    def load_client_version(self):
        self.CLIENT_VERSION = {
            key[len('CLIENT_'):]: value for key, value in os.environ.items() if key.startswith('CLIENT_')
        }
