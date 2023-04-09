#Import libraries bs4(BeautifulSoup) for web scraping, pandas for dataframe creation and requests to open and read the webpage
import bs4
import pandas as pd
import requests

#The first few lines of code were derived from tutorial on this page
#https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/

#Open CSV as Pandas dataframe containing electorate names and the URLs of the election results on the AEC website
directory = 'C:/Users/Azzla/Downloads/Federal_Election_2022/'
electorates_csv = 'Electorate_Result_Pages_WA.csv'

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

    #Set up arrays to store information
    tcp_incumbent = []#Two candidate preferred percentage (TCP percentage) for the incumbent
    tcp_challenger = []#Two candidate preferred percentage (TCP percentage) for the challenger
    votes_incumbent = []#Total votes counted for each polling booth for incumbent
    votes_challenger = []#Total votes counted for each polling booth for challenger
    polling_place_names_votes_table = []#Names of polling places in the votes table on page
    polling_place_names_address_table = []#Names of polling places in the table containing polling place info including addresses
    polling_place_addresses = []#Polling place addresses

    #Tags in tables
    #tcpbppPP - name of polling place (votes table)
    #ppPp - name of polling place (address table)
    #tcpbppC1P - tcp percentage of first candidate (incumbent)
    #tcpbppC2P - tcp percentage of second candidate
    #tcpbppC1V - number of votes to first candidate (incumbent)
    #tcpbppC2V - number of votes to second candidate
    #ppAdd - Polling Place Address

    #Scrape all polling place names in the Address table
    polling_places_votes_table = soup.find_all('td', attrs = {'headers': 'tcpbppPP'})
    for row in polling_places_votes_table:
        row_in_a_tag = row.a
        if row_in_a_tag == 'None':
            polling_place_names_votes_table.append('Not a polling day polling booth in electorate')
        else:
            row_in_a_tag = str(row_in_a_tag)
            a = row_in_a_tag.find('>')
            b = row_in_a_tag.find('</')
            name = row_in_a_tag[a+1:b]
            polling_place_names_votes_table.append(name)

    #Scrape all polling place names in the votes table
    polling_places_address_table = soup.find_all('td', attrs = {'headers': 'ppPp'})
    for row in polling_places_address_table:
        row_in_a_tag = row.a
        if row_in_a_tag == 'None':
            polling_place_names_address_table.append('Not a polling day polling booth in electorate')
        else:
            row_in_a_tag = str(row_in_a_tag)
            a = row_in_a_tag.find('>')
            b = row_in_a_tag.find('</')
            name = row_in_a_tag[a+1:b]
            polling_place_names_address_table.append(name)

    #Scrape the polling place addresses
    polling_place_address = soup.find_all('td', attrs = {'headers': 'ppAdd'})
    for row in polling_place_address:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        address = row[a+1:b]
        polling_place_addresses.append(address)   

    #Scrape the two candidate preferred percentage vote for the incumbent
    tcp_first_candidate = soup.find_all('td', attrs = {'headers': 'tcpbppC1P'})
    for row in tcp_first_candidate:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        value = row[a+1:b]
        tcp_incumbent.append(value)
        
    #Scrape the two candidate preferred percentage vote for the challenger
    tcp_second_candidate = soup.find_all('td', attrs = {'headers': 'tcpbppC2P'})
    for row in tcp_second_candidate:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        value = row[a+1:b]
        tcp_challenger.append(value)

    #Scrape the number of votes for the incumbent
    votes_first_candidate = soup.find_all('td', attrs = {'headers': 'tcpbppC1V'})
    for row in votes_first_candidate:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        value = row[a+1:b]
        votes_incumbent.append(value)

    #Scrape the number of votes for the challenger
    votes_second_candidate = soup.find_all('td', attrs = {'headers': 'tcpbppC2V'})
    for row in votes_second_candidate:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        value = row[a+1:b]
        votes_challenger.append(value)

    #Set up arrays to store in values to go in dataframe for export
    table_incumbent_tcp = []
    table_challenger_tcp = []
    table_incumbent_votes = []
    table_challenger_votes = []
    table_polling_place_names = []
    table_polling_place_addresses = []

    #Find the number of polling places with addresses and the number of booths (polling places plus postal, hospital votes etc.)
    num_polling_places = len(polling_places_address_table)
    num_polling_options = len(polling_places_votes_table)

    #Match the polling place names in the address table with the names in the voted table to correctly allocate address and result information for each place
    for i in range(num_polling_places):
        for j in range(num_polling_options):
            if polling_place_names_votes_table[j] == polling_place_names_address_table[i]:
                table_polling_place_names.append(polling_place_names_votes_table[j])
                table_incumbent_tcp.append(tcp_incumbent[j])
                table_challenger_tcp.append(tcp_challenger[j])
                table_incumbent_votes.append(votes_incumbent[j])
                table_challenger_votes.append(votes_challenger[j])
                table_polling_place_addresses.append(polling_place_addresses[i])

    #Create a dataframe to store all information scraped
    df = pd.DataFrame({'name': table_polling_place_names, 'address': table_polling_place_addresses, 'incumbent_TCP': table_incumbent_tcp,
                       'challenger_TCP': table_challenger_tcp, 'incumbent_votes': table_incumbent_votes, 'challenger_votes': table_challenger_votes})

    #Export dataframe to csv
    file_name = str(electorate_name) + '.csv'

    df.to_csv(directory + file_name)
            
