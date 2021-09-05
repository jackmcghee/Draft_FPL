import FPL #my custom class
import json

fpl_1 = FPL.FPL() #create the initial instance

print("initiating setup")
with open(f'C:/Users/Knick/Documents/Python/Projects - Independent/FPL/settings.txt','r') as jsonfile:
    data = json.load(jsonfile)

fldrs = data['draft_settings'][0]['folders'] #getting the foler list
fldr_list = fldrs.split(',')
folders = [f.strip() for f in fldr_list] #getting it into a list
prefix_folder = data['draft_settings'][0]['prefix_folder']

#to create the original folders
fpl_1.create_folder(prefix_folder,within_prefix_folder=False) #create the prefix folder
for f in folders:
    fpl_1.create_folder(f,within_prefix_folder=True) #create all the sub folders
print("setup complete")
