
    
def import_donnees():
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    import zipfile
    import os
    import glob
    import io
    from io import BytesIO
    from zipfile import ZipFile
    from urllib.request import urlopen
    
    # parts de production minéraux, par pays
    url_csv = "https://www.world-mining-data.info/wmd/downloads/XLS/6.5.%20Share_of_World_Mineral_Production_2020_by_Countries.xlsx"
    shares_prod_2020 = pd.ExcelFile(url_csv)
    
    # data limites des pays à partir de geopandas
    countries = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # attention correspondance pays
    dico_correspondance_pays = {'Afghanistan':"", 'Albania': 'Albania', 'Algeria': 'Algeria', 'Angola': 'Angola', 'Antarctica':"", 'Argentina': 'Argentina', 'Armenia': 'Armenia','Australia': 'Australia', 'Austria': 'Austria', 'Azerbaijan': 'Azerbaijan', 'Bahamas':"", 'Bangladesh': 'Bangladesh','Bolivia': 'Bolivia', 'Belgium':"", 'Belize':"", 'Benin':"", 'Bosnia and Herz.': 'Bosnia and Herzegovina', 'Botswana': 'Botswana', 'Brazil': 'Brazil', 'Brunei':"", 'Bulgaria': 'Bulgaria', "Côte d'Ivoire": 'Côte D’Ivoire', 'Burkina Faso': 'Burkina Faso', 'Burundi':"", 'Cambodia':"", 'Cameroon':"", 'Canada': 'Canada', 'Central African Rep.':"", 'Chad':"", 'Chile': 'Chile', 'China': 'China', 'Colombia': 'Colombia', 'Costa Rica': 'Costa Rica', 'Croatia':"", 'Cuba': 'Cuba', 'Cyprus': 'Cyprus', 'Czechia': 'Czechia','Dem. Rep. Congo': 'Democratic Republic of The Congo','Dominican Rep.': 'Dominican Republic','Congo':"", 'Denmark':"", 'Djibouti':"", 'Ecuador': 'Ecuador', 'El Salvador':"",'Egypt': 'Egypt', 'Eq. Guinea':"", 'Eritrea': 'Eritrea', 'Estonia':"", 'Ethiopia': 'Ethiopia','Fiji': 'Fiji', 'Falkland Is.':"", 'Finland': 'Finland', 'Fr. S. Antarctic Lands':"", 'France': 'France', 'Gabon': 'Gabon', 'Gambia':"", 'Georgia': 'Georgia', 'Germany': 'Germany', 'Ghana': 'Ghana','Greece': 'Greece', 'Guatemala': 'Guatemala', 'Guinea': 'Guinea', 'Guinea-Bissau': 'Guinea-Bissau', 'Haiti':"",'Guyana': 'Guyana','Honduras': 'Honduras', 'Hungary': 'Hungary', 'Iceland':"", 'India': 'India', 'Indonesia': 'Indonesia', 'Iran': 'Iran', 'Iraq': 'Iraq','Ireland': 'Ireland', 'Israel': 'Israel', 'Italy': 'Italy','Jamaica': 'Jamaica', 'Japan': 'Japan', 'Jordan': 'Jordan', 'Kazakhstan': 'Kazakhstan', 'Kenya': 'Kenya','Kyrgyzstan': 'Kyrgyzstan', 'Kosovo':"", 'Kuwait':"", 'Laos': 'Laos', 'Latvia':"", 'Lebanon':"", 'Lesotho': 'Lesotho','Liberia': 'Liberia', 'Libya':"", 'Lithuania':"", 'Madagascar': 'Madagascar', 'Malawi': 'Malawi', 'Malaysia': 'Malaysia','Mali': 'Mali', 'Mauritania': 'Mauritania', 'Mexico': 'Mexico', 'Moldova':"", 'Mongolia': 'Mongolia','Montenegro': 'Montenegro', 'Morocco': 'Morocco', 'Mozambique': 'Mozambique', 'Myanmar': 'Myanmar/Burma', 'N. Cyprus':"", 'Namibia': 'Namibia', 'Nepal':"", 'Netherlands':"", 'New Caledonia': 'New Caledonia', 'New Zealand': 'New Zealand', 'Nicaragua': 'Nicaragua', 'Niger': 'Niger','North Korea': 'North Korea', 'Nigeria':"", 'North Macedonia': 'North Macedonia', 'Norway': 'Norway', 'Oman': 'Oman', 'Pakistan': 'Pakistan', 'Panama': 'Panama','Papua New Guinea': 'Papua New Guinea', 'Paraguay':"", 'Peru': 'Peru','Philippines': 'Philippines', 'Poland': 'Poland', 'Portugal': 'Portugal', 'Puerto Rico':"",'Romania': 'Romania', 'Qatar':"", 'Russia': 'Russian Federation','Rwanda': 'Rwanda', 'S. Sudan':"",'Saudi Arabia': 'Saudi Arabia', 'Senegal': 'Senegal', 'Serbia': 'Serbia', 'Sierra Leone': 'Sierra Leone','Slovakia': 'Slovakia', 'Slovenia': 'Slovenia', 'Solomon Is.': 'Solomon Islands', 'Somalia':"",'South Africa': 'South Africa', 'Somaliland':"", 'South Korea': 'South Korea', 'Spain': 'Spain', 'Sri Lanka':"", 'Sudan': 'Sudan', 'Suriname': 'Suriname', 'Sweden': 'Sweden', 'Switzerland':"", 'Syria':"", 'Taiwan':"", 'Tajikistan': 'Tajikistan', 'Tanzania': 'United Republic of Tanzania', 'Thailand': 'Thailand', 'Timor-Leste':"", 'Trinidad and Tobago':"", 'Tunisia': 'Tunisia', 'Turkey': 'Turkey', 'Turkmenistan':"", 'Uganda': 'Uganda', 'Ukraine': 'Ukraine','United Kingdom':'United Kingdom','United Arab Emirates': 'United Arab Emirates','United States of America': 'United States', 'Uruguay': 'Uruguay', 'Uzbekistan': 'Uzbekistan', 'Venezuela': 'Venezuela', 'Vietnam': 'Vietnam', 'W. Sahara': 'Western Sahara', 'Yemen':"", 'Zambia': 'Zambia', 'Zimbabwe': 'Zimbabwe','Belarus':"",'Bhutan':"",'eSwatini':"",'Greenland':"",'Luxembourg':"",'Palestine':"",'Togo':"",'Vanuatu':""}
    
    # Importation données zones minières, à partir de Maus, V., Giljum, S., Gutschlhofer, J. et al. A global-scale data set of mining areas. Sci Data 7, 289 (2020). https://doi.org/10.1038/s41597-020-00624-w

    file = "global_mining_polygons_v1.gpkg"
    resp = urlopen("https://store.pangaea.de/Publications/Maus-etal_2020/Global_mining.zip")
    myzip = ZipFile(BytesIO(resp.read()))

    df = gpd.read_file(myzip.open('global_mining_polygons_v1.gpkg'))
    # correction données : assignation des polygones miniers aux bons pays (voir ex Pologne)
    df =  gpd.tools.sjoin(df, countries, how="left")[['ISO3_CODE', 'COUNTRY_NAME', 'AREA', 'geometry', 'name', 'iso_a3']]
    
    # importation data stress hydrique du WRI
    url_stress = "https://wri-public-data.s3.amazonaws.com/resourcewatch/wat_006_projected_water_stress.zip"
    df_stress = gpd.read_file(url_stress)
    
    #plusieurs méthodes permettent de fusionner les différentes données. Ici on utilise df.overlay pour obtenir pour chaque polygone issu du WRI sa localisation dans le monde. 
    df_total = df_stress.overlay(countries, how="intersection")
    
    #Ici on crée un dataframe qui associe à chaque polygone minier ses données de stress hydrique. La méthode crée quelques doublons, pour les polygones miniers qui sont à cheval sur plusieurs polygones de stress hydrique ou plusieurs pays, mais pour les usages de df_total_mining cela n'a pas d'importance. Par contre dans la fonction calcul_pourcentages_zones on supprime ces doublons. 
    df_total_mining = gpd.tools.sjoin(df, df_total, how="left")

    return shares_prod_2020, countries, dico_correspondance_pays, df, df_stress, df_total, df_stress, df_total_mining
    
    
    
    
    
    
    
    
    
    