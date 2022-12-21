# fonction qui ne garde qu'un point lorsque plusieurs points ont les mêmes coordonnées, puis qui ne garde qu'un point parmi les points qui sont situés à moins d'une distance_max l'un de l'autre. 
def suppress_duplicates_and_close(test_Chile_copper, distance_max):
    
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    
   
    #supprime les points identiques, garde les premiers
    points_clean = test_Chile_copper.drop_duplicates(subset = ['points'], keep='first', inplace=False, ignore_index=True)    

    #convertir les projections en 2D pour calculer des distances
    points_only = gpd.GeoDataFrame(points_clean)['points'].to_crs({'init': 'epsg:3857'})
    #poly_only = df_total_mining['geometry'].to_crs({'init': 'epsg:3857'})
    nb_points = len(points_only)
    #nb_poly = len(poly_only)

    matrix_distances_points = pd.DataFrame()
    for i in range(0,nb_points):
        new_row = points_only.distance(points_only.iloc[i]) /1000 
        matrix_distances_points = matrix_distances_points.append(new_row, ignore_index=True).round(decimals = 2)

    
    distances_points = matrix_distances_points[matrix_distances_points > 0].min()

    points2 = points_clean.drop(distances_points[distances_points < distance_max].drop_duplicates(keep='last').index, axis=0)[['localities', 'points']]
    points3 = points2.reset_index(drop = True)

    return points3


######################################################################################################################################
#Fonction qui assigne le polygone le plus proche aux points miniers. 
def add_closest_polygon(points, data_pays_mines, distance_max_mine):
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    
    polys = data_pays_mines['geometry'].to_crs({'init': 'epsg:3857'})
    points_only = gpd.GeoDataFrame(points)['points'].to_crs({'init': 'epsg:3857'})
    matrix_distances = pd.DataFrame()
    

    nb_points = len(points_only)
    
    for i in range(0,nb_points):
        new_row = polys.distance(points_only.iloc[i])/1000 
        matrix_distances = matrix_distances.append(new_row, ignore_index=True)
    
    new_col = data_pays_mines.loc[matrix_distances.idxmin(axis = 1), 'geometry'].reset_index(drop = True)

    new_col2 = data_pays_mines.loc[matrix_distances.idxmin(axis = 1), 'AREA'].reset_index(drop = True)    
    matrix_distances.idxmin(axis = 1)   

    points['polygons']= new_col 
    points['distances'] = gpd.GeoDataFrame(points)['polygons'].to_crs({'init': 'epsg:3857'}).distance(gpd.GeoDataFrame(points)['points'].to_crs({'init': 'epsg:3857'}))/1000
    points['AREA'] = new_col2
    points_with_poly = points.loc[points['distances'] < distance_max_mine]
    
    #tri sur distance puis suppression derniers doublons sur colonne polys
    points_with_poly = points_with_poly.drop_duplicates(subset = 'polygons', keep='first').sort_values('distances', ascending = True)
    points_with_poly = points_with_poly.sort_index()
    
    return points_with_poly

##########################################################################################################################################
# fonction qui exécute les fonctions précédentes de façon à garder la cohérence des paramètres d'entrée.
def assign_polygons_points(test_Chile_copper, data_pays_mines, distance_max, distance_max_mine):
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    
   
    points = suppress_duplicates_and_close(test_Chile_copper, distance_max)

    points_with_poly = add_closest_polygon(points, data_pays_mines, distance_max_mine).reset_index(drop = True) 

    return points_with_poly

#########################################################################################################################################

# focntion qui reprend la fonction dans visualisation_stress_mines.py pour l'adapter au cas d'un seul minéral. 
def calcul_pourcentages_zones_mineral(scenario, df_test, df_total):
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    
    df_spec = gpd.tools.sjoin(df_test, df_total, how="left")
    
    conditions2 = [
        (df_spec[scenario] == 'No data'),
        (df_spec[scenario] == 'Low (<10%)'),
        (df_spec[scenario] == 'Low-medium (10-20%)'),
        (df_spec[scenario] == 'Medium-high (20-40%)'),
        (df_spec[scenario] == 'High (40-80%)'),
        (df_spec[scenario] == 'Extremely high (>80%)'),
        (df_spec[scenario] == 'Arid and low water use'),
        ]
    values2 = [0, 1, 2, 3, 4, 5, 6]


    df_spec['value_risk'] = np.select(conditions2, values2)

    df_test2 = df_spec.sort_values(by='value_risk', ascending = False).drop_duplicates('AREA',keep='first')

    group_bystress2 = df_test2.groupby(['value_risk']).sum()

    total_area = group_bystress2['AREA'].sum()

    area_stress = [0] * 7

    for i in range(7):
        try:
            area_stress[i] = group_bystress2.AREA[i]
        except:
            area_stress[i] = 0


    No_data = round(area_stress[0]/total_area*100,2)
    Low = round(area_stress[1]/total_area*100,2)
    Low_medium = round(area_stress[2]/total_area*100,2)
    Medium_high = round(area_stress[3]/total_area*100,2)
    High = round(area_stress[4]/total_area*100,2)
    Extremely_high = round(area_stress[5]/total_area*100,2)
    Arid = round(area_stress[6]/total_area*100,2)

    results = pd.DataFrame.from_dict({
                   'No data' : [No_data], 
                   'Low (<10%)': [Low], 
                   'Low-medium (10-20%)' : [Low_medium], 
                   'Medium-high (20-40%)' : [Medium_high], 
                   'High (40-80%)': [High], 
                   'Extremely high (>80%)': [Extremely_high], 
                   'Arid and low water use' : [Arid]}, orient = "index", columns = ['Percentage'])



    return results



