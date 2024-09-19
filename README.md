# intercom proxy

## 1. Installation

install.sh creates virtual environment and install packages from the requirements.txt and execute pytest after that.

## 2. Configuration

You can use environment variables to set Intercom API versions for your clients. Name them with prefix CLIENT_ 
(e.g. CLIENT_clientid=api_version).

Other settings (also through env vars or you can change them directly in app/config.py):
1.     API_PORT: int = 8000
2.     API_HOST: str = '0.0.0.0'
3.     INTERCOM_API_URL: str = 'https://api.intercom.io'
4.     ALLOWED_PREFIX: list = ['/messages', '/contacts', '/conversations', '/version']
4.     DEFAULT_VERSION: str = '1.0'

Each client will use the version selected based on priority from top to bottom:
1. Version from Client-API-Version header
2. Version from service data fetched by client's id from Client-ID header
3. Default version from configuration



3. ## Usage
You can send GET request to /version for receiving current client_id:intercom_api_version mapping.

Also you can change the version by making a PUT request to /version/{client_key} 
with request body {"version": "_your_new_version_"}

All other requests would go through proxy direct to Intercom API with changing the host to INTERCOM_API_URL defined in settings.
If path would not be started by one of the ALLOWED_PREFIX, service would raise 403 HTTP ERROR.