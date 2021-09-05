# Draft_FPL
Creating a way to import player data from FPL, as well as team data from a local league
When recreating, the settings file should be stored in a central main folder with all the .py files.
The settings file should be updated: 
"latest_week": 0
set players_checked, players_updated and gw_updated to yesterdays date (this should be corrected so that they can be set to 0)
The FPL_setup.py script should be run
It will create all neccessary folders. Move the attributes.csv and memeber_details.csv into the Inputs folder (this probably isn't neccessary and could be removed)
Set the update_players.py to run and the update_gw.py to run after it 
