import streamlit as st
import requests
import math
import folium
from streamlit_folium import st_folium

# Geoapify API key
API_KEY = "YOUR_API_KEY"  # Replace with your API key

# Haversine formula to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Fetch nearby places using Geoapify Places API
def fetch_nearby_places(latitude, longitude, category, radius=5000, limit=20):
    url = f"https://api.geoapify.com/v2/places?categories={category}&filter=circle:{longitude},{latitude},{radius}&limit={limit}&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch data from the API.")
        return None

# Streamlit app
st.title("Nearby Places Finder 🌍")

# Category selection
category = st.selectbox(
    "What are you looking for?",
    options=["catering.restaurant", "commercial.fuel", "entertainment", "accommodation"],
    format_func=lambda x: {
        "catering.restaurant": "Restaurant 🍴",
        "commercial.fuel": "Gas Station ⛽",
        "entertainment": "Entertainment 🎭",
        "accommodation": "Hotel 🏨"
    }[x]
)

# Initial coordinates
initial_latitude = 40.7128
initial_longitude = -74.0060

# Initialize session state for coordinates
if 'latitude' not in st.session_state:
    st.session_state.latitude = initial_latitude
if 'longitude' not in st.session_state:
    st.session_state.longitude = initial_longitude

# Create a map
m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12)

# Add current marker if coordinates exist
folium.Marker(
    [st.session_state.latitude, st.session_state.longitude],
    popup="Selected Location"
).add_to(m)

# Display the map in Streamlit with on_click event
map_result = st_folium(
    m,
    width=700,
    height=450,
    returned_objects=["last_clicked"]
)

# Update coordinates when map is clicked
if map_result['last_clicked'] is not None:
    st.session_state.latitude = map_result['last_clicked']['lat']
    st.session_state.longitude = map_result['last_clicked']['lng']
    st.rerun()

# Add manual coordinate input
col1, col2 = st.columns(2)
with col1:
    latitude = st.number_input('Latitude', value=st.session_state.latitude, min_value=-90.0, max_value=90.0, step=0.0001)
with col2:
    longitude = st.number_input('Longitude', value=st.session_state.longitude, min_value=-180.0, max_value=180.0, step=0.0001)

# Update session state with input values if they change
if latitude != st.session_state.latitude or longitude != st.session_state.longitude:
    st.session_state.latitude = latitude
    st.session_state.longitude = longitude
    st.rerun()

# Search button
if st.button("Search Nearby Places"):
    if st.session_state.latitude and st.session_state.longitude:
        # Fetch nearby places
        st.write(f"Fetching nearby {category.split('.')[-1]}s...")
        places_data = fetch_nearby_places(st.session_state.latitude, st.session_state.longitude, category)
        
        if places_data and "features" in places_data:
            st.write(f"Found {len(places_data['features'])} places nearby:")
            
            for place in places_data["features"]:
                name = place["properties"].get("name", "N/A")
                address = place["properties"].get("street", "N/A")
                city = place["properties"].get("city", "N/A")
                phone = place["properties"].get("phone", "N/A")
                website = place["properties"].get("website", "N/A")
                place_latitude = place["geometry"]["coordinates"][1]
                place_longitude = place["geometry"]["coordinates"][0]
                
                # Calculate distance
                distance = haversine(
                    st.session_state.latitude, 
                    st.session_state.longitude, 
                    place_latitude, 
                    place_longitude
                )
                
                # Display place details in a card-like format
                with st.container():
                    st.markdown(f"""
                    **{name}**
                    - 📍 {address}, {city}
                    - 📞 {phone}
                    - 🌐 {website}
                    - 📏 {distance:.2f} km away
                    """)
                    st.markdown("---")
        else:
            st.warning("No places found nearby.")
    else:
        st.warning("Please enter valid coordinates.")

# Add instructions for users
st.markdown("""
### How to use:
1. Click on the map to select a location or enter latitude and longitude manually
2. Click the "Search Nearby Places" button
3. Results will appear below the map
""")