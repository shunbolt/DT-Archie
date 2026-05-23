import os
import json

SCRIPT_PATH = os.path.dirname(__file__)

PATH_TO_LABEL_FR = os.path.join(SCRIPT_PATH, "FR_label.json")
PATH_TO_CATEGORY_FR = os.path.join(SCRIPT_PATH, "FR_category.json")
PATH_TO_TAG_FR = os.path.join(SCRIPT_PATH, "FR_tag.json")
PATH_TO_HELP_FR = os.path.join(SCRIPT_PATH, "FR_help.txt")
PATH_TO_HELP_SLASH_FR = os.path.join(SCRIPT_PATH, "FR_help_slash.txt")


def read_full_label(lang="FR") -> dict:
    """Read the entire label file

    Args:
        lang (str, optional): Language to use. Defaults to "FR".

    Returns:
        dict: dict of dict contained in the full file
    """
    with open(PATH_TO_LABEL_FR, "r", encoding="utf-8") as file:
        label_data = json.load(file)

    return label_data


def read_label(label: str, lang="FR") -> dict:
    """Read corresponding label and return dict value associated with it

    Args:
        label (str): key label
        lang (str): Language to use. Defaults "FR"
    Returns:
        dict : dict of values from the label. Returns None if not found
    """

    label_data = read_full_label(lang)

    return label_data.get(label)


def read_category(category: str, lang="FR") -> dict:
    """Read corresponding category and return dict label value

    Args:
        category (str): key category
        lang (str): Language to use. Defaults "FR"
    Returns:
        dict : dict value of the category. Returns None if not found
    """

    with open(PATH_TO_CATEGORY_FR, "r", encoding="utf-8") as file:
        category_data = json.load(file)

    return category_data.get(category)


def read_tag(tag: str, lang="FR") -> dict:
    """Read corresponding tag and return dict label value

    Args:
        tag (str): key tag
        lang (str): Language to use. Defaults "FR"
    Returns:
        dict : dict value of the tag. Returns None if not found
    """

    with open(PATH_TO_TAG_FR, "r", encoding="utf-8") as file:
        tag_data = json.load(file)

    return tag_data.get(tag)


def read_help(lang="FR", help_type=None) -> str:
    """Read the content of the help file

    Args:
        lang (str, optional): Language to use. Defaults to "FR".
        help_type (str, optional): Type of help. Defaults to prefix commands.

    Returns:
        str: Help content
    """

    if help_type == "/":
        with open(PATH_TO_HELP_SLASH_FR, "r", encoding="utf-8") as file:
            help_content = file.read()
    else:
        with open(PATH_TO_HELP_FR, "r", encoding="utf-8") as file:
            help_content = file.read()

    return help_content
