from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

class WebScrapper:
    def __init__(self):
        self.driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
        self.data = []

    def load_page(self, url):
        self.driver.get(url)
        self.driver.maximize_window()

    def perform_action(self, action, data_structure):
        wait = WebDriverWait(self.driver, 20)

        if action['action_type'] == 'scroll':
            self.scroll_to_element((getattr(By, action['selector_type']), action['selector_value']))
        elif action['action_type'] == 'fetch_data':
            self.fetch_data_structure(data_structure['selector_type'], data_structure['selector_value'], data_structure['row_selector'], data_structure['columns'])
        else:
            element_selector = (getattr(By, action['selector_type']), action['selector_value'])
            element = wait.until(EC.presence_of_element_located(element_selector))

            if action['action_type'] == 'click':
                element = wait.until(EC.element_to_be_clickable(element_selector))
                element.click()
            elif action['action_type'] == 'send_keys' and 'value' in action:
                element.send_keys(action['value'])
            elif action['action_type'] == 'hover':
                ActionChains(self.driver).move_to_element(element).perform()
            else:
                raise ValueError('Acción no soportada')
        
        time.sleep(5)

    def fetch_data_structure(self, selector_type, selector_value, row_selector, columns):
        try:
            structure_selector = (getattr(By, selector_type), selector_value)
            structure = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(structure_selector))
            rows = structure.find_elements(By.CSS_SELECTOR, row_selector)

            for row in rows:
                row_data = {}
                valid_row = True
                for column_info in columns:
                    column_name = column_info['name']
                    column_selector = column_info['selector']
                    attribute = column_info['attribute']
                    try:
                        cell = row.find_element(By.CSS_SELECTOR, column_selector)
                        if cell:
                            if attribute == 'textContent':
                                cell_value = cell.text.strip()
                            elif attribute == 'title':
                                cell_value = cell.get_attribute('title').strip()
                            else:
                                cell_value = cell.get_attribute(attribute).strip()

                            if cell_value in ['', None]:
                                valid_row = False
                            
                            row_data[column_name] = cell_value

                        else:
                            row_data[column_name] = None
                            valid_row = False

                    except Exception as e:
                        row_data[column_name] = None
                        valid_row = False

                if valid_row:
                    self.data.append(row_data)

        except Exception as e:
            print(f'Error al obtener los datos de la tabla: {e}')

    def scroll_to_element(self, element_selector):
        element = self.driver.find_element(*element_selector)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def get_data(self):
        return self.data
    
    def close(self):
        self.driver.quit()
