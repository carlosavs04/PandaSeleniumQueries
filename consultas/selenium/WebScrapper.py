from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

class WebScrapper:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.data = []

    def load_page(self, url):
        self.driver.get(url)
        self.driver.maximize_window()

    def search_term(self, search_box_selector, search_button_selector, search_term):
        wait = WebDriverWait(self.driver, 20)
        search_box = wait.until(EC.element_to_be_clickable(search_box_selector))
        search_box.send_keys(search_term)
        search_button = wait.until(EC.element_to_be_clickable(search_button_selector))
        search_button.click()

        time.sleep(5)

    def fetch_data_table(self, table_selector, columns):
        try: 
            table = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(table_selector))
            rows = table.find_elements(By.TAG_NAME, 'tr')

            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) >= len(columns):
                    row_data = {}
                    for column_name, column_index in columns:
                        row_data[column_name] = cells[column_index].text
                    self.data.append(row_data)
        except Exception as e:
            print(f'Error al obtener los datos de la tabla: {e}')

    def export_to_excel(self, file_name):
        df = pd.DataFrame(self.data)
        df.to_excel(file_name, index=False)
        print(f'Archivo {file_name} creado con éxito')
    
    def close(self):
        self.driver.quit()

if __name__ == '__main__':
    scrapper = WebScrapper()

    search_url = 'https://es.wikipedia.org/'
    search_term = 'Copa Mundial de Fútbol'
    search_box_selector = (By.ID, 'searchInput')
    search_button_selector = (By.CLASS_NAME, 'cdx-search-input__end-button')
    table_selector = (By.CSS_SELECTOR, "table[cellspacing='0']")

    colums = [
        ("Año", 0),
        ("Sede", 1),
        ("Campeón", 2),
        ("Resultado", 3),
        ("Subcampeón", 4),
    ]

    try: 
        scrapper.load_page(search_url)
        scrapper.search_term(search_box_selector, search_button_selector, search_term)
        scrapper.fetch_data_table(table_selector, colums)
        scrapper.export_to_excel('copa_mundial.xlsx')
    
    finally: 
        scrapper.close()