from qgis.PyQt import QtGui
import pandas as pd

def party_colour(party):
    all_parties = []
    all_parties.append('Australian Labor Party')
    all_parties.append('Liberal')
    all_parties.append('Tie')
    all_parties.append('Independent')
    all_parties.append('Centre Alliance')
    all_parties.append('NT CLP')
    all_parties.append('A.L.P.')
    all_parties.append('The Greens')
    all_parties.append('The Nationals')
    all_parties.append('Labor')
    all_parties.append('Liberal National Party of Queensland')
    all_parties.append('Queensland Greens')
    all_parties.append("Katter's Australian Party (KAP)")

    party_colours = []
    party_colours.append('red')
    party_colours.append('blue')
    party_colours.append('black')
    party_colours.append('grey')
    party_colours.append('orange')
    party_colours.append('blue')
    party_colours.append('red')
    party_colours.append('green')
    party_colours.append('blue')
    party_colours.append('red')
    party_colours.append('blue')
    party_colours.append('green')
    party_colours.append('purple')

    num_parties = len(all_parties)
    for i in range(num_parties):
        if all_parties[i] == party:
            correct_party = all_parties[i]
            correct_colour = party_colours[i]

    return correct_colour
    
    
    

def add_electorate(electorate):
    folders = ['WA', 'SA_NT_and_TAS', 'VIC', 'NSW_and_ACT', 'QLD']

    #Declare csv files containing electorate names to go through
    files = []
    files.append('Electorate_Result_Pages_WA.csv')
    files.append('Electorate_Result_Pages_SA_NT_TAS.csv')
    files.append('Electorate_Result_Pages_VIC.csv')
    files.append('Electorate_Result_Pages_NSW_ACT.csv')
    files.append('Electorate_Result_Pages_QLD.csv')
    
    
    num_regions = len(folders)

    electorate_region = 'DNE'
    e_file = 'DNE'

    directory = 'C:/Users/Azzla/Downloads/Federal_Election_2022/'

    for i in range(num_regions):
        f_directory = directory + str(folders[i]) + '/'
        csv_file = f_directory + str(files[i])
        df = pd.read_csv(csv_file)
        electorates = df['ELECTORATE']
        for e in electorates:
            if e == electorate:
                electorate_region = folders[i]
                e_file = '/' + str(e) + '.csv'

    if (electorate_region == 'DNE') or (e_file == 'DNE'):
        print('The electorate you entered does not exist!')
    else:
        canvas = qgis.utils.iface.mapCanvas()
        registry = QgsProject.instance()
        
        basemap_source = "type=xyz&url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0"
        basemap = QgsRasterLayer(basemap_source, 'OpenStreetMap','wms')

        all_electorates_shp = directory + '2021-Cwlth_electoral_boundaries_ESRI/2021_ELB_region.shp'
        seats_layer = QgsVectorLayer(all_electorates_shp,"Electorates","ogr")

        suburbs = 'C:/Users/Azzla/Downloads/SAL_2021_AUST_GDA2020_SHP/SAL_2021_AUST_GDA2020.shp'
        suburbs_lyr = QgsVectorLayer(suburbs, "Suburbs", "ogr")

        electorate_booths = directory + electorate_region + e_file
        booth_results = pd.read_csv(electorate_booths)
        winning_parties= booth_results['Winning_Party']
        parties_in_df = []
        for w in winning_parties:
            if w not in parties_in_df:
                parties_in_df.append(w)
                
        InFlPth="file:///"+ electorate_booths
        uri = InFlPth+"?delimiter=%s&xField=%s&yField=%s" % (",","Longitude","Latitude")
        booth_results_shp = QgsVectorLayer(uri, "Booth Results", "delimitedtext")

        current_seat_shp = directory + "Electorate_mapping.shp"
        suburbs_in_seat_shp = directory + "Suburbs_in_electorate.shp"

        electorate_shp = directory + electorate_region + '/' + str(electorate) + '.shp'
        seat_boundary = processing.run("native:extractbyattribute", {'INPUT':all_electorates_shp,'FIELD':'Elect_div','OPERATOR':0,
                                                                     'VALUE':electorate,'OUTPUT':current_seat_shp})

        seat_boundary_lyr = QgsVectorLayer(current_seat_shp, "Electorate Boundary", "ogr")
        registry.addMapLayers([seat_boundary_lyr, basemap])
        seat_boundary_style = seat_boundary_lyr.renderer()
        symbol_e = seat_boundary_style.symbol()
        #Set fill colour
        symbol_e.setColor(QColor.fromRgb(104,62,6))
        #Set fill style
        symbol_e.symbolLayer(0).setBrushStyle(Qt.BrushStyle(Qt.NoBrush))#Set stroke colour
        symbol_e.symbolLayer(0).setStrokeColor(QColor(104,62,6))
        symbol_e.symbolLayer(0).setStrokeWidth(1)
        #Set transparency
        symbol_e.setOpacity(100)
        #Refresh
        seat_boundary_lyr.triggerRepaint()

        suburbs_in_seat = processing.run("native:intersection", {'INPUT':suburbs,'OVERLAY':seat_boundary_lyr,'INPUT_FIELDS':[],
                                                                    'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'',
                                                                    'OUTPUT':suburbs_in_seat_shp,'GRID_SIZE':None})
  
        suburbs_in_seat_lyr = QgsVectorLayer(suburbs_in_seat_shp, "Suburbs In Electorate", "ogr")
        registry.addMapLayers([suburbs_in_seat_lyr])
        suburbs_style = suburbs_in_seat_lyr.renderer()
        symbol_s = suburbs_style.symbol()
        #Set fill colour
        symbol_s.setColor(QColor.fromRgb(206,132,226))
        #Set fill style
        symbol_s.symbolLayer(0).setBrushStyle(Qt.BrushStyle(Qt.NoBrush))#Set stroke colour
        symbol_s.symbolLayer(0).setStrokeColor(QColor(206,132,226))
        symbol_s.symbolLayer(0).setStrokeWidth(0.2)
        #Set transparency
        symbol_s.setOpacity(100)
        #Refresh
        suburbs_in_seat_lyr.triggerRepaint()

        columns_in_df = booth_results.columns
        label_columns = [str(columns_in_df[6]), str(columns_in_df[7])]

        i = 0
        for party in parties_in_df:
            output_lyr = directory + 'Winning_booths_' + str(party) + '.shp'
            party_lyr = processing.run("native:extractbyattribute", {'INPUT':booth_results_shp,'FIELD':'Winning_Party','OPERATOR':0,
                                                                     'VALUE':party,'OUTPUT':output_lyr})
            winning_booths_lyr = QgsVectorLayer(output_lyr, str(party), "ogr")
            registry.addMapLayers([winning_booths_lyr])

##            wb_renderer = winning_booths_lyr.renderer()
##            symbol_wb = wb_renderer.symbol()
##            #symbol_wb.setColor(QColor('0,0,0,0'))
##            #Set transparency
##            symbol_wb.setOpacity(0)
##            winning_booths_lyr.triggerRepaint()
##
##            label = QgsPalLayerSettings()
##            label.enabled = True
##            label.fieldName = str(label_columns[i])
##            text_format = QgsTextFormat()
##            label_colour = party_colour(party)
##            text_format.setFont(QFont("Open Sans", 9))
##            text_format.setColor(QColor(str(label_colour)))
##
##            buffer_settings = QgsTextBufferSettings()
##            buffer_settings.setEnabled(True)
##            buffer_settings.setSize(1)
##            buffer_settings.setColor(QColor("white"))
##            text_format.setBuffer(buffer_settings)
##            label.setFormat(text_format)
##            #label.enabled = True
####            label_settings = QgsVectorLayerSimpleLabeling(label)
####            winning_booths_lyr.setLabeling(label_settings)
##            wb_renderer.setSymbol(symbol_wb)
##            winning_booths_lyr.setLabeling(QgsVectorLayerSimpleLabeling(label))
##            #label.drawLabels = True
##            winning_booths_lyr.triggerRepaint()
##            i += 1
        

add_electorate("Wills")
                
"""
Double-click on the history item or paste the command below to re-run the algorithm
"""

       
    
