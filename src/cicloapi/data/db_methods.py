# db_methods.py

from cicloapi.core.config import settings
import json
import os

current_working_directory = os.getcwd()
def save_users_db():
    """
    Saves the user database to disk.
    """
    TEMP_DB = settings.USERS_DB.copy()
    for key in TEMP_DB.keys():
        TEMP_DB[key]["hashed_password"] = TEMP_DB[key]["hashed_password"].decode()

    with open(current_working_directory, 'src', 'cicloapi', 'data', 'users_db_fake.json', "w") as outfile:
        json.dump(TEMP_DB, outfile)
