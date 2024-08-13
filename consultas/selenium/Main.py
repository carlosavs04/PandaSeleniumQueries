from ConfigManager import ConfigManager
from WebScrapper import WebScrapper
from ExcelExporter import ExcelExporter
import os

def main(config_file):
   config_manager = ConfigManager(config_file)
   config = config_manager.get_config()
   
   scrapper = WebScrapper()

   try:
       scrapper.load_page(config['search_url'])

       for action in config['actions']:
           scrapper.perform_action(action, config['data_structure'])
           
           if config.get('specialized_flow', False) and action['action_type'] == 'fetch_data':
               file_suffix = action.get('file_suffix', 'default')
               specialized_output_file = config['output_file'].replace('.xlsx', f'_{file_suffix}.xlsx')
               data = scrapper.get_data()
               print(f'Datos extraídos: {data}')
               exporter = ExcelExporter(data)
               exporter.export_to_excel(specialized_output_file)
               scrapper.data = []
               
       if not config.get('specialized_flow', False):
           data = scrapper.get_data()
           print(f'Datos extraídos: {data}')
           exporter = ExcelExporter(data)
           exporter.export_to_excel(config['output_file'])

   finally:
       scrapper.close()

if __name__ == '__main__':
    #config_file = os.path.join(os.path.dirname(__file__), 'json/milan.json')
    #config_file = os.path.join(os.path.dirname(__file__), 'json/world-cup.json')
    #config_file = os.path.join(os.path.dirname(__file__), 'json/videogames.json')
    config_file = os.path.join(os.path.dirname(__file__), 'json/weather.json')

    main(config_file)