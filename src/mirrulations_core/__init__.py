import os
from mirrulations_core.mirrulations_logging import logger

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../.config/config.ini')
LOGGER = logger
VERSION = 'v1.3'
