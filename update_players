"""run this to generate all player data into the Players foler. Each player will have their data for gws that they've played in

import FPL #my custom class
import pandas as pd
import json
import datetime as dt

print("checking settings")
with open(f'C:/Users/Knick/Documents/Python/Projects - Independent/FPL/settings.txt','r') as jsonfile: #opening the settings json file
    data = json.load(jsonfile) #loading the data
    current_latest_gw = data['draft_settings'][0]['latest_week']
    prefix_folder = data['draft_settings'][0]['prefix_folder']

d = dt.date.today()
today = d.strftime("%d/%m/%y") #today's date

#this generates all the bootstrap stats for the league
print("updating bootstrap info")
fpl_1 = FPL.FPL(draft_url= f'https://draft.premierleague.com/api/bootstrap-static') #create the initial instance
fpl_conn = fpl_1.connect(df=False)
detail = fpl_conn[1]

for i in detail: #updating a csv for each heading detected within the bootstrap-static address
    df = pd.DataFrame(detail[i])
    df.to_csv(f'{prefix_folder}/bootstrap-static/{i}.csv')
    print(f"{prefix_folder}/bootstrap-static/{i}.csv saved")

event = pd.read_csv(f'{prefix_folder}/bootstrap-static/events.csv',index_col=0)
max_gw = event.iloc[0]['current'] #fetching the most recent gw

print(f"date: {today}, latest local gw: {current_latest_gw}, latest API gw: {max_gw}")
if max_gw > current_latest_gw: #if the most recent gw is greater than the one detected in the settings json
    print("update required")
    """The following is using the FPL class to populate the FPL folder"""
    min_player_num = 1
    all_players = pd.read_csv(f'{prefix_folder}/bootstrap-static/elements.csv',index_col=0)
    max_player_num = max(all_players['id'])
    print(f"downloading players {min_player_num} to {max_player_num}")

    #loop over all players and generate all their results"""
    for n in range(min_player_num,max_player_num+1): #looping through players
        FPL_df = FPL.FPL_player(player_num=n,prefix_folder=prefix_folder) #loading a player
        FPL_list = FPL_df.gen_player_results() #getting their full results
        print(f"dowloading player data: player {n}")
        if FPL_list is not None: #if there are results
            FPL_df = pd.DataFrame(FPL_list)
            FPL_df.to_csv(f"{prefix_folder}/Players/Player_{n}.csv")
            print(f"{prefix_folder}/Players/Player_{n}.csv saved")
        else:
            print("no data")
              
    #updating the settings
    date['draft_settings'][0]['latest_week'] = max_gw
    data['draft_settings'][0]['players_updated'] = today
    print(f"update complete, players_updated date updated to {today}")
    
else:
    print(f"files up to date at gw {max_gw}, no changes made")

#updating more settings
data['draft_settings'][0]['players_checked'] = today
with open(f'settings.txt','w') as jsonfile:
    json.dump(data,jsonfile,indent=4) #putting the data into the settings json
