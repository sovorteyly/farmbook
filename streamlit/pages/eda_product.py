from preprocessed_file import *
from navigation import make_sidebar

make_sidebar()
st.title("Available Area for Selected Product")

def get_area_totals(selected_product_name):
    # Get selected product ID
    selected_product_id = products_df.loc[products_df['name'] == selected_product_name, 'id'].iloc[0]
    
    # Filter data for the selected product
    filtered_selected_product_id = processed_farmer_yield_df[processed_farmer_yield_df['product_id'] == selected_product_id]
    
    # Aggregate converted_result_in_kg values for each area
    area_totals = filtered_selected_product_id.groupby(['adr_province_id', 'adr_district_id', 'adr_commune_id', 'adr_village_id'])['converted_result_in_kg'].sum().reset_index()
    
    # Merge with province names
    area_totals = area_totals.merge(adr_province_df[['id', 'name_kh']].rename(columns={'name_kh': 'province_name'}), 
                                    left_on='adr_province_id', right_on='id', how='left')
    area_totals.drop(columns=['id'], inplace=True)
    
    # Merge with district names
    area_totals = area_totals.merge(adr_district_df[['id', 'name_kh']].rename(columns={'name_kh': 'district_name'}), 
                                    left_on='adr_district_id', right_on='id', how='left')
    area_totals.drop(columns=['id'], inplace=True)
    
    # Merge with commune names
    area_totals = area_totals.merge(adr_commune_df[['id', 'name_kh']].rename(columns={'name_kh': 'commune_name'}), 
                                    left_on='adr_commune_id', right_on='id', how='left')
    area_totals.drop(columns=['id'], inplace=True)
    
    # Merge with village names
    area_totals = area_totals.merge(adr_village_df[['id', 'name_kh']].rename(columns={'name_kh': 'village_name'}), 
                                    left_on='adr_village_id', right_on='id', how='left')
    area_totals.drop(columns=['id'], inplace=True)
    
    return area_totals

def plot_area_totals(area_totals, selected_area_level, selected_province=None, selected_district=None):
    if selected_area_level == "Province":
        fig = px.bar(area_totals.groupby('province_name')['converted_result_in_kg'].sum().reset_index(), 
                     x='province_name', y='converted_result_in_kg', 
                     labels={'province_name': 'Province', 'converted_result_in_kg': 'Total Converted Result (kg)'},
                     title='Total Converted Result in kg for Each Province'
                    )
    elif selected_area_level == "District":
        if selected_province:
            district_totals = area_totals[area_totals['province_name'] == selected_province].groupby('district_name')['converted_result_in_kg'].sum().reset_index()
            fig = px.bar(district_totals, x='district_name', y='converted_result_in_kg', 
                         labels={'district_name': 'District', 'converted_result_in_kg': 'Total Converted Result (kg)'},
                         title=f'Total Converted Result in kg for Each District in {selected_province}'
                        )
        else:
            st.warning("Please select a province.")
            return None
    elif selected_area_level == "Commune":
        if selected_province and selected_district:
            commune_totals = area_totals[(area_totals['province_name'] == selected_province) & 
                                         (area_totals['district_name'] == selected_district)].groupby('commune_name')['converted_result_in_kg'].sum().reset_index()
            fig = px.bar(commune_totals, x='commune_name', y='converted_result_in_kg', 
                         labels={'commune_name': 'Commune', 'converted_result_in_kg': 'Total Converted Result (kg)'},
                         title=f'Total Converted Result in kg for Each Commune in {selected_province}, {selected_district}'
                        )
        else:
            st.warning("Please select a province and a district.")
            return None
    elif selected_area_level == "Village":
        if selected_province and selected_district:
            village_totals = area_totals[(area_totals['province_name'] == selected_province) & 
                                         (area_totals['district_name'] == selected_district)].groupby('village_name')['converted_result_in_kg'].sum().reset_index()
            fig = px.bar(village_totals, x='village_name', y='converted_result_in_kg', 
                         labels={'village_name': 'Village', 'converted_result_in_kg': 'Total Converted Result (kg)'},
                         title=f'Total Converted Result in kg for Each Village in {selected_province}, {selected_district}'
                        )
        else:
            st.warning("Please select a province and a district.")
            return None
    
    # Display the plot using Streamlit
    st.plotly_chart(fig)

selected_product_name = st.selectbox("Select Product Name:", products_df['name'])
area_totals = get_area_totals(selected_product_name)

selected_area_level = st.selectbox("Select Area Level:", ["Province", "District", "Commune", "Village"])

selected_province = None
selected_district = None
selected_commune = None

if selected_area_level == "District" or selected_area_level == "Commune" or selected_area_level == "Village":
    selected_province = st.selectbox("Select Province:", area_totals['province_name'].unique())

if selected_area_level == "Commune" or selected_area_level == "Village":
    if selected_province:
        selected_district = st.selectbox("Select District:", area_totals[area_totals['province_name'] == selected_province]['district_name'].unique())
    else:
        st.warning("Please select a province.")

if selected_area_level == "Village":
    if selected_province and selected_district:
        selected_commune = st.selectbox("Select Commune:", area_totals[(area_totals['province_name'] == selected_province) & (area_totals['district_name'] == selected_district)]['commune_name'].unique())
    else:
        st.warning("Please select a province and a district.")

plot_area_totals(area_totals, selected_area_level, selected_province, selected_district)