# fake_db.py

import json
import os
# Class that loads the fake user database (to be deprecated soon)


class Database:
    def __init__(self, db_route: str):
        self.db_route = db_route
        self.db = self.load_db()

        for key in self.db.keys():
            self.db[key]["hashed_password"] = self.db[key]["hashed_password"].encode()

    def load_db(self):
        with open(self.db_route, "r") as file:
            data = file.read()
            return json.loads(data)


current_working_directory = os.getcwd()
file_path = os.path.join(current_working_directory, 'src', 'cicloapi', 'data', 'users_db_fake.json')
db_ob = Database(file_path)

users_db = db_ob.db
