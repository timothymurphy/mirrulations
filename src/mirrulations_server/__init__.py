from flask import Flask
import fakeredis

from mirrulations_core.api_call_manager import APICallManager
from mirrulations_server.redis_manager import RedisManager

from mirrulations_core import config

API_KEY = config.read_value('SERVER', 'API_KEY')

FLASK_APP = Flask(__name__)

API_MANAGER = APICallManager(API_KEY)
REDIS_MANAGER = RedisManager(fakeredis.FakeRedis())
