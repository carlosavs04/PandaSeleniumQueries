import pandas as pd

class ExcelExporter:
    def __init__(self, data):
        self.data = data

    def export_to_excel(self, file_name):
        df = pd.DataFrame(self.data)
        df.to_excel(file_name, index=False)
        print(f'Archivo {file_name} creado con éxito')