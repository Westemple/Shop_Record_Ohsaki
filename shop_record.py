import streamlit as st  
import folium  
from streamlit_folium import folium_static  
import re  
import json  
import os  
  
# Set the page config to wide mode  
st.set_page_config(layout="wide")  
  
# Define the file to store the places data  
DATA_FILE = 'places.json'  
  
# Function to load data from JSON file  
def load_data():  
    if os.path.exists(DATA_FILE):  
        with open(DATA_FILE, 'r', encoding='utf-8') as f:  
            return json.load(f)  
    return []  
  
# Function to save data to JSON file  
def save_data(data):  
    with open(DATA_FILE, 'w', encoding='utf-8') as f:  
        json.dump(data, f, ensure_ascii=False, indent=4)  
  
# Load initial data  
if 'places' not in st.session_state:  
    st.session_state['places'] = load_data()  
  
def extract_lat_lon_zoom(url):  
    pattern = r'@(-?\d+\.\d+),(-?\d+\.\d+),(\d+(?:\.\d+)?)z'  
    match = re.search(pattern, url)  
    if match:  
        lat, lon, zoom = match.groups()  
        return float(lat), float(lon), int(float(zoom))  
    return None, None, None   
  
# Title of the app  
st.title("懇親会で使用した店の記録アプリ")  
  
# Input for shop name and Google Maps URL  
shop_name = st.text_input("店名を入力してください:")  
url = st.text_input("Google MapsのURLを入力してください:")  
  
# Register button  
if st.button("登録"):  
    lat, lon, zoom = extract_lat_lon_zoom(url)  
    if lat and lon and zoom:  
        # Adjust longitude to move 250 meters east  
        lon += 0.002  
        st.write(f"抽出された座標: 緯度 {lat}, 経度 {lon}, ズームレベル {zoom}")  
        new_place = {'name': shop_name, 'url': url, 'lat': lat, 'lon': lon, 'zoom': zoom, 'comments': '', 'rating': None}  
        st.session_state['places'].append(new_place)  
        save_data(st.session_state['places'])  # Save data to JSON file  
        st.experimental_rerun()   
  
# Default center (Tokyo) or center on the last added place  
if st.session_state['places']:  
    last_place = st.session_state['places'][-1]  
    map_center = [last_place['lat'], last_place['lon']]  
    map_zoom = last_place.get('zoom', 17)  # Use default zoom level 17 if 'zoom' key is missing  
else:  
    map_center = [35.6895, 139.6917]  
    map_zoom = 12  # Default zoom level if no places are added  
  
# Display map  
m = folium.Map(location=map_center, zoom_start=map_zoom)  
  
# Display each place on the map  
for place in st.session_state['places']:  
    folium.Marker(  
        location=[place['lat'], place['lon']],  
        popup=f"{place.get('name', 'Unnamed')}<br>コメント: {place.get('comments', 'No comments')}<br>評価: {place.get('rating', 'No rating')}",  
        tooltip=place.get('name', 'Unnamed')  
    ).add_to(m)  
  
# Display map in the app  
folium_static(m)  
  
# List of places with options to add comments, rating, and delete  
for i, place in enumerate(st.session_state['places']):  
    st.write(f"### {place.get('name', 'Unnamed')}")  
    place['comments'] = st.text_area(f"コメント ({place.get('name', 'Unnamed')}):", place.get('comments', ''), key=f"comments_{i}")  
    place['rating'] = st.slider(f"評価 ({place.get('name', 'Unnamed')}):", 0, 5, place.get('rating', 0), key=f"rating_{i}")  
  
    if st.button(f"削除 ({place.get('name', 'Unnamed')})", key=f"delete_{i}"):  
        del st.session_state['places'][i]  
        save_data(st.session_state['places'])  # Save data to JSON file  
        st.experimental_rerun()  
  
# Save data whenever comments or ratings are changed  
save_data(st.session_state['places'])  