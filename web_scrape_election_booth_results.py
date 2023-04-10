#Import libraries bs4(BeautifulSoup) for web scraping, pandas for dataframe creation and requests to open and read the webpage
import bs4
import pandas as pd
import requests

#The first few lines of code were derived from tutorial on this page
#https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/

#Open CSV as Pandas dataframe containing electorate names and the URLs of the election results on the AEC website
directory = 'C:/Users/Azzla/Downloads/Federal_Election_2022/'
electorates_csv = 'Electorate_Result_Pages_SA_NT_TAS.csv'

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
    candidates = soup.find_all('td', attrs = {'headers': 'tcp2Candidate'})
    for row in candidates:
        row = str(row)
        a = row.find('>')
        b = row.find(',')
        name = row[a+1:b]
        main_candidates.append(name)
        

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
    #Here's an API key that is needed
    my_key = 'AIzaSyBbzl1MucXnp2Po5jpGizeaFZSsSmwfHho'
    polling_place_address = soup.find_all('td', attrs = {'headers': 'ppAdd'})
    for row in polling_place_address:
        row = str(row)
        a = row.find('>')
        b = row.find('</')
        address_booth = row[a+1:b]
        polling_place_addresses.append(address_booth)
        #From address we will extract components to use in Google Maps
        #search to extract coordinates
        #Split the address into the placename and street details components
        address_booth = address_booth.split(', ')
        place_name = address_booth[0]
        street_details = address_booth[1]#Includes locality, state, postcode
        # Following commands sourced from
        # 'https://towardsdatascience.com/pythons-geocoding-convert-a-list-of-addresses-into-a-map-f522ef513fd6'
        base_url= "https://maps.googleapis.com/maps/api/geocode/json?"
        # set up your search parameters - address and API key
        parameters = {"address": str(place_name), "key": my_key}
        r = requests.get(f"{base_url}{urllib.parse.urlencode(parameters)}")
        data = json.loads(r.content)
        try:
            geolocation = data.get("results")[0].get("geometry").get("location")
            latitude = geolocation['lat']
            longitude = geolocation['lng']
        except:
            parameters = {"address": str(street_details), "key": my_key}
            r = requests.get(f"{base_url}{urllib.parse.urlencode(parameters)}")
            data = json.loads(r.content)
            try:
                geolocation = data.get("results")[0].get("geometry").get("location")
                latitude = geolocation['lat']
                longitude = geolocation['lng']
            except:
                latitude = 'Cannot find on Google'
                longitude = 'Cannot find on Google'
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

    #Set up arrays to store in values to go in dataframe for export
    table_first_tcp = []
    table_second_tcp = []
    table_first_votes = []
    table_second_votes = []
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
                table_first_tcp.append(tcp_first[j])
                table_second_tcp.append(tcp_second[j])
                table_first_votes.append(votes_first[j])
                table_second_votes.append(votes_second[j])
                table_polling_place_addresses.append(polling_place_addresses[i])
                table_latitudes.append(latitudes[i])
                table_longitudes.append(longitudes[i])

    first_candidate_name = main_candidates[0]
    second_candidate_name = main_candidates[1]

    TCP_first_header = 'TCP_' + str(first_candidate_name)
    TCP_second_header = 'TCP_' + str(second_candidate_name)
    votes_first_header = 'Votes_' + str(first_candidate_name)
    votes_second_header = 'Votes_' + str(second_candidate_name)

    #Create a dataframe to store all information scraped
    df = pd.DataFrame({'name': table_polling_place_names, 'address': table_polling_place_addresses, str(TCP_first_header): table_first_tcp,
                       str(TCP_second_header): table_second_tcp, str(votes_first_header): table_first_votes, str(votes_second_header): table_second_votes})

    #Export dataframe to csv
    file_name = str(electorate_name) + '.csv'

    df.to_csv(directory + file_name)
            
