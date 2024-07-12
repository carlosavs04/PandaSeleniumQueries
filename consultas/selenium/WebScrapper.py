from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class WebScrapper:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.data = []

    def load_page(self, url):
        self.driver.get(url)
        self.driver.maximize_window()

    def perform_action(self, element_selector, action_type, value=None):
        wait = WebDriverWait(self.driver, 20)
        element = wait.until(EC.element_to_be_clickable(element_selector))

        if action_type == 'click':
            element.click()
        elif action_type == 'send_keys' and value:
            element.send_keys(value)
        else:
            raise ValueError('Acción no soportada')
        
        time.sleep(5)

    def fetch_data_structure(self, structure_selector, row_selector, columns):
        try: 
            structure = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(structure_selector))
            rows = structure.find_elements(By.CSS_SELECTOR, row_selector)

            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td') if row_selector == 'tr' else row.find_elements(By.TAG_NAME, 'div')
                if len(cells) >= len(columns):
                    row_data = {}
                    for column_name, column_index in columns:
                        row_data[column_name] = cells[column_index].text
                    self.data.append(row_data)
        except Exception as e:
            print(f'Error al obtener los datos de la tabla: {e}')

    def get_data(self):
        return self.data
    
    def close(self):
        self.driver.quit()