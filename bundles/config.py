from yaml import load


class Config(dict):
    def __init__(self):
        super().__init__()
        self.config = load(open("config/config.yml"))

    def __getitem__(self, attr):
        return self.config[attr]
