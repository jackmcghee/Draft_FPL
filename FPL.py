import requests
import pandas as pd
import numpy as np
import matplotlib 
import os

class FPL(object):
    """This is the basic FPL object, it contains basic information and generic methods
    most objects should be generated via one of its sub classes"""
    def __init__(self,prefix_folder="21_22",draft_url="https://draft.premierleague.com/api"):
        self.prefix_folder = self.prefix_check(prefix_folder)
        self.draft_url = draft_url
        
    def prefix_check(self,prefix_folder):
        #if the prefix string is not empty and doesn't end in /, appending it so it does
        if prefix_folder != "" and prefix_folder[-1] != '/': 
            prefix_folder = prefix_folder + '/'
        return prefix_folder

    def connect(self,column="",df=True,raise_exception=True):
        """used to connect via the requests library and give a json or df back"""
        print("connecting to...")
        print(self.draft_url)
        r = requests.get(self.draft_url)
        if r.status_code == 404: #this happens if there is no website at the requested address
            if raise_exception == False:
                return [False,None]
            else:
                raise Exception(f"Connection Issue Detected with url: \n'{draft_url}'")
        draft_json = r.json() #getting the request message as a json
        if len(column) > 0: #if a column is given...
            json = draft_json[column] #...get that secion of the json
        else:
            json = draft_json
        if df == True: #if df is True it will attempt to return a df
            result = pd.DataFrame(json)
        else:
            result = json
        print("...finished")
        return [True,result]

    def save(self,name,type="csv"):
        """Save a df as a csv, deprecated as it can just be replaced at all relevant parts by to_csv)"""
        if type == "csv":
            self.df.to_csv(name) #...which is then saved to a csv

    def create_folder(self,folder_name="",within_prefix_folder=False):
        """creating a folder, within a prefix folder or not"""
        if within_prefix_folder == True:
            folder_name = f"{self.prefix_folder}/{folder_name}"
        if folder_name != "":
            try:
                os.mkdir(folder_name)
                return True
            except WindowsError as e:
                if e.winerror == 183:
                    return False
        else:
            print("Please enter a name for a folder")

    def __exit__(self):
        pass
    

class FPL_player(FPL):
    """ This is used to represent the results of a Premier League player within FPL"""
    def __init__(self,player_num,draft_url= 'https://draft.premierleague.com/api',prefix_folder=""):       
        self.player_num = player_num #possibly push this to gen_player_results as an argument, see what else we create  
        super().__init__(prefix_folder,draft_url)

    def gen_player_results(self,df_save=True):
        """get the player's results via connecting to api, i'm not sure this is necessary and I think the instance could run the connect command on their own"""
        draft_url = f'{self.draft_url}/element-summary/{self.player_num}' #a team's GW team
        results = self.connect(draft_url,'history',raise_exception=False) #get the player's history
        if results[0] == True:
            return results[1]
        else:
            return None

    def gen_gw_results_from_csv(self,gw,within_prefix_folder=True,df_save=True):
        """used to track week scores based on player csvs, this is currently replaced by calling getPlayerFromCSV alone"""
        player = self.getPlayerFromCSV(within_prefix_folder)
        if gw in list(player['event']):
            player_gw_df = player[player['event']==gw]
        else:
            player_gw_df = None
        self.df = player_gw_df
        return player_gw_df
    
    def getPlayerFromCSV(self,within_prefix_folder=True):
        folder = "Players"
        if within_prefix_folder == True: #i don't think this needs to be hear and could be moved to the script
            folder = self.append_prefix_folder(folder)
        try:
            player_csv = f"{folder}/Player_{self.player_num}.csv"
            player = pd.read_csv(player_csv,index_col=0) #check we can load the player
            self.results = player #these two lines doesn't have a purpose at the moment, or if they do then they do the same thing, what does FPL_player(1).getPlayerFromCSV.results show?
            return player
        except:
            raise Exception(f"{player_csv} not found, please check Players folder")

            
    def append_prefix_folder(self,folder):
        if self.prefix_folder != "":
            folder = f"{self.prefix_folder}{folder}"
        return folder




class FPL_member(FPL):
    """used to track the scores of any FPL team"""
    def __init__(self,draft_url= 'https://draft.premierleague.com/api',
                 players_in_squad=15,players_in_team=11,prefix_folder="",member_initial="JM",entry_id="128314",
                 check=True):
        self.players_in_squad = players_in_squad
        self.players_in_team = players_in_team
        self.entry_id = entry_id
        self.member_initial = member_initial
        super().__init__(prefix_folder,draft_url)

    """def set_df(self,df) #getter
        self.df = df
    def get_df(self)
        return self.df"""

    def gen_draft_team(self,gw):
        """this creates the draft team for the member over all the weeks"""     
        draft_url = f'{self.draft_url}/entry/{self.entry_id}/event/{gw}' #a team's GW team
        team = self.connect(draft_url,'picks',True) #this is their player list
        team = team[1] #...the team 
        team.set_index('position',inplace=True) #making sure the dataframe is in position order
        team_df = pd.DataFrame([],index=range(1,self.players_in_squad+1)) #create the dataframe
        team_df[f"GW{gw}"] = team.loc[:,['element']] #adding their full GW to a df
        return team_df

    def map_player_stat_3(self,gw,attribute="web_name",constant=True,df_save=True): 
        """the following is mapping the name of each player onto their id, it can be used to map any attribute.
        If the value stays constant throughout e.g. name, use constant=True
        It requires the bootstrap, gw and member folders to exist already"""
        if constant == True: #if constant, take the lookups from the bootstrap element table
            elements = pd.read_csv(f'{self.prefix_folder}/bootstrap-static/elements.csv',index_col=0)
            elements.set_index(['id'],inplace=True)
        team = pd.read_csv(f'{self.prefix_folder}/Draft_teams/{self.member_initial}.csv',index_col=0)
        new_df = pd.DataFrame([])
        if constant == True:
            new_df[f'GW{gw}'] = team[f'GW{gw}'].map(elements[attribute]) #if constant put the mappings directly onto the ids
        else:
            wk = pd.read_csv(f"{self.prefix_folder}/Weeks/GW{gw}.csv") #if not constant, fetch each mapping per GW 
            wk.set_index('element',inplace=True)
            new_df[f'GW{gw}'] = team[f'GW{gw}'].map(wk[attribute])
            new_df.fillna(0,inplace=True)
        self.df = new_df
        return new_df

    #recommendation: to get a full gw, loop through GWs for each member and join them.

class FPL_analyse(FPL): 
    def __init__(self,prefix_folder="21_22", players_in_squad=15, players_in_team=11):
        self.players_in_squad = players_in_squad
        self.players_in_team = players_in_team
        super().__init__(prefix_folder)
        
    #def get_df(self): #would like more of these
    #    return self.df
    
    #def set_df(self,df):
    #    self.df = df
    
    def member_total_scores(self): #moved into the script
        pass
    
    def multi_row(self,concat_list=['id','detail','fixture','opponent_team'],exception_list = ['element','event']):
        """used to deal with player with double/triple GWs
        can move the concat list and exeption list into the settings file"""
        my_dict = {}      
        for i in self.df.columns:
            if i in concat_list: 
                my_dict[i] = ' & '.join(list(self.df[i].astype(str))) #concatenate in the concat list
            elif i not in exception_list: 
                my_dict[i] = round(sum(self.df[i]),4) #sum anything in the exception list
            else:
                my_dict[i] = list(self.df[i])[0] #otherwise just take the first value
        modified_df = pd.DataFrame([my_dict])
        return modified_df
    
    def team_stat_1(self,df,team_type=0,df_save=True):
        """this gets the score of each member's team based on a df of GW results
        team_types: 1=Full Squad(15),0=Main Team(11),-1=Subs(4)"""
        #summing
        if team_type == 1:
            total = df.sum() #the full 15 players
        elif team_type == 0:
            total = df.head(11).sum() #only the first 11 players are needed (can get this from the fpl settings if it were ever to vary
        elif team_type == -1:
            total = df.tail(4).sum() #only the last 4 players are needed
        else:
            raise Exception("Invalid Team Type")
        return total

    def overall_over_time(self,df,type="sum"):
        """this gets the average of a df through columns (useful for gw1, gw2..."""
        stat_list = {}
        wk_list = []
        for i in df:
            wk_list.append(i)
            if type == 'sum':
                stat_list[i] = df[wk_list].sum().sum()
            elif type == 'mean':
                stat_list[i] = df[wk_list].mean().mean()
            elif type == 'median':
                stat_list[i] = df[wk_list].median().median()
        return stat_list



