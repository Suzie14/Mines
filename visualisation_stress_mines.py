

### choix scénario de stress hydrique et codes couleurs pour visualisations
def attribute_colors_to_stress(df_total,scenario):  
    import pandas as pd
    import geopandas as gpd
    import numpy as np

    
    conditions = [
        (df_total[scenario] == 'No data'),
        (df_total[scenario] == 'Low (<10%)'),
        (df_total[scenario] == 'Low-medium (10-20%)'),
        (df_total[scenario] == 'Medium-high (20-40%)'),
        (df_total[scenario] == 'High (40-80%)'),
        (df_total[scenario] == 'Extremely high (>80%)'),
        (df_total[scenario] == 'Arid and low water use'),
        ]
    values = ['grey', 'yellow', 'gold', 'orange','darkorange',"orangered", 'maroon']
    df_total['Color'] = np.select(conditions, values) #ajoute colonne avec couleurs dans le dataframe
    return df_total

#######################################################################################################################


# Cette fonction permet d'associer des numéros à chaque valeur de stress, ce qui permet notamment de trier les valeurs dans un dataframe.
def attribrute_stress_values(pays,scenario, df_total_mining):
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    conditions2 = [
        (df_total_mining[scenario] == 'No data'),
        (df_total_mining[scenario] == 'Low (<10%)'),
        (df_total_mining[scenario] == 'Low-medium (10-20%)'),
        (df_total_mining[scenario] == 'Medium-high (20-40%)'),
        (df_total_mining[scenario] == 'High (40-80%)'),
        (df_total_mining[scenario] == 'Extremely high (>80%)'),
        (df_total_mining[scenario] == 'Arid and low water use'),
        ]
    values2 = [0, 1, 2, 3, 4, 5, 6]
    
    df_total_mining['value_risk'] = np.select(conditions2, values2)
    
    #Ensuite on trie les valeurs et on supprime les polygones en doublons, de sorte à garder le niveau de stress le plus pessimiste pour la zone.
    df_test = df_total_mining.sort_values(by='value_risk', ascending = False).drop_duplicates('AREA',keep='first')
    
    if pays=="World":
        df_clean_pays2 = df_test
        
    else: 
        df_clean_pays2 = df_total_mining.loc[df_total_mining['name_left'] == pays]

    return df_clean_pays2


###################################################################################################################



def calcul_pourcentages_zones(pays,scenario, df_total_mining):
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    
    #Voir fonction ci-dessous pour la suppression des doublons et l'affectation de valeurs numériques au scénario
    df_clean_pays = attribrute_stress_values(pays,scenario, df_total_mining)

    grouped_bystress_pays = df_clean_pays.groupby(['value_risk']).sum()

    total_area = grouped_bystress_pays['AREA'].sum()

    area_stress = [0] * 7

    #Cette boucle permet de réaliser le calcul même s'il n'y a pas de zones dans certains paramètres de stress, dans ce cas la zone est de 0 km². 
    for i in range(7):
        try:
            area_stress[i] = grouped_bystress_pays.AREA[i]
        except:
            area_stress[i] = 0


    No_data = round(area_stress[0]/total_area*100,2)
    Low = round(area_stress[1]/total_area*100,2)
    Low_medium = round(area_stress[2]/total_area*100,2)
    Medium_high = round(area_stress[3]/total_area*100,2)
    High = round(area_stress[4]/total_area*100,2)
    Extremely_high = round(area_stress[5]/total_area*100,2)
    Arid = round(area_stress[6]/total_area*100,2)

    results_agregate_pays = pd.DataFrame.from_dict({
                       'No data' : [No_data], 
                       'Low (<10%)': [Low], 
                       'Low-medium (10-20%)' : [Low_medium], 
                       'Medium-high (20-40%)' : [Medium_high], 
                       'High (40-80%)': [High], 
                       'Extremely high (>80%)': [Extremely_high], 
                       'Arid and low water use' : [Arid]}, orient = "index", columns = ['Percentage'])

    return results_agregate_pays


##################################################################################################################



# fonction qui permet, à partir des données mondiales de production, d'extraire de chaque onglet pour un pays sa production en tonnes, sa part de marché mondiale et qui calcule le pourcentage des extractions en volume par type de minéral.
def shares_prod_country(pays, shares_prod_2020):
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    
    df_shares_country = {}

    dict_of_df = {}
    i = 0

    for sheet_name in shares_prod_2020.sheet_names:

            df_provisoire = pd.read_excel(shares_prod_2020, sheet_name, header = 0)
            df_provisoire.columns=df_provisoire.iloc[0]
            dict_of_df["df_{}".format(sheet_name)] = pd.read_excel(shares_prod_2020, sheet_name, header = 1)[['Country','Production 2020', 'Share in %']]

            key = "df_{}".format(sheet_name)

            try: 
                df_shares_country[sheet_name] = dict_of_df[key].loc[dict_of_df[key]['Country'] == pays].values.tolist()
            except:
                pass 

    non_metric_t = ['Rhenium', 'Gold', 'Palladium', 'Platinum', 'Rhodium', 'Silver', 'Diamonds (Gem)', 'Diamonds (Ind)','Natural Gas']
    df_shares_country2 = {k:v for k,v in df_shares_country.items() if k not in non_metric_t}
    df_shares_country2
    new_dict = {k:v for k,v in df_shares_country2.items() if v}
    new_dict

    res1 = pd.DataFrame.from_dict(new_dict, orient = "index",columns = ['donnees'])
    res2 = pd.DataFrame(res1['donnees'].tolist(), columns=['country','Production_in_t','Share_world_production'], index=res1.index)
    res2['Share_world_production']=res2['Share_world_production'].round(decimals = 2)
    res2['%_of_extractions'] = round(res2['Production_in_t'] / res2['Production_in_t'].sum()*100,2)

    res2 = res2[['country','Production_in_t','%_of_extractions','Share_world_production']]
    return(res2)


#######################################################################################################################################
# permet de visualiser le stress hydrique dans le monde.
def visualisation_zones_stress_monde(scenario, df_total):
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    df_print = attribute_colors_to_stress(df_total,scenario)
    base_graphe = df_print.plot(color=df_print['Color'], figsize=(20, 20), legend = True ) 
    plt.title("Water stress in the world (scenario: "+scenario+")")
    grey_patch = mpatches.Patch(color='grey', label='No Data')
    yellow_patch = mpatches.Patch(color='yellow', label='Low (<10%)')
    gold_patch = mpatches.Patch(color='gold', label='Low-Medium (10-20%)')
    orange_patch = mpatches.Patch(color='orange', label='Medium-High (20-40%)')
    darkorange_patch = mpatches.Patch(color='darkorange', label='High(40-80%)')
    orangered_patch = mpatches.Patch(color='orangered', label='Extremely high(>80%)')
    maroon_patch = mpatches.Patch(color='maroon', label='Arid and low water use')
    plt.legend(handles=[grey_patch, yellow_patch,gold_patch,orange_patch,darkorange_patch,orangered_patch,maroon_patch], loc ="lower left")
    
    return

#######################################################################################################################################
# permet de visualiser les zones minières et le stress hydrique pour un pays donné.
def visualisation_zones_pays(pays,scenario, df, df_total):
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    data_country = df.loc[df['name'] == pays]
    #data_country.crs # => WGS84 Latitude/Longitude: "EPSG:4326"
    
    data_pays = df_total.loc[df_total['name'] == pays]
    df_print = attribute_colors_to_stress(df_total,scenario)
    df_print = df_print.loc[df_print['name'] == pays]
    base_graphe = df_print.plot(color=df_print['Color'], figsize=(20, 20)) 
    data_country.plot(ax=base_graphe, color = "limegreen")
    plt.title("Water stress and mines in"+pays+ "(scenario: "+scenario+")")


#     fig, ax = plt.subplots()
    green_patch = mpatches.Patch(color='limegreen', label='Mines')
    grey_patch = mpatches.Patch(color='grey', label='No Data')
    yellow_patch = mpatches.Patch(color='yellow', label='Low (<10%)')
    gold_patch = mpatches.Patch(color='gold', label='Low-Medium (10-20%)')
    orange_patch = mpatches.Patch(color='orange', label='Medium-High (20-40%)')
    darkorange_patch = mpatches.Patch(color='darkorange', label='High(40-80%)')
    orangered_patch = mpatches.Patch(color='orangered', label='Extremely high(>80%)')
    maroon_patch = mpatches.Patch(color='maroon', label='Arid and low water use')
    plt.legend(handles=[green_patch, grey_patch, yellow_patch,gold_patch,orange_patch,darkorange_patch,orangered_patch,maroon_patch], loc ="upper left")
    
    
    return

