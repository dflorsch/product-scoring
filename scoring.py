from datetime import date

import pandas as pd
import numpy as np
from data import load_data, transform_data

data = load_data()
tdata = transform_data(data)

# Unique list of product groups in tdata
unique_groups = tdata['group id'].unique()

# Drop nan from unique groups list
unique_groups = unique_groups[~np.isnan(unique_groups)]

scoring_df = pd.DataFrame(columns=['Group ID', 'Group Size', 'Image Score', 'Price Score (OEM & CPT)', 'OEM Score',
                                   'CPT Score', 'Basic Data Score', 'Multi-/Doppelpack Score', 'Group Size Score',
                                   'Total Score'])

for group_id in unique_groups:
    group_df = tdata.loc[tdata['group id'] == group_id]

    # 1) Image Score
    if 'original' in group_df['image'].unique():
        image_score = (group_df['image'].value_counts()['original'] / len(group_df['image'])) * 20
        image_score = round(image_score)
    else:
        image_score = 0

    # 2) Price Score (group)

    # 3) Price Score (cpt & oem)
    oem_min = group_df[group_df['typ'] == 'Original']['vk'].min()
    cpt_min = group_df[group_df['typ'] == 'Kompatibel']['vk'].min()

    if pd.isna(cpt_min):
        price_score2 = 0
    elif pd.isna(oem_min):
        price_score2 = 0
    elif oem_min < cpt_min:
        price_score2 = -10
    else:
        price_score2 = 10

    # 4) OEM Score
    if 'Original' in group_df['typ'].unique():
        if group_df['typ'].value_counts()['Original'] >= 2:
            oem_score = 10
        else:
            oem_score = group_df['typ'].value_counts()['Original'] * 5
    else:
        oem_score = 0

    # 5) CPT Score
    if 'Kompatibel' in group_df['typ'].unique():
        if group_df['typ'].value_counts()['Kompatibel'] >= 4:
            cpt_score = 20
        else:
            cpt_score = group_df['typ'].value_counts()['Kompatibel'] * 5
    else:
        cpt_score = 0

    # 6) Basic Data Score
    count = 0
    for index, row in group_df.iterrows():
        if row['seitenleistung'] == 0 or row['farbcode'] == 0:
            count = count + 0
        else:
            count = count + 1

    try:
        data_score = (count / len(group_df)) * 20
        data_score = round(data_score)
    except ZeroDivisionError:
        data_score = 0

    # 7) Multi-/Doppelpack Score
    if 'yes' in group_df['pixi bundle (pim id)'].unique():
        if group_df['pixi bundle (pim id)'].value_counts()['yes'] >= 2:
            pack_score = 10
        else:
            pack_score = group_df['pixi bundle (pim id)'].value_counts()['yes'] * 5

    else:
        pack_score = 0

    # 8) Size of Product group
    if len(group_df) < 5:
        pg_size_score = -10
    elif len(group_df) > 20:
        pg_size_score = -10
    else:
        pg_size_score = 0

    # 9) Total Score
    total_score = image_score + price_score2 + oem_score + cpt_score + data_score + pack_score + pg_size_score

    # Create dict and append scores to DataFrame scoring_df
    temp_dict = [{'Group ID': int(group_id),
                  'Group Size': len(group_df),
                  'Image Score': image_score,
                  'Price Score (OEM & CPT)': price_score2,
                  'OEM Score': oem_score,
                  'CPT Score': cpt_score,
                  'Basic Data Score': data_score,
                  'Multi-/Doppelpack Score': pack_score,
                  'Group Size Score': pg_size_score,
                  'Total Score': total_score}]

    temp_df = pd.DataFrame.from_dict(temp_dict)

    scoring_df = pd.concat([scoring_df, temp_df])

scoring_df.to_csv(f'data/product_scoring_{date.today()}.csv', index=False)

