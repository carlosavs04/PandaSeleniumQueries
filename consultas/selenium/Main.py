from ConfigManager import ConfigManager
from WebScrapper import WebScrapper
from ExcelExporter import ExcelExporter
from selenium.webdriver.common.by import By
import os, time

def main(config_file):
   config_manager = ConfigManager(config_file)
   config = config_manager.get_config()
   
   scrapper = WebScrapper()

   try:
       scrapper.load_page(config['search_url'])

       for action in config['actions']:
           scrapper.perform_action(action, config['data_structure'])
               
       data = scrapper.get_data()

       print(f'Datos extraídos: {data}')
       exporter = ExcelExporter(data)
       exporter.export_to_excel(config['output_file'])

   finally:
       scrapper.close()

if __name__ == '__main__':
    #config_file = os.path.join(os.path.dirname(__file__), 'json/milan.json')
    #config_file = os.path.join(os.path.dirname(__file__), 'json/world-cup.json')
    config_file = os.path.join(os.path.dirname(__file__), 'json/videogames.json')

    main(config_file)