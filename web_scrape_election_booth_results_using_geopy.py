#Import libraries bs4(BeautifulSoup) for web scraping
#pandas for dataframe creation
#requests to open webpages
#geopy and Nominatim for finding geolocation of addresses
#json for extracting info from json formatted data
import bs4
import pandas as pd
import requests
from geopy.geocoders import Nominatim


#The first few lines of code were derived from tutorial on this page
#https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/

#Open CSV as Pandas dataframe containing electorate names and the URLs of the election results on the AEC website
directory = 'C:/Users/Azzla/Downloads/Federal_Election_2022/VIC/'
electorates_csv = 'Electorate_Result_Pages_VIC.csv'

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
    tcp_first = []#Two candidate preferred percentage (TCP percentage) for the first
    tcp_second = []#Two candidate preferred percentage (TCP percentage) for the second
    votes_first = []#Total votes counted for each polling booth for first
    votes_second = []#Total votes counted for each polling booth for second
    polling_place_names_votes_table = []#Names of polling places in the votes table on page
    polling_place_names_address_table = []#Names of polling places in the table containing polling place info including addresses
    polling_place_addresses = []#Polling place addresses
    latitudes = [] #Latitudes of polling places
    longitudes = [] #Longitudes of polling places
    polling_booth_winning_party = [] #Party that won that polling place booth

    #Tags in tables
    #tcpbppPP - name of polling place (votes table)
    #ppPp - name of polling place (address table)
    #tcpbppC1P - tcp percentage of first candidate (first)
    #tcpbppC2P - tcp percentage of second candidate
    #tcpbppC1V - number of votes to first candidate (first)
    #tcpbppC2V - number of votes to second candidate
    #ppAdd - Polling Place Address

    #Scrape candidate names
    main_candidates = []
    candidates = soup.find_all('td', attrs = {'headers': 'tcpbvtCan'})
    for row in candidates:
        row = str(row)
        a = row.find('>')
        b = row.find(',')
        name = row[a+1:b]
        main_candidates.append(name)

    #Scrape candidate's party
    candidates_party = []
    candidates = soup.find_all('td', attrs = {'headers': 'tcpbvtPty'})
    for row in candidates:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        name = row[a+1:b]
        candidates_party.append(name)

    #Scrape candidate's status (Elected or not)
    candidates_status = []
    candidates = soup.find_all('td', attrs = {'headers': 'tcpbvtSts'})
    for row in candidates:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        name = row[a+1:b]
        candidates_status.append(name)
        
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
    #From the address, do a Google Maps search for it's coordinates

    num_cannotfinds = 0
    polling_place_address = soup.find_all('td', attrs = {'headers': 'ppAdd'})
    for row in polling_place_address:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        address_booth = row[a+1:b]
        address_booth.replace('&amp;', 'and')
        polling_place_addresses.append(address_booth)
        # calling the Nominatim tool
        loc = Nominatim(user_agent="GetLoc")
        try:
            # entering the location name
            getLoc = loc.geocode(str(address_booth))
            latitude = getLoc.latitude
            longitude = getLoc.longitude
        except:
            split_address = address_booth.split(',')
            length = len(split_address)
            if length >= 2:
                address_to_use = str(split_address[length-2]) + str(split_address[length-1])
                try:
                    getLoc = loc.geocode(str(address_to_use))
                    latitude = getLoc.latitude
                    longitude = getLoc.longitude
                except:
                    try:
                        address_to_use = str(split_address[0]) + str(split_address[length-1])
                        getLoc = loc.geocode(str(address_to_use))
                        latitude = getLoc.latitude
                        longitude = getLoc.longitude
                    except:
                        latitude = 'Cannot find latitude from address'
                        longitude = 'Cannot find longitude from address'
                        num_cannotfinds += 1
            else:
                address_to_use = str(split_address[0]) + str(split_address[length-1])
                try:
                    getLoc = loc.geocode(str(address_to_use))
                    latitude = getLoc.latitude
                    longitude = getLoc.longitude
                except:
                    latitude = 'Cannot find latitude from address'
                    longitude = 'Cannot find longitude from address'
                    num_cannotfinds += 1                                           
        latitudes.append(latitude)
        longitudes.append(longitude)

    #Scrape the two candidate preferred percentage vote for the first
    tcp_first_candidate = soup.find_all('td', attrs = {'headers': 'tcpbppC1P'})
    for row in tcp_first_candidate:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        value = row[a+1:b]
        tcp_first.append(value)
        
    #Scrape the two candidate preferred percentage vote for the second
    tcp_second_candidate = soup.find_all('td', attrs = {'headers': 'tcpbppC2P'})
    for row in tcp_second_candidate:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        value = row[a+1:b]
        tcp_second.append(value)

    #Scrape the number of votes for the first
    votes_first_candidate = soup.find_all('td', attrs = {'headers': 'tcpbppC1V'})
    for row in votes_first_candidate:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        value = row[a+1:b]
        votes_first.append(value)

    #Scrape the number of votes for the second
    votes_second_candidate = soup.find_all('td', attrs = {'headers': 'tcpbppC2V'})
    for row in votes_second_candidate:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        value = row[a+1:b]
        votes_second.append(value)

    #Now we need to make sure the votes meet the right candidate.

    #First we sum up the votes for the first and second candidates
    int_votes_first = []
    int_votes_second = []
    for votes in votes_first:
        votes = votes.replace(',','')
        votes = int(votes)
        int_votes_first.append(votes)
    for votes in votes_second:
        votes = votes.replace(',','')
        votes = int(votes)
        int_votes_second.append(votes)
    total_votes_first = sum(int_votes_first)
    total_votes_second = sum(int_votes_second)

    #Now to match the right candidates and the right party
    print(main_candidates)
    print(candidates_party)
    
    for i in range(2):
        if candidates_status[i] == 'Elected':
            winning_candidate = main_candidates[i]
            winning_party = candidates_party[i]

    if total_votes_first > total_votes_second:
        winning_candidate_votes = votes_first
        winning_candidate_tcp = tcp_first
        losing_candidate_votes = votes_second
        losing_candidate_tcp = tcp_second        
    else:
        winning_candidate_votes = votes_second
        winning_candidate_tcp = tcp_second
        losing_candidate_votes = votes_first
        losing_candidate_tcp = tcp_first

    for name in main_candidates:
        if name != str(winning_candidate):
            losing_candidate = name

    for party in candidates_party:
        if party != str(winning_party):
            losing_party = party
                

    #Set up arrays to store in values to go in dataframe for export
    table_winning_tcp = []
    table_losing_tcp = []
    table_winning_votes = []
    table_losing_votes = []
    table_polling_place_names = []
    table_polling_place_addresses = []
    table_latitudes = []
    table_longitudes = []

    #Find the number of polling places with addresses and the number of booths (polling places plus postal, hospital votes etc.)
    num_polling_places = len(polling_places_address_table)
    num_polling_options = len(polling_places_votes_table)

    #Match the polling place names in the address table with the names in the voted table to correctly allocate address and result information for each place
    for i in range(num_polling_places):
        for j in range(num_polling_options):
            if polling_place_names_votes_table[j] == polling_place_names_address_table[i]:
                table_polling_place_names.append(polling_place_names_votes_table[j])
                table_winning_tcp.append(winning_candidate_tcp[j])
                table_losing_tcp.append(losing_candidate_tcp[j])
                table_winning_votes.append(winning_candidate_votes[j])
                table_losing_votes.append(losing_candidate_votes[j])
                if winning_candidate_tcp[j] > losing_candidate_tcp[j]:
                    polling_booth_winning_party.append(winning_party)
                elif losing_candidate_tcp[j] > winning_candidate_tcp[j]:
                    polling_booth_winning_party.append(losing_party)
                else:
                    polling_booth_winning_party.append('Tie')
                table_polling_place_addresses.append(polling_place_addresses[i])
                table_latitudes.append(latitudes[i])
                table_longitudes.append(longitudes[i])

    TCP_first_header = 'TCP_' + str(winning_candidate)
    TCP_second_header = 'TCP_' + str(losing_candidate)
    votes_first_header = 'Votes_' + str(winning_candidate)
    votes_second_header = 'Votes_' + str(losing_candidate)


    #Create a dataframe to store all information scraped
    df = pd.DataFrame({'Name': table_polling_place_names, 'Address': table_polling_place_addresses,
                       'Latitude': table_latitudes, 'Longitude': table_longitudes, str(TCP_first_header): table_winning_tcp,
                       str(TCP_second_header): table_losing_tcp, str(votes_first_header): table_winning_votes,
                       str(votes_second_header): table_losing_votes, 'Winning_Party': polling_booth_winning_party})

    #Export dataframe to csv
    file_name = str(electorate_name) + '.csv'

    df.to_csv(directory + file_name)
    print('Number of addresses that no geolocation coordinates found for: ' + str(num_cannotfinds))
    print('Completed file ' + str(file_name))
            
