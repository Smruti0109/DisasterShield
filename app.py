import streamlit as st
import requests
import pandas as pd
import folium
import requests
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

# Predefined stock locations
stock_locations = [
    {"name": "Delhi", "coords": (28.7041, 77.1025), "resources": {"Food": 500, "Water": 1000, "Medical Kits": 300}},
    {"name": "Mumbai", "coords": (19.0760, 72.8777), "resources": {"Food": 700, "Water": 1200, "Medical Kits": 400}},
    {"name": "Chennai", "coords": (13.0827, 80.2707), "resources": {"Food": 450, "Water": 900, "Medical Kits": 200}},
    {"name": "Kolkata", "coords": (22.5726, 88.3639), "resources": {"Food": 600, "Water": 1100, "Medical Kits": 350}},
]

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

# Function to set custom background with revolving Earth
def set_background():
    background_style = """
    <style>
    .stApp {
        background: radial-gradient(circle at center, #0d1117, #0d1117);
        color: white;
        font-family: 'Arial', sans-serif;
        position: relative;
        overflow: hidden;
        min-height: 100vh;
    }
    .earth {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 500px;
        height: 500px;
        background: url('https://upload.wikimedia.org/wikipedia/commons/9/97/The_Earth_seen_from_Apollo_17.jpg') no-repeat center;
        background-size: cover;
        border-radius: 50%;
        animation: spin 20s linear infinite;
        box-shadow: 0 0 50px rgba(255, 255, 255, 0.5);
    }
    @keyframes spin {
        from { transform: translate(-50%, -50%) rotate(0deg); }
        to { transform: translate(-50%, -50%) rotate(360deg); }
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(to bottom, #3a3a3a, #6a11cb);
        color: white;
    }
    .stButton > button {
        background: linear-gradient(to right, #43cea2, #185a9d);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 18px;
        padding: 10px 20px;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.1);
        background: linear-gradient(to right, #185a9d, #43cea2);
    }
    .stDropdown {
        background: linear-gradient(to bottom right, #ffffff, #e0e0e0);
        border-radius: 5px;
        font-size: 16px;
    }
    .square-box {
        width: 300px;
        height: 150px;
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #c9d1d9;
        font-size: 16px;
        margin: 20px;
        text-align: center;
        padding: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    <div class="earth"></div>
    """
    st.markdown(background_style, unsafe_allow_html=True)

# Apply custom background
set_background()

# Streamlit Sidebar
st.sidebar.title("Navigation")
menu = st.sidebar.selectbox(
    "Go to", ["Home", "Disaster Monitoring & Prediction", "Resource Tracking"],
    format_func=lambda x: f"🌟 {x}"
)

# Main Dashboard
st.title("🌍 DisasterShield: Disaster Relief System")

if menu == "Home":
    st.subheader("Welcome!")
    st.markdown("""
        DisasterShield is an disaster relief system designed to optimize disaster response efforts. It leverages predictive analytics, and resource tracking to provide actionable insights for disaster management.
        Explore:
        - *Disaster Monitoring & Prediction*: Track weather conditions and predict disaster impacts.
        - *Resource Tracking*: Monitor and optimize resource allocation.
    """)

    # Corrected Code

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='text-align: center;'>Flood Statistics</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Monitor rainfall data and assess flood risks.</p>", unsafe_allow_html=True)
        flood_image = Image.open("C:\\Users\\Pratiksha\\Documents\\VScode\\disaster_relief\\india-flood-prone-areas-map-2021.jpg")  # Replace with your actual path
        st.image(flood_image, caption="Flood Monitoring", use_container_width=True)
    with col2:
        st.markdown("<h3 style='text-align: center;'>Earthquake Statistics</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Track seismic activity and evaluate earthquake impacts.</p>", unsafe_allow_html=True)
        earthquake_image = Image.open("C:\\Users\\Pratiksha\\Documents\\VScode\\disaster_relief\\Seismic-Map-of-India.png")  # Replace with your actual path
        st.image(earthquake_image, caption="Earthquake Monitoring", use_container_width=True)


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
            st.session_state["lat"] = lat  # Store latitude in session state
            st.session_state["lon"] = lon  # Store longitude in session state
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

    st.markdown(
        """
        <style>
        .large-font {
            font-size:20px !important;
        }
        .medium-font {
            font-size:18px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Load the resources.csv file
    resources_file = "C:\\Users\\Pratiksha\\Documents\\VScode\\disaster_relief\\resources_data.csv"
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
                
                # Ask if the user wants to allocate resources (default set to "No")
                allocate = st.radio("Do you want to allocate resources?", ("Yes", "No"), index=1)
                
                # Display available resources table
                st.markdown(f"Closest Stock Location (lat: {closest_stock['Latitude']}, lon: {closest_stock['longitude']}):")
                st.markdown("### Available Resources")
                stock_info = closest_stock[["Food And Water", "Clothing", "Shelter", "Medical Suppliers"]]
                stock_df = pd.DataFrame(stock_info).reset_index()
                stock_df.columns = ["Resource", "Available Quantity"]
                st.table(stock_df)
                
                if allocate == "Yes":
                    # Help allocate resources
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
                        updated_stock_info = closest_stock[["Food And Water", "Clothing", "Shelter", "Medical Suppliers"]]
                        updated_stock_df = pd.DataFrame(updated_stock_info).reset_index()
                        updated_stock_df.columns = ["Resource", "Remaining Quantity"]
                        st.markdown("### Updated Stock Levels")
                        st.table(updated_stock_df)
                else:
                    st.info("You chose not to allocate resources. The available resources are displayed above.")
        else:
            st.warning("Please enter latitude and longitude in the Disaster Monitoring tab first.")
