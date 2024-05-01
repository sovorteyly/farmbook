import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def get_csv_folder_path(relative_folder_path):
    """
    Construct the absolute path to the folder containing CSV files.
    
    Args:
    - relative_folder_path (str): The relative path to the folder containing CSV files.
    
    Returns:
    - str: The absolute path to the folder containing CSV files.
    """
    # Get the current working directory
    current_directory = os.getcwd()

    # Construct the absolute path to the folder using os.path.join
    folder_path = os.path.join(current_directory, relative_folder_path)
    
    return folder_path

def read_csv_files(folder_path):
    """
    Read all CSV files in the specified folder and return a dictionary of DataFrames.
    
    Args:
    - folder_path (str): The path to the folder containing CSV files.
    
    Returns:
    - dict: A dictionary where keys are DataFrame names (extracted from file names) and values are DataFrames.
    """
    # Create an empty dictionary to store DataFrames
    dfs = {}

    # Iterate through the files in the folder
    for file_name in os.listdir(folder_path): 
        # Check if the file is a CSV file
        if file_name.endswith(".csv"):
            # Construct the absolute path to the CSV file
            file_path = os.path.join(folder_path, file_name)
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            # Extract the name of the DataFrame from the file name
            df_name = os.path.splitext(file_name)[0]
            # Store the DataFrame in the dictionary
            dfs[df_name] = df
    
    return dfs

selected_columns_dict = {
    'adr_communes': ['id', 'adr_province_id', 'adr_district_id', 'code', 'name_kh', 'name_en', 'type'], 
    'adr_districts': ['id', 'adr_province_id', 'code', 'name_kh', 'name_en', 'type'], 
    'adr_province': ['id', 'code', 'name_kh', 'name_en', 'type'], 
    'adr_villages': ['id', 'adr_province_id', 'adr_district_id', 'adr_commune_id', 'code', 'name_kh', 'name_en'], 
    'products': ['id', 'name', 'description', 'product_group_id'], 
    'product_groups': ['id', 'name', 'description', 'parent_id', 'has_child'], 
    'buyer_demands': ['id', 'buyer_product_id', 'product_id', 'buyer_outlet_id', 'quantity', 'product_unit_id'], 
    'buyer_products': ['id', 'name', 'product_id', 'buyer_outlet_id', 'product_name'], 
    'buyer_outlets': ['id', 'company_name', 'adr_province_id', 'adr_district_id', 'adr_commune_id', 'adr_village_id'], 
    'farmer_products': ['id', 'name', 'product_id', 'farmer_outlet_id', 'product_name', 'description'],
    'farmer_outlets': ['id', 'name', 'adr_village_id', 'adr_commune_id', 'adr_district_id', 'adr_province_id', 'parent_id', 'is_group', 'producer_group_name'],
    'farmer_yields': ['id', 'farmer_product_id', 'farmer_outlet_id', 'farmer_product_name', 'predicted_result', 'predicted_result_name', 'predicted_result_unit_id', 'product_land', 'product_land_name', 'product_land_unit_id', 'collecting_result_date', 'collecting_result_duration'],
}



def merge_and_select_columns(farmer_product_df, products_df, product_groups_df, farmer_outlets_df):
    """
    Merge multiple DataFrames and select specific columns to create the final DataFrame.
    
    Args:
    - farmer_product_df (pd.DataFrame): DataFrame containing farmer product information.
    - products_df (pd.DataFrame): DataFrame containing product information.
    - product_groups_df (pd.DataFrame): DataFrame containing product group information.
    - farmer_outlets_df (pd.DataFrame): DataFrame containing farmer outlet information.
    - adr_village_df (pd.DataFrame): DataFrame containing village information.
    
    Returns:
    - pd.DataFrame: The final DataFrame after merging and selecting columns.
    """
    # Merge farmer_product_df with products_df to get product group information
    merged_df = pd.merge(farmer_product_df, products_df[['id', 'product_group_id']], 
                        left_on='product_id', right_on='id', how='left')
    merged_df.drop('id_y', axis=1, inplace=True)
    
    # Merge with product_groups_df to get product group names
    merged_df = pd.merge(merged_df, product_groups_df[['id', 'name']],
                        left_on='product_group_id', right_on='id', how='left')
    merged_df.drop('id', axis=1, inplace=True)
    merged_df.rename(columns={'name': 'product_group_name'}, inplace=True)
    
    # Merge with farmer_outlets_df to get outlet location information
    merged_df = pd.merge(merged_df, farmer_outlets_df[['id', 'name', 'adr_village_id', 'adr_commune_id', 'adr_district_id', 'adr_province_id']], 
                        left_on='farmer_outlet_id', right_on='id', how='left')
    merged_df.drop('id', axis=1, inplace=True)
    merged_df.rename(columns={'id_x': 'id'}, inplace=True)
    merged_df.rename(columns={'name': 'farmer_outlet_name'}, inplace=True)
    merged_df.drop('name_x', axis=1, inplace=True)
    merged_df.rename(columns={'name_y': 'product_group_name'}, inplace=True)
    
    return merged_df

# Define function for unit conversion to kilograms
def convert_to_unit(value, unit_id):
    if unit_id == 10:
        return value * 1000  # Convert tons to kilograms
    elif unit_id == 11:
        return value  # Already in kilograms
    else:
        return None  # Handle unknown unit IDs
    
    # Define function for unit conversion to square meters
def convert_to_square_meter(value, unit_id):
    if unit_id == 1: 
        return value * 10000
    elif unit_id == 2: 
        return value * 100
    elif unit_id == 3: 
        return value * 1000000
    elif unit_id == 4: 
        return value
    else: 
        return None

def process_farmer_yield_df(farmer_yield_df, merged_df):
    """
    Process the farmer_yield_df DataFrame by merging, column renaming, and unit conversion.
    
    Args:
    - farmer_yield_df (pd.DataFrame): DataFrame containing farmer yield information.
    - merged_df (pd.DataFrame): DataFrame containing merged information from other DataFrames.
    
    Returns:
    - pd.DataFrame: The processed DataFrame after merging, column renaming, and unit conversion.
    """
    # Merge farmer_yield_df with merged_df
    farmer_yield_df = pd.merge(farmer_yield_df, merged_df[['id', 'farmer_outlet_name','product_id', 'product_group_id', 'product_group_name', 'adr_village_id', 'adr_commune_id', 'adr_district_id', 'adr_province_id']],
                              left_on='farmer_product_id', right_on='id', how='left')
    farmer_yield_df.drop('id_y', axis=1, inplace=True)
    farmer_yield_df.rename(columns={'id_x': 'id'}, inplace=True)
    
    # Apply unit conversion functions
    farmer_yield_df['converted_result_in_kg'] = farmer_yield_df.apply(lambda row: convert_to_unit(row['predicted_result'], row['predicted_result_unit_id']), axis=1)
    farmer_yield_df['converted_land_in_m^2'] = farmer_yield_df.apply(lambda row: convert_to_square_meter(row['product_land'], row['product_land_unit_id']), axis=1)
    
    return farmer_yield_df

def get_selected_area_names(selected_province_id, selected_district_id, selected_commune_id, selected_village_id):
    selected_names = {}
    
    selected_names['province_name'] = adr_province_df.loc[adr_province_df['id'] == selected_province_id, 'name_kh'].iloc[0]
    selected_names['district_name'] = adr_district_df.loc[adr_district_df['id'] == selected_district_id, 'name_kh'].iloc[0]
    selected_names['commune_name'] = adr_commune_df.loc[adr_commune_df['id'] == selected_commune_id, 'name_kh'].iloc[0]
    selected_names['village_name'] = adr_village_df.loc[adr_village_df['id'] == selected_village_id, 'name_kh'].iloc[0]
    
    return selected_names



# Reading file 
relative_folder_path = "csv_v2"
folder_path = get_csv_folder_path(relative_folder_path)
dfs = read_csv_files(folder_path)

# Reading all dataframe
products_df = dfs['products'][selected_columns_dict['products']]
products_group_df = dfs['product_groups'][selected_columns_dict['product_groups']]
farmer_outlets_df = dfs['farmer_outlets'][selected_columns_dict['farmer_outlets']]
farmer_product_df = dfs['farmer_products'][selected_columns_dict['farmer_products']]
farmer_yield_df = dfs['farmer_yields'][selected_columns_dict['farmer_yields']]

adr_village_df = dfs['adr_villages'][selected_columns_dict['adr_villages']]
adr_commune_df = dfs['adr_communes'][selected_columns_dict['adr_communes']]
adr_district_df = dfs['adr_districts'][selected_columns_dict['adr_districts']]
adr_province_df = dfs['adr_provinces'][selected_columns_dict['adr_province']]

# Merging necessary df 
farmer_product_detail_df = merge_and_select_columns(farmer_product_df, products_df, products_group_df, farmer_outlets_df)
processed_farmer_yield_df = process_farmer_yield_df(farmer_yield_df, farmer_product_detail_df)


