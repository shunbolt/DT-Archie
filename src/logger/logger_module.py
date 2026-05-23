import os
import logging


def create_logger(
    path_logfile: str, name_logfile: str, mode="w"
) -> logging.FileHandler:
    """Function to create logger for the bot

    Args:
        path_logfile (str): Path to the log file
        mode (str, optional): Writing mode. Defaults to 'w'.

    Returns:
        logging.FileHandler: Filehandler for logging purposes
    """

    # Build logger output from the bot
    os.makedirs(name=path_logfile, exist_ok=True)
    return logging.FileHandler(
        filename=os.path.join(path_logfile, name_logfile), mode=mode
    )
