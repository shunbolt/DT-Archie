# DT-Archie

This project implements a Discord bot to handle guild daily quests through several members of a guild for Dofus Touch
The bot can be used to :

- Register daily quests where you need help from other guild / party members
- Check what other members need for their daily quests
- Register yourself as a helper for other mates

The bot has been developped in Python and specifically the discord.py library 

## Table of contents

- [DT-Archie](#dt-archie)

## Install

To install the bot, use the following instructions :

## Usage

You can use the bot with the following commands :

```sh
!ajout_quete <quest_category> <quest_label> <quest_comments> // Add a quest to the user billboard with the corresponding category / label / comments
!lire_quetes // Display the list of quests of the user
!supp_quete <index> // Delete a quest from the list of user quest given it's index on the billboard

```

The arguments to add a quest are :
- quest_category (str, optional): Category of quest among values like "dungeon", "battle", etc... Defaults to "dungeon".
- quest_label (str, optional): Label of quest. For a dungeon, should be the name of the boss. Defaults to "".
- quest_comments (str, optional): User defined comment for additional context to the quests (required success, ...). Defaults to "".

Note : The `!ajout_quete` command will be simplified to only requiring label and comments.

## Authors

Made by Shunbolt 
Discord ID : Shunbolt#1312

## Thanks

## Contributing

## License

This project is under the MIT LICENSE

More on [the LICENSE file](LICENSE)

