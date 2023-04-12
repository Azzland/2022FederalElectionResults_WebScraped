#Import libraries bs4(BeautifulSoup) for web scraping
#pandas for dataframe creation
#requests to open webpages
import bs4
import pandas as pd
import requests

#The first few lines of code were derived from tutorial on this page
#https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/

#Open CSV as Pandas dataframe containing electorate names and the URLs of the election results on the AEC website
directory = 'C:/Users/Azzla/Downloads/Federal_Election_2022/QLD/'
electorates_csv = 'Electorate_Result_Pages_QLD.csv'

electorates_directory = pd.read_csv(directory + electorates_csv)

#Get the columns
name_of_electorates = electorates_directory['ELECTORATE'] #Names of each electorate
urls_of_results = electorates_directory['URL'] #URLs of the elctorates

num_electorates = len(name_of_electorates)#Number of electorates

#Loop to iterate for each electorate
for i in range(num_electorates):
    #Get url of polling results page for electorate
    url = urls_of_results[i]
    #Get name of electorate
    electorate_name = name_of_electorates[i]

    r = requests.get(url)
       
    soup = bs4.BeautifulSoup(r.content, features="html.parser")

    #Scrape candidate names
    main_candidates = []
    candidates = soup.find_all('td', attrs = {'headers': 'tcp2Candidate'})
    for row in candidates:
        row = str(row)
        a = row.find('>')
        b = row.find(',')
        name = row[a+1:b]
        main_candidates.append(name)

    #Scrape party of each candidate
    party_represented = []
    parties = soup.find_all('td', attrs = {'headers': 'tcpPty'})
    for row in parties:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        name = row[a+1:b]
        #print(name)
        party_represented.append(name)

    first_candidate = main_candidates[0]
    first_candidate_party = party_represented[0]
    second_candidate = main_candidates[1]
    second_candidate_party = party_represented[1]

    #Now open csv file for that electorate
    CSV_Name = str(electorate_name) + '.csv'
    df = pd.read_csv(directory + CSV_Name)

    #get TCP column results
    tcp_first_candidate_col = 'TCP_' + str(first_candidate)
    tcp_second_candidate_col = 'TCP_' + str(second_candidate)

    party_leading = []
    num_booths = len(df[tcp_first_candidate_col])

    for i in range(num_booths):
        first_candidate_tcp = df[tcp_first_candidate_col][i]
        second_candidate_tcp = df[tcp_second_candidate_col][i]
        if first_candidate_tcp > second_candidate_tcp:
            party_leading.append(first_candidate_party)
        elif second_candidate_tcp > first_candidate_tcp:
            party_leading.append(second_candidate_party)
        else:
            party_leading.append('Tie')

    df['Party_Leading'] = party_leading

    #Export updated dataframe to csv
    df.to_csv(directory + str(electorate_name) + '_v2.csv')
    print('File ' + str(str(electorate_name) + '_v2.csv completed!'))
            
print('Complete')

