import logging
import httpx
import uvicorn as uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel

from app.config import ProxySettings
from app.log import log_configure


settings = ProxySettings()
settings.load_client_version()
log_config = log_configure()
app = FastAPI(title='proxy_intercom')
logger = logging.getLogger('proxy')


class ClientVersionUpdate(BaseModel):
    version: str


@app.middleware("http")
async def restrict_routes(request: Request, call_next):
    if not any(request.url.path.startswith(prefix) for prefix in settings.ALLOWED_PREFIX):
        return Response(status_code=403, content="Access denied")

    response = await call_next(request)
    return response


@app.put("/version/{client_key}")
async def update_client_version(client_key: str, update: ClientVersionUpdate):
    logger.info(f'changing intercom version to {update.version} for client {client_key}')
    settings.CLIENT_VERSION[client_key] = update.version
    return {"message": f"Client {client_key} version updated", "client_version": settings.CLIENT_VERSION[client_key]}


@app.get("/version")
async def get_client_version():
    return settings.CLIENT_VERSION


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_base(request: Request, path: str):
    client_id = request.headers.get("Client-ID")
    logger.info(f'request to {path} from client {client_id}')
    version = request.headers.get("Client-API-Version")
    if not version:
        if not client_id or client_id not in settings.CLIENT_VERSION:
            logger.warning('intercom version not found, using default version')
        version = settings.CLIENT_VERSION.get(client_id, settings.DEFAULT_VERSION)
    headers = {**request.headers, "Intercom-Version": version}
    logger.debug(headers)
    if "Client-API-Version" in headers.keys():
        headers.pop("Client-API-Version")
    if "Client-ID" in headers.keys():
        headers.pop("Client-ID")

    async with httpx.AsyncClient() as client:
        url = f"{settings.INTERCOM_API_URL}/{path}"
        request_body = await request.body()
        try:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=request_body,
                params=request.query_params
            )
            if resp.status_code == 429:
                logger.warning(f'rate limit exceeded for client {client_id}')
                # additional logic for rate limiting goes here
                return Response(content=f'Rate limit exceeded for client {client_id}',
                                status_code=resp.status_code, headers=resp.headers)
            resp.raise_for_status()
        except httpx.RequestError as ex:
            logger.error(f'An error occured while requesting {ex.request.url}')
            return Response(content='request error', status_code=400)
        except httpx.HTTPStatusError as ex:
            logger.error(f"Error response {ex.response.status_code} while requesting {ex.request.url}.")
    return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)


if __name__ == '__main__':
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT, log_config=log_config)
