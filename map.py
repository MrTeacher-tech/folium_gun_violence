import folium
import pandas as pd
import geopandas as gpd

def add_space(state_name):
    if "New" in state_name:
        split_name= state_name.split("New")
        state_name = "New " + split_name[1].capitalize()
    
    elif "North" in state_name:
        split_name= state_name.split("North")
        state_name = "North " + split_name[1].capitalize()

    elif "South" in state_name:
        split_name= state_name.split("South")
        state_name = "South " + split_name[1].capitalize()

    
    elif "West" in state_name:
        split_name= state_name.split("West")
        state_name = "West " + split_name[1].capitalize()

    elif "Rhode" in state_name:
        split_name= state_name.split("Rhode")
        state_name = "Rhode " + split_name[1].capitalize()
    
    return state_name



#LOAD in gun violence data

gun_violence_rates = "gun_violence.csv"

gun_df = pd.read_csv(gun_violence_rates)

gun_df["URL"] = gun_df["URL"].str.split("/").str[4].str.capitalize().str.strip()    #get full state name with capital first letter

gun_df["STATE_NAME"] = gun_df["URL"].apply(add_space)


gun_df = gun_df.loc[gun_df["YEAR"] == 2022]


#Load in median household income data

household_income = "Median_Income_Per_State_2022.csv"

income_df = pd.read_csv(household_income)

income_df["Median_HouseHold_Income_2022"] = "$" + income_df["Median_HouseHold_Income_2022"]

#Load in permit carry

permitless_carry = "constitutional_carry_states.csv"

carry_df = pd.read_csv(permitless_carry)

#load in governors

governors = "governors_2022.csv"

gov_df = pd.read_csv(governors)


gov_df = gov_df.drop(columns=["Length of regular term in years","Date of first service","Present term ends","Number of previous terms","Term limits","Joint election of governor and lieutenant governor (a)","Official who succeeds governor","Birthdate","Birthplace"])


gov_df = gov_df.rename(columns={"Name and party":"GOV"})

#GEOPANDAS stuff below

us_states_geo = "us-states.json"
geo_df = gpd.read_file(us_states_geo)

geo_df = geo_df.rename(columns={"name":"STATE_NAME"})

# Merge GeoJSON data with gun violence data
merged_df = geo_df.merge(gun_df[['STATE_NAME', 'RATE']], on='STATE_NAME', how='left')

merged_df = merged_df.merge(income_df[['STATE_NAME', 'Median_HouseHold_Income_2022']], on='STATE_NAME', how='left')

merged_df = merged_df.merge(carry_df[['STATE_NAME', 'ConstitutionalCarryStatus2022']], on='STATE_NAME', how='left')

merged_df = merged_df.merge(gov_df[['STATE_NAME', 'GOV']], on='STATE_NAME', how='left')

merged_df = merged_df.dropna()

#print(merged_df)

# Create a folium map
m = folium.Map(location=(37, -100), zoom_start=4, tiles="cartodb positron")

title = '2022 Gun Deaths by State'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(title)  

m.get_root().html.add_child(folium.Element(title_html))


choropleth = folium.Choropleth(
    geo_data=merged_df,
    data=merged_df,
    columns=["STATE_NAME", "RATE"],
    key_on="feature.properties.STATE_NAME",
    fill_color="RdYlGn_r",
    fill_opacity=0.8,
    line_opacity=0.3,
    bins = [0, 5, 10, 15, 20, 25, 30],
    nan_fill_color="white",
    legend_name="Deaths per 100,000",
    
)

# Add tooltips to the Choropleth layer
choropleth.geojson.add_child(
    folium.GeoJsonTooltip(
        fields=["STATE_NAME", "GOV", "ConstitutionalCarryStatus2022", "Median_HouseHold_Income_2022", "RATE"],
        aliases=["State Name:", "Governor", "Open Carry Status:", "Median Household Income:", "Gun Deaths Per 100,000:"],
        localize=True,
        sticky=True,
    )
)
# Add the Choropleth layer to the map
choropleth.add_to(m)

# Save the map to an HTML file
m.save("gun-violence.html")