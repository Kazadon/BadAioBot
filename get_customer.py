from docx import Document
from docx.enum.style import WD_STYLE_TYPE

class CostumerFeatures:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.document = Document(filepath)
        self.document.styles.add_style('List Number', WD_STYLE_TYPE.PARAGRAPH)
        self.table = self.document.tables

    # Show all data
    def show_all_features(self):
        data = list()
        for item in self.table:
            for row in item.rows[1::]:
                data.append(f"{row.cells[0].text}:\n{row.cells[1].text}\n")
        return '\n'.join(data)

    # Searching a list of costumers by query    
    def find_costumer_list(self, query: str):
        costumer_list = list()
        for item in self.table:
            for row in item.rows[1::]:
                if row.cells[0].text.lower().find(query.lower()) != -1:
                    costumer_list.append(row.cells[0].text)
        return costumer_list

    # доделать нумерацию текста в ячейках
    # Show quieried costumer feauter
    def get_costumer_feature(self, query: str) -> None:
        for item in self.table:
            for row in item.rows[1::]:
                if row.cells[0].text == query:
                    return row.cells[1].text

# print(CostumerFeatures('customer_features.docx').show_all_features())                    
