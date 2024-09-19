import coloredlogs
import logging.config
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LOGGING_LEVEL: str = 'DEBUG'

    @property
    def LOGGING_CONFIG(self):
        fmt = '%(asctime)s.%(msecs)03d [%(levelname)s]|[%(name)s]: %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'

        config = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'colored': {
                    '()': 'coloredlogs.ColoredFormatter',
                    'format': '%(asctime)s (%(levelname)s) %(name)s %(message)s'
                },
                'default': {
                    'format': fmt
                }
            },
            'handlers': {
                'default': {
                    'level': self.LOGGING_LEVEL,
                    'formatter': 'colored',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout'
                },
            },
            'root': {
                'handlers': ['default']
            },
            'loggers': {
                '': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False
                },
                'uvicorn': {
                    'propagate': True
                },
                'uvicorn.access': {
                    'propagate': True
                },
                'uvicorn.error': {
                    'propagate': True
                },
            }
        }
        return config


settings = Settings()


def log_configure(*configs):
    result_config = Settings().LOGGING_CONFIG
    coloredlogs.install()

    for config in configs:
        result_config['formatters'].update(config.get('formatters', {}))
        result_config['handlers'].update(config.get('handlers', {}))
        result_config['loggers'].update(config.get('loggers', {}))

    logging.config.dictConfig(result_config)

    logging.info('Logging configured.')

'''
To send logs to Grafana, you can install the additional library python-logging-loki and add a handler to logger.

handler = logging_loki.LokiHandler(
    url="https://my-loki-instance/loki/api/v1/push", 
    tags={"application": "my-app"},
    auth=("username", "password"),
    version="1",
)
'''