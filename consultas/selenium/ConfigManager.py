import json

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()
    
    def load_config(self):
        with open(self.config_file, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def get_config(self):
        return self.config_data