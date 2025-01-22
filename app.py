import streamlit as st
import requests
import pandas as pd
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium
import json

# Disaster options
DISASTER_TYPES = ["Flood", "Earthquake"]

# Initialize session state
if "lat" not in st.session_state:
    st.session_state["lat"] = None
if "lon" not in st.session_state:
    st.session_state["lon"] = None
if "disaster_type" not in st.session_state:
    st.session_state["disaster_type"] = None
if "current_stock" not in st.session_state:
    st.session_state["current_stock"] = None
    
import requests

def predict_flood(inputs):
    API_KEY = "IBM Watson API"
    token_response = requests.post(
        'https://iam.cloud.ibm.com/identity/token', 
        data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'}
    )
    mltoken = token_response.json().get("access_token")

    if not mltoken:
        st.error("Failed to obtain token. Check your API key.")
        return "Error in prediction"

    header = {
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer ' + mltoken
    }

    # Prepare the payload with the user's input
    payload_scoring = {
        "input_data": [{
            "fields": ["Latitude", "Longitude", "Rainfall (mm)", "River Discharge (m³/s)", "Water Level (m)", "Historical Floods"],
            "values": [list(inputs.values())]
        }]
    }

    # Send the request to the flood prediction model endpoint
    response_scoring = requests.post(
        'PUBLIC_ENDPOINT', 
        json=payload_scoring, 
        headers=header
    )

    # Log the response details
    if response_scoring.status_code == 200:
        result = response_scoring.json()
        # st.write(result)  # Log the full response for debugging
        flood_occurred = result.get("predictions", [{}])[0].get("values", [[0]])[0][0]
        return "Yes" if flood_occurred == 1 else "No"
    else:
        st.error(f"API request failed with status code {response_scoring.status_code}: {response_scoring.text}")
        return "Error in prediction"


def predict_earthquake(inputs):
    # IBM Watson API key and token generation
    API_KEY = "IBM Watson API"
    token_response = requests.post(
        'https://iam.cloud.ibm.com/identity/token', 
        data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'}
    )
    mltoken = token_response.json()["access_token"]

    header = {
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer ' + mltoken
    }

    # Prepare the payload with the user's input
    payload_scoring = {
        "input_data": [{
            "fields": ["depth", "magNst", "latitude", "longitude"],
            "values": [list(inputs.values())]
        }]
    }

    # Send the request to the earthquake prediction model endpoint
    response_scoring = requests.post(
        'PUBLIC_ENDPOINT', 
        json=payload_scoring, 
        headers=header
    )

    if response_scoring.status_code == 200:
        result = response_scoring.json()
        try:
            magnitude = result.get("predictions", [{}])[0].get("values", [[None]])[0][0]
            if magnitude is None:
                raise ValueError("Magnitude value is missing")
            return round(float(magnitude), 2)
        except (TypeError, ValueError):
            st.error("Failed to parse magnitude from API response.")
            return "Error in prediction"
    else:
        st.error(f"API request failed with status code {response_scoring.status_code}: {response_scoring.text}")
        return "Error in prediction"

def get_earthquake_category(magnitude):
    """Classify earthquake magnitude into categories."""
    try:
        magnitude = float(magnitude)  
    except (ValueError, TypeError):
        return "Invalid magnitude value"

    if magnitude < 2.0:
        return "Micro Earthquake"
    elif 2.0 <= magnitude < 4.0:
        return "Minor Earthquake"
    elif 4.0 <= magnitude < 6.0:
        return "Light Earthquake"
    elif 6.0 <= magnitude < 7.0:
        return "Strong Earthquake"
    elif 7.0 <= magnitude < 8.0:
        return "Major Earthquake"
    elif 8.0 <= magnitude < 10.0:
        return "Great Earthquake"
    else:
        return "Massive Earthquake"
    
# Function to find the closest stock location
def find_closest_stock(lat, lon):
    current_location = (lat, lon)
    closest_location = min(stock_locations, key=lambda loc: geodesic(current_location, loc["coords"]).km)
    return closest_location

# Streamlit Sidebar
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Home", "Disaster Monitoring & Prediction", "Resource Tracking"])

# Main Dashboard
st.title("🌍 DisasterShield: Disaster Relief System")

if menu == "Home":
    st.subheader("Welcome!")
    st.markdown("""
        This dashboard helps optimize disaster relief efforts using real-time weather data and AI predictions.
        Explore:
        - *Disaster Monitoring & Prediction*: Track weather conditions and predict disaster impacts.
        - *Resource Tracking*: Monitor and optimize resource allocation.
    """)

elif menu == "Disaster Monitoring & Prediction":
    st.subheader("🌦 Disaster Monitoring & AI Predictions")

    # Disaster type selection
    disaster_type = st.selectbox("Select Disaster Type", DISASTER_TYPES)
    st.session_state["disaster_type"] = disaster_type

    if disaster_type == "Flood":
        # Inputs for flood prediction
        lat = st.number_input("Enter Latitude", step=0.01)
        lon = st.number_input("Enter Longitude", step=0.01)
        rainfall = st.number_input("Enter Rainfall (mm)", value=0.0)
        river_discharge = st.number_input("Enter River Discharge (m³/s)", value=0.0)
        water_level = st.number_input("Enter Water Level (m)", value=0.0)
        historical_floods = st.selectbox("Historical Floods in Area", ["Yes", "No"])

        if st.button("Predict Flood Impact"):
            inputs = {
                "Latitude": lat,
                "Longitude": lon,
                "Rainfall (mm)": rainfall,
                "River Discharge (m³/s)": river_discharge,
                "Water Level (m)": water_level,
                "Historical Floods": historical_floods
            }
            st.session_state["lat"] = lat  
            st.session_state["lon"] = lon  
            flood_result = predict_flood(inputs)
            st.markdown(f"*Flood Prediction Result:*\n- Flood Occurred: {flood_result}")

    elif disaster_type == "Earthquake":
        # Inputs for earthquake prediction
        lat = st.number_input("Enter Latitude", value=20.5937, step=0.01)
        lon = st.number_input("Enter Longitude", value=78.9629, step=0.01)
        depth = st.number_input("Enter Depth (km)", value=10.0, step=0.1)
        magNst = st.number_input("Enter Magnitude (magNst)", value=4.0, step=0.1)

        if st.button("Predict Earthquake Impact"):
            inputs = {
                "latitude": lat,
                "longitude": lon,
                "depth": depth,
                "magNst": magNst
            }
            magnitude = predict_earthquake(inputs)
            category = get_earthquake_category(magnitude)
            st.markdown(f"**Prediction Result:**\n- Magnitude: {magnitude}\n- Category: {category}")
            st.session_state["lat"] = lat
            st.session_state["lon"] = lon

    # Display selected location on map only if lat and lon are valid
    if st.session_state["lat"] is not None and st.session_state["lon"] is not None:
        st.markdown("*Location Map:*")
        m = folium.Map(location=[st.session_state["lat"], st.session_state["lon"]], zoom_start=6)
        folium.Marker([st.session_state["lat"], st.session_state["lon"]], 
                      tooltip=f"Disaster Location: ({st.session_state['lat']}, {st.session_state['lon']})").add_to(m)
        st_folium(m, width=800, height=400)

elif menu == "Resource Tracking":
    st.subheader("🚚 Resource Tracking")
    
    # Load the resources.csv file
    resources_file = "resources_data.csv"
    resources_df = pd.read_csv(resources_file)
    
    # Check for missing or invalid data
    if resources_df[['Latitude', 'longitude']].isnull().any().any():
        st.error("Error: The dataset contains missing latitude or longitude values. Please check your resources.csv file.")
    else:
        if "lat" in st.session_state and "lon" in st.session_state and st.session_state["lat"] is not None and st.session_state["lon"] is not None:
            user_coords = (st.session_state["lat"], st.session_state["lon"])
            
            # Check if user input coordinates are valid
            if not all(map(lambda x: x is not None and isinstance(x, (int, float)), user_coords)):
                st.error("Invalid input latitude and longitude. Please enter valid coordinates.")
            else:
                # Calculate the geodesic distance
                resources_df['Distance'] = resources_df.apply(
                    lambda row: geodesic(user_coords, (row['Latitude'], row['longitude'])).km, axis=1
                )
                closest_stock = resources_df.loc[resources_df['Distance'].idxmin()]
                
                st.markdown(f"Closest Stock Location (lat: {closest_stock['Latitude']}, lon: {closest_stock['longitude']}):")
                
                # Display available resources
                st.markdown("### Available Resources")
                stock_info = closest_stock[["food and water", "clothing", "shelter", "medical suppliers"]]
                stock_df = pd.DataFrame(stock_info).reset_index()
                stock_df.columns = ["Resource", "Available Quantity"]
                st.table(stock_df)
                
                # Allocate resources
                st.markdown("### Allocate Resources")
                allocations = {}
                for resource in stock_info.index:
                    allocations[resource] = st.number_input(
                        f"Allocate {resource.replace('_', ' ').capitalize()}",
                        min_value=0, max_value=int(stock_info[resource]), step=1
                    )
                
                if st.button("Update Stock After Allocation"):
                    # Update the resources in the DataFrame
                    for resource, allocated_quantity in allocations.items():
                        closest_stock[resource] -= allocated_quantity
                    
                    # Save the updated data back to CSV
                    resources_df.loc[resources_df['Distance'].idxmin()] = closest_stock
                    resources_df.drop(columns=["Distance"], inplace=True)  # Clean up before saving
                    resources_df.to_csv(resources_file, index=False)
                    
                    st.success("Stock updated successfully!")
                    
                    # Display updated stock
                    updated_stock_info = closest_stock[["food and water", "clothing", "shelter", "medical suppliers"]]
                    updated_stock_df = pd.DataFrame(updated_stock_info).reset_index()
                    updated_stock_df.columns = ["Resource", "Remaining Quantity"]
                    st.markdown("### Updated Stock Levels")
                    st.table(updated_stock_df)
        else:
            st.warning("Please enter latitude and longitude in the Disaster Monitoring tab first.")
