import json

PATH_TO_LABEL_FR = "FR_label.json"
PATH_TO_CATEGORY_FR = "FR_category.json"

def read_label(label : str, lang = "FR") -> dict:
    """Read corresponding label and return dict value associated with it

    Args:
        label (str): key label
        lang (str): Language to use. Defaults "FR"
    """
    
    with open(PATH_TO_LABEL_FR, 'r', encoding='utf-8') as file:
        label_data = json.load(file)
        
    return label_data.get(label)
    
def read_category(category : str, lang = "FR") -> str:
    """Read corresponding category and return string label value

    Args:
        category (str): key category
        lang (str): Language to use. Defaults "FR"
    """
    
    with open(PATH_TO_CATEGORY_FR, 'r', encoding='utf-8') as file:
        category_data = json.load(file)
        
    return category_data.get(category)