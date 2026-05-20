import os
from pickledb import PickleDB

KEY_SEPARATOR = "_"

def create_database(path_database : str, name_database : str) -> PickleDB :
    """Function to create the database from the specified json file

    Args:
        path_database (str): Path to the database
        name_database (str): Name of the database file

    Returns:
        PickleDB: PickleDB object representing the database
    """
    
    # Build database object for the bot
    os.makedirs(name=path_database, exist_ok=True)
    return PickleDB(os.path.join(path_database, name_database))

async def get_quests_from_user(database : PickleDB,
                               server_id : str,
                               user_id : str) -> list :
    """Function to retrieve the list of all quests of a given user

    Args:
        database (PickleDB): Database to store quest info
        server_id (str): Discord server id where the command comes from
        user_id (str): User id where the command comes from

    Returns:
        list: List of the quests given in a list of dict format 
    """
    
    await database.load()
    
    key = server_id + KEY_SEPARATOR + user_id
    
    list_to_return = await database.get(key, default=[])
    
    return list_to_return

async def get_quests_from_server(database : PickleDB,
                                 server_id : str,
                                 filter_label = None) -> dict:
    """Function to retrieve all quests of a server as a 

    Args:
        database (PickleDB): Database to store quest info
        server_id (str): Discord server id where the command comes from
        filter_label (str, optional): label to filter the dict upon
        
    Returns:
        dict: dict of the quests with their user id as keys
    """
    
    await database.load()
    
    list_keys = await database.all()
    
    users_from_server_keys = [key for key in list_keys if key.split(KEY_SEPARATOR)[0] == server_id]
    users_from_server_keys.sort()
    
    # Retrieve server specific users with non null values
    dict_server_quests = {
            key.split(KEY_SEPARATOR)[1] : await database.get(key, default=[])
            for key in users_from_server_keys if await database.get(key, default=[])
        } 
    
    if filter_label:
        # Keep only quests equal to the quest label
        dict_server_quests = {
            key : [quest for quest in list_quest if quest.get("quest_label") == filter_label] 
            for key, list_quest in dict_server_quests.items() 
            if [quest for quest in list_quest if quest.get("quest_label") == filter_label]
        }
    
    return dict_server_quests
    

async def insert_quest(database : PickleDB,
                 server_id : str,
                 user_id : str,
                 server_name : str,
                 user_name : str,
                 quest_category = "dungeon",
                 quest_label = "",
                 quest_comments = ""):
    """Function to insert a quest in the given database

    Args:
        database (PickleDB): Database to store quest info
        server_id (str): Discord server id where the command comes from
        user_id (str): User id where the command comes from
        server_name (str) : Discord server name where the command comes from
        user_name (str) : User name where the command comes from
        quest_category (str, optional): Category of quest among set values. Defaults to "dungeon".
        quest_label (str, optional): Label of quest. Defaults to "".
        quest_comments (str, optional): User defined comment. Defaults to "".
    """
    
    await database.load()
    
    dict_to_insert = {
        "server_name" : server_name,
        "user_name" : user_name,
        "quest_category" : quest_category,
        "quest_label" : quest_label,
        "quest_comments" : quest_comments
    }
    
    list_quests = await get_quests_from_user(
        database=database,
        server_id=server_id,
        user_id=user_id
    )
    
    list_quests.append(dict_to_insert)
    
    key = server_id + KEY_SEPARATOR + user_id
    await database.set(key, list_quests)
    
    await database.save()
    

async def remove_quest_from_index(database : PickleDB,
                                  server_id : str,
                                  user_id : str,
                                  idx : int) -> int:
    """Function to remove a quest from the user given it's index

    Args:
        database (PickleDB): Database to store quest info
        server_id (str): Discord server id where the command comes from
        user_id (str): User id where the command comes from
        idx (int): Index to remove
    Returns:
        int: Status code 
    """
    
    await database.load()
    
    list_quests = await get_quests_from_user(
        database=database,
        server_id=server_id,
        user_id=user_id
    )
    
    # Handle out of bound list condition
    if idx < len(list_quests):
        del list_quests[idx]
    else:
        return -1
    
    
    key = server_id + "_" + user_id
    await database.set(key, list_quests)
    
    await database.save()
    
    return 0
    
    
    