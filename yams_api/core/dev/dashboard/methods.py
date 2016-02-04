# given a user_id, load a dashboard from the DB
import json
from yams_api.core.dev.dashboard import models

def get_dashboard(user_id=None):
    return