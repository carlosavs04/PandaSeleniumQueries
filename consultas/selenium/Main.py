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
           selector = (getattr(By, action['selector_type']), action['selector_value'])
           scrapper.perform_action(selector, action['action_type'], action.get('value'))

       time.sleep(5)

       structure_selector = (getattr(By, config['data_structure']['selector_type']), config['data_structure']['selector_value'])
       row_selector = config['data_structure']['row_selector']

       columns = []
       for col in config['data_structure']['columns']:
           columns.append({
               'name': col['name'],
               'selector': col['selector'],
               'attribute': col['attribute']
           })

       scrapper.fetch_data_structure(structure_selector, row_selector, columns)

       if 'post_data_actions' in config:
           for action in config['post_data_actions']:
               selector = (getattr(By, action['selector_type']), action['selector_value'])
               scrapper.perform_action(selector, action['action_type'], action.get('value'))
               scrapper.fetch_data_structure(structure_selector, row_selector, columns)
               
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