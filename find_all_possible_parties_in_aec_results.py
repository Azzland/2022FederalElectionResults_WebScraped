import pandas as pd

all_parties = []

directory = 'C:/Users/Azzla/Downloads/Federal_Election_2022/'

folders = ['WA', 'SA_NT_and_TAS', 'VIC', 'NSW_and_ACT', 'QLD']

#Declare csv files containing electorate names to go through
files = []
files.append('Electorate_Result_Pages_WA.csv')
files.append('Electorate_Result_Pages_SA_NT_TAS.csv')
files.append('Electorate_Result_Pages_VIC.csv')
files.append('Electorate_Result_Pages_NSW_ACT.csv')
files.append('Electorate_Result_Pages_QLD.csv')


num_regions = len(folders)

for i in range(num_regions):
    folder_name = folders[i]
    file_name = files[i]
    file_location = directory + folder_name + '/' + file_name
    df = pd.read_csv(file_location)
    electorates = df['ELECTORATE']
    for e in electorates:
        data_file = str(e) + '.csv'
        data_location = directory + folder_name + '/' + data_file
        df_e = pd.read_csv(data_location)
        winning_party = df_e['Winning_Party']
        for w in winning_party:
            if w not in all_parties:
                all_parties.append(w)
                print(w)
    
