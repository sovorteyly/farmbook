from preprocessed_file import *
from navigation import make_sidebar

make_sidebar()
st.title("Available Product for Selected Area")

def filter_dataframe(selected_province_id, selected_district_id, selected_commune_id, selected_village_id):
    filtered_df = processed_farmer_yield_df[
        (processed_farmer_yield_df['adr_province_id'] == selected_province_id) &
        (processed_farmer_yield_df['adr_district_id'] == selected_district_id) &
        (processed_farmer_yield_df['adr_commune_id'] == selected_commune_id) &
        (processed_farmer_yield_df['adr_village_id'] == selected_village_id)
    ]
    return filtered_df

def filter_and_plot(selected_province_id, selected_district_id, selected_commune_id, selected_village_id, selected_area_name):
    # Filter dataframe based on selected area
    filtered_df = filter_dataframe(selected_province_id, selected_district_id, selected_commune_id, selected_village_id)
    
    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        st.warning("No data available for the selected area.")
        return
    
    try:
        # Group by product_id and calculate the sum of converted_result_in_kg
        product_sum_df = filtered_df.groupby('product_id')['converted_result_in_kg'].sum().reset_index()

        # Merge product_sum_df with filtered_df to get the farmer_product_name
        product_sum_df = product_sum_df.merge(filtered_df[['product_id', 'farmer_product_name']].drop_duplicates(), on='product_id', how='left')

        # Sort product_sum_df based on the 'converted_result_in_kg' column in ascending order
        product_sum_df = product_sum_df.sort_values(by='converted_result_in_kg')
        title = f'Total Yield in kg for Each Product in {selected_area_name["province_name"]}, {selected_area_name["district_name"]}, {selected_area_name["commune_name"]}, {selected_area_name["village_name"]}'
        # Create bar chart using Plotly
        fig = px.bar(product_sum_df, 
                     x='farmer_product_name', 
                     y='converted_result_in_kg', 
                     labels={'farmer_product_name': 'Farmer Product Name', 'converted_result_in_kg': 'Converted Result (kg)'},
                     title=title
                    )

        # Explicitly set x-axis data type to categorical
        fig.update_xaxes(type='category')

        # Display the plot using Streamlit
        st.plotly_chart(fig)
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        

def count_farmer_outlets(selected_province_id, selected_district_id, selected_commune_id, selected_village_id):
    # Filter dataframe based on selected area
    filtered_df = filter_dataframe(selected_province_id, selected_district_id, selected_commune_id, selected_village_id)
    
    # Group by product_id and count the number of unique farmer outlets
    outlet_counts = filtered_df.groupby('product_id')['farmer_outlet_id'].nunique().reset_index()
    
    return outlet_counts

def plot_outlet_counts(selected_province_id, selected_district_id, selected_commune_id, selected_village_id):
    try:
        # Count farmer outlets for each product in the selected area
        outlet_counts = count_farmer_outlets(selected_province_id, selected_district_id, selected_commune_id, selected_village_id)
        
        # Check if the outlet_counts DataFrame is empty
        if outlet_counts.empty:
            st.warning("No data available for the selected area.")
            return
        
        # Merge with farmer product names
        outlet_counts = outlet_counts.merge(processed_farmer_yield_df[['product_id', 'farmer_product_name']].drop_duplicates(), on='product_id', how='left')

        # Create bar chart using Plotly
        fig = px.bar(outlet_counts, 
                     x='farmer_product_name', 
                     y='farmer_outlet_id', 
                     labels={'farmer_product_name': 'Farmer Product Name', 'farmer_outlet_id': 'Number of Farmer Outlets'},
                     title='Number of Farmer Outlets for Each Product'
                    )

        # Explicitly set x-axis data type to categorical
        fig.update_xaxes(type='category')

        # Display the plot using Streamlit
        st.plotly_chart(fig)
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        
def plot_land_usage(selected_province_id, selected_district_id, selected_commune_id, selected_village_id):
    try:
        # Filter dataframe based on selected area
        filtered_df = filter_dataframe(selected_province_id, selected_district_id, selected_commune_id, selected_village_id)
        
        # Check if the filtered DataFrame is empty
        if filtered_df.empty:
            st.warning("No data available for the selected area.")
            return
        
        # Group by product_id and calculate the sum of product_land
        land_usage_df = filtered_df.groupby('product_id')['converted_land_in_m^2'].sum().reset_index()

        # Merge with farmer product names
        land_usage_df = land_usage_df.merge(processed_farmer_yield_df[['product_id', 'farmer_product_name']].drop_duplicates(), on='product_id', how='left')

        # Create bar chart using Plotly
        fig = px.bar(land_usage_df, 
                     x='farmer_product_name', 
                     y='converted_land_in_m^2', 
                     labels={'farmer_product_name': 'Farmer Product Name', 'converted_land_in_m^2': 'Land Usage (m^2)'},
                     title='Land Usage for Each Product'
                    )

        # Explicitly set x-axis data type to categorical
        fig.update_xaxes(type='category')

        # Display the plot using Streamlit
        st.plotly_chart(fig)
    
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.write(processed_farmer_yield_df)

st.write("Choose province `ត្បូងឃ្មុំ`, district `ក្រូចឆ្មារ` ,commune `ឈូក`, and village `រួមវិញ` to see illustration")
# PROVINCE
# Get unique values of name_kh column
province_names = adr_province_df['name_kh'].unique()
selected_province_name = st.selectbox("Select Province:", province_names)
filtered_province = adr_province_df[adr_province_df['name_kh'] == selected_province_name]
selected_province_id = filtered_province['id'].iloc[0]

# DISTRICT
# Filter district dataframe based on selected province id
filtered_districts = adr_district_df[adr_district_df['adr_province_id'] == selected_province_id]
district_names = filtered_districts['name_kh'].unique()
selected_district_name = st.selectbox("Select District:", district_names)
filtered_district = filtered_districts[filtered_districts['name_kh'] == selected_district_name]
selected_district_id = filtered_district['id'].iloc[0]

# COMMUNE
filtered_communes = adr_commune_df[(adr_commune_df['adr_province_id'] == selected_province_id) &
                                   (adr_commune_df['adr_district_id'] == selected_district_id)]
commune_names = filtered_communes['name_kh'].unique()
selected_commune_name = st.selectbox("Select Commune:", commune_names)
filtered_selected_commune = filtered_communes[filtered_communes['name_kh']== selected_commune_name]
selected_commune_id = filtered_selected_commune['id'].iloc[0]

# VILLAGE
filtered_villages = adr_village_df[(adr_village_df['adr_province_id'] == selected_province_id) &
                                   (adr_village_df['adr_district_id'] == selected_district_id) &
                                   (adr_village_df['adr_commune_id'] == selected_commune_id)
                                ]
village_names = filtered_villages['name_kh'].unique()
selected_village_name = st.selectbox("Select Commune:", village_names)
filtered_selected_village = filtered_villages[filtered_villages['name_kh']== selected_village_name]
selected_village_id = filtered_selected_village['id'].iloc[0]

# selected_province_id = 25
# selected_district_id = 198
# selected_commune_id = 1590
# selected_village_id = 13588

selected_area_name = get_selected_area_names(selected_province_id, selected_district_id, selected_commune_id, selected_village_id)
         
filter_and_plot(selected_province_id, selected_district_id, selected_commune_id, selected_village_id, selected_area_name)

plot_outlet_counts(selected_province_id, selected_district_id, selected_commune_id, selected_village_id)

plot_land_usage(selected_province_id, selected_district_id, selected_commune_id, selected_village_id)