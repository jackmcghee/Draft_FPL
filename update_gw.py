"""this takes all player data (created in update_players or similar) and converts it into GW files which contain all player data for each gw
it also takes memeber data and works out which players are playing for each week, then gets associated stats for each member's team both collectinve and individual.
The memeber details are in the member_details csv stats are in the attributes csv"""

import FPL #my custom class
import pandas as pd
import json
import datetime as dt

min_gw = 1
min_player_num = 1
players_in_squad = 15 #could get this from the bootstrap settings, but fine for now

with open(f'C:/Users/Knick/Documents/Python/Projects - Independent/FPL/settings.txt','r') as jsonfile: #opening the settings json file
    data = json.load(jsonfile) #loading the data
    prefix_folder = data['draft_settings'][0]['prefix_folder']
    players_updated = data['draft_settings'][0]['players_updated']
    gw_updated = data['draft_settings'][0]['gw_updated']

d = dt.date.today()
today = d.strftime("%d/%m/%y") #today's date

#needing to check the players_updated vs gw_updated
if players_updated > gw_updated:
    print("player changes made, commencing gw updates")

    all_players = pd.read_csv(f'{prefix_folder}/bootstrap-static/elements.csv',index_col=0)
    max_player_num = max(all_players['id'])
    print(f"downloading all players ({min_player_num} to {max_player_num})")

    event = pd.read_csv(f'{prefix_folder}/bootstrap-static/events.csv',index_col=0)
    max_gw = event.iloc[0]['current']
    print(f"collating gws {min_gw} to {max_gw}")

    for gw in range(min_gw,max_gw+1): #looping through gws
        print(f"collating gw {gw} data")
        full_gw = pd.DataFrame()
        for n in range(1,max_player_num+1): #looping through players
            FPL_df = FPL.FPL_player(player_num=n,prefix_folder=prefix_folder)
            player = FPL_df.getPlayerFromCSV(within_prefix_folder=True)
            player_gw_df = None
            if len(player) > 0:
                if gw in list(player['event']): #if the player has played in that gw
                    player_gw_df = player[player['event']==gw]
                    if len(player_gw_df)>1: #and there is more than one row
                        analyser = FPL_analyse()
                        player_gw_df = analyser.multi_row(player_gw_df) 
                    full_gw = pd.concat([full_gw,player_gw_df]) #add the row to a dictionary with all the rows from this gw
            else: #occurs if the player df is empty (happens for new players)
                print(f"player {n} skipped")
        if len(full_gw) > 0: #if any results have been generated
            full_gw.set_index('element')  #once everything has been looped through, set the index to be the player id  
            full_gw.to_csv(f"{prefix_folder}/Weeks/GW{gw}.csv") #save it
            print(f"{prefix_folder}/Weeks/GW{gw}.csv saved")
        else:
            print("no results for gw: {gw}")


    #this will get the initials and entry ids of each memeber
    print('reading member_details csv')
    league = pd.read_csv(f'{prefix_folder}/Inputs/member_details.csv')
    
    #this will generate the attribute requested
    print("reading attributes csv")
    attributes = pd.read_csv(f'{prefix_folder}/Inputs/attributes.csv') #where the attributes information is stored

    #this is to get the member's team, just the ids
    for i in range(len(league)):
        lge = league.iloc[i] #the row of the member
        member = FPL.FPL_member(member_initial=lge['name'],entry_id=lge['entry_id'],prefix_folder=prefix_folder)
        draft_team_all_weeks = pd.DataFrame([],index=range(min_gw,max_gw+1))
        for gw in range(min_gw,max_gw+1): #looping through gws 
            team_gw = member.gen_draft_team(gw) #the member's team for each gw
            draft_team_all_weeks = draft_team_all_weeks.join(team_gw,how='right')
        draft_team_all_weeks.to_csv(f'{prefix_folder}/Draft_teams/{lge["name"]}.csv') #saving the full team
        print(f'{prefix_folder}/Draft_teams/{lge["name"]}.csv saved')

    #this is dealing with the rest on the attributes
    analyser = FPL.FPL_analyse()
    for a in range(len(attributes)):
        att = attributes.iloc[a] #the attribute of the row
        print(f"fetching member attribute data: attribute: '{att['name']}'")
        member_all_score_df = pd.DataFrame([],index=range(min_gw,max_gw+1))
        overall_over_time_df = pd.DataFrame([])
        
        for i in range(len(league)):
            lge = league.iloc[i]
            player_stats_all = pd.DataFrame([]) #reset the stat df          
            member = FPL.FPL_member(member_initial=lge['name'],entry_id=lge['entry_id'],prefix_folder=prefix_folder)
            for gw in range(min_gw,max_gw+1): #looping through gws 
                player_stats = member.map_player_stat_3(gw,attribute=att['name'],constant=att['static']) #get the att of each player for each week
                player_stats_all = player_stats_all.join(player_stats,how='right') #add this to the stat df
            player_stats_all.to_csv(f'{prefix_folder}/Draft_teams/{lge["name"]}_{att["name"]}.csv') #saving
            print(f"{prefix_folder}/Draft_teams/{lge['name']}_{att['name']}.csv saved")
            
            if att['sum'] == True: #if the attribute needs to get summed
                member_all_score_df[lge['name']] = list(player_stats_all.head(11).sum().round(3)) #take the sum of the first 11 player scores
                a = analyser.overall_over_time(player_stats_all.head(11),'sum')
                overall_over_time_df[lge['name']] = a.values()
 
        if att['sum'] == True:
            member_all_score_df_final = member_all_score_df.T
            member_all_score_df.to_csv(f'{prefix_folder}/Draft_stats/full_{att["name"]}.csv')
            print(f"{prefix_folder}/full_{att['name']}.csv saved")
            if att['static'] == False:
                overall_over_time_df.index = a.keys()
                overall_over_time_df.to_csv(f'{prefix_folder}/Draft_stats/full_tracked_sum_{att["name"]}.csv')
                print(f"{prefix_folder}/full_tracked_sum_{att['name']}.csv saved")

    #updating settings
    data['draft_settings'][0]['gw_updated'] = today
    with open(f'settings.txt','w') as jsonfile:
        json.dump(data,jsonfile,indent=4) #putting the data into the settings json
    print(f"update complete, gw updated date updated to {today}")

else:
    print("no player changes made, no gw changes made")
