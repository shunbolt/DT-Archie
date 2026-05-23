# DT-Archie

This project implements a Discord bot to handle guild daily quests through several members of a guild for Dofus Touch

The bot can be used to :

- Register daily quests where you need help from other guild / party members
- Check what other members need for their daily quests
- Register yourself as a helper for other mates

The bot has been developped in Python and specifically with the discord.py library 

## Table of contents

- [DT-Archie](#dt-archie)
  - [Table of contents](#table-of-contents)
  - [Install](#install)
  - [Usage](#usage)
  - [Authors](#authors)
  - [Data usage](#data-usage)
  - [License](#license)


## Install

The bot can be installed in a server using the discord install link below :

Link to the Archie bot install

## Usage

You can use the main commands :

```sh
/ajout_quete [quest_label] [quest_comments] // Add a quest to the user billboard with the corresponding label / comments
/lire_quetes // Display the list of quests of the user
/lire_toutes_quetes // Display the list of all published quests
/supp_quete [index] // Delete a quest from the list of user quest given it's index on the billboard
```
Whenever you need help, use the `/aide` command to get the list of available commands.

## Authors

Made by Shunbolt 

Discord ID : Shunbolt#1312

## Data usage

Only discord and server ids are stored in the database to handle quests.
No data will be use for commercial purposes

## License

This project is under the GPL-3.0 LICENSE

More on the [LICENSE](LICENSE) file

