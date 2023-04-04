import re

import pandas as pd
import numpy as np
from pandas import DataFrame


def load_data() -> DataFrame:
    # product data
    product_path = 'data/products.csv'
    product_df = pd.read_csv(product_path, sep=';')

    # image data
    image_path = 'data/oxids_with_images.csv'
    image_df = pd.read_csv(image_path, sep=',')
    image_df = image_df.rename(columns={"oxid": "Oxid ID", "image_url": "image"})

    # price data
    price_path = 'data/sales_prices_feed_production.csv'
    price_df = pd.read_csv(price_path, sep=';')
    price_df = price_df[['oxid', 'tonerpartner.de VK']]
    price_df = price_df.rename(columns={"oxid": "Oxid ID", "tonerpartner.de VK": "vk"})

    # Merge DataFrames on Oxid ID
    input_df = pd.merge(product_df, image_df, on='Oxid ID', how='outer')
    input_df = pd.merge(input_df, price_df, on='Oxid ID', how='outer')

    # Delete unnecessary rows (not in stock)
    input_df = input_df[input_df['Pixi aktiviert'] == True]
    input_df = input_df[input_df['Deaktiviert'] == False]
    # Delete unnecessary rows (no vk)
    input_df['vk'] = input_df['vk'].fillna(0)
    input_df = input_df[input_df['vk'] != 0]

    # Drop unnecessary columns
    input_df = input_df[['Oxid ID', 'Pixi Bundle (PIM ID)', 'Seitenleistung', 'Farbcode', 'Typ', 'Group ID', 'image',
                         'vk']]

    # Set all column names lowercase
    input_df = input_df.rename(columns=str.lower)

    return input_df


def transform_data(input_df: DataFrame) -> DataFrame:
    # Doppel- / Multipack
    input_df['pixi bundle (pim id)'] = input_df['pixi bundle (pim id)'].fillna("no")
    input_df['pixi bundle (pim id)'] = np.where(input_df['pixi bundle (pim id)'] != "no", "yes", "no")

    # image check
    regex = '.*/(?P<numbers_only>\d+)\.jpeg$'
    input_df['image'] = input_df['image'].replace(to_replace=f'{regex}', value='original', regex=True)
    input_df['image'] = input_df['image'].fillna('no image')
    input_df['image'] = np.where(input_df['image'] != "original", "fake", "original")

    # Seitenleistung
    input_df['seitenleistung'] = input_df['seitenleistung'].fillna(0)

    # Farbcode
    input_df['farbcode'] = input_df['farbcode'].fillna(0)

    return input_df
