# fonction qui nettoie les chaînes de caractères (voir Main). 
def clean_strings(df):

    import sys
    import subprocess    
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'unidecode'])
    from unidecode import unidecode
    import re
    from re import sub
    s = df[["localities", "points"]]
    s['t1'] = s["localities"].apply(unidecode).str.lower()  # enleve les caractères spéciaux et accents
    s['t2'] = s["t1"].str.replace("[^abcdefghijklmnopqrstuvwxyz ]", "").str.strip(' ') # ne conserve que les caractères en minuscule et les espaces
    return s


##############################################################################################################################
# fonction qui ajoute les distances minimales entre les chaînes de caractères et les points. 
def add_columns_with_Lev_distances(s):
    import sys
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Levenshtein'])
    import pandas as pd
    import numpy as np
    import geopandas as gpd
    
    from Levenshtein import distance as Lev_dist
    
    nb_str = len(s['t2'])
    matrix_distances_lev = np.zeros((nb_str,nb_str),dtype=np.int)
                                
    for i in range(0,nb_str):
      for j in range(0,nb_str):
          matrix_distances_lev[i,j] = Lev_dist(s['t2'].iloc[i],s['t2'].iloc[j])
    matrix_distances_str = pd.DataFrame(matrix_distances_lev)


    s2 = pd.concat([matrix_distances_str[matrix_distances_str > 0].min(),s], axis = 1)

    s2['duplicated']=s['points'].duplicated()
    s2['dupli']= np.where(s2['duplicated']== True, 1, 0)
    s2.rename(columns = {0:'lev_dist'}, inplace = True)
    
    
    
    points_only = gpd.GeoDataFrame(s2)['points'].to_crs({'init': 'epsg:3857'})
    
    nb_points = len(points_only)

    matrix_distances_points = pd.DataFrame()
    for i in range(0,nb_points):
        new_row = points_only.distance(points_only.iloc[i]) /1000 
        matrix_distances_points = matrix_distances_points.append(new_row, ignore_index=True).round(decimals = 2)

    
    distances_points = matrix_distances_points[matrix_distances_points > 0].min()
    s3 = pd.concat([s2,distances_points], axis = 1)
    s3.rename(columns = {0:'dist_points'}, inplace = True)
    
    return s3[['localities','points','dupli','lev_dist','dist_points']]