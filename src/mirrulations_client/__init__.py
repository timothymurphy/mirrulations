from mirrulations_core.api_call_manager import APICallManager

from mirrulations_client.server_call_manager import ServerCallManager
from mirrulations_client.client_health_call_manager import ClientHealthCallManager

from mirrulations_core import config

API_KEY = config.read_value('CLIENT', 'API_KEY')
CLIENT_ID = config.read_value('CLIENT', 'CLIENT_ID')
SERVER_ADDRESS = config.read_value('CLIENT', 'SERVER_ADDRESS')

API_MANAGER = APICallManager(API_KEY)
SERVER_MANAGER = ServerCallManager(CLIENT_ID, SERVER_ADDRESS)
CLIENT_HEALTH_MANAGER = ClientHealthCallManager()
