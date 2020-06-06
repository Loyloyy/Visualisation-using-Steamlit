import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# Special thing about Streamlit is that instead of rebuilding the entire page and scanning the entire script
# everytime you edit, it only send the changes made to update the page necessary
# st.title('Hello wow')

# Markdown is enabled as well
# If you don't know how to use the library, simply writing it down will show info on the webdriver
# for e.g. st.markdown()
# st.markdown('## My first streamlit dashboard!')

data_URL = ('C:/Users/Alloy/Desktop/Streamlit/Motor_Vehicle_Collisions_-_Crashes.csv')

st.title('Motor Vehicle Collisions in New York City')
st.markdown('This application is a Streamlit dashboard that helps'
'to analyse motor vehicle collisions in NYC 🚗🚗🚗')

@st.cache(persist = True)
def load_data(nrows):
    data = pd.read_csv(data_URL, nrows = nrows, parse_dates = [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset = ['LATITUDE', 'LONGITUDE'], inplace = True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace = True)
    data.rename(columns = {'crash_date_crash_time': 'date/time'}, inplace = True)
    return data

data = load_data(100000)

st.header('Where are the most number of people injured in NYC?')
# Create a slider and set the starting and end limit
injured_people = st.slider('Number of people injured in vehicle collisions', 0, 19)
# Query the
st.map(data.query('injured_persons >= @injured_people')[['latitude', 'longitude']].dropna(how = 'any'))


st.header('How many collisions occur during a given time of day?')
# hour = st.selectbox('Hour to look at', range(0, 23), 1)
hour = st.slider('Hour to look at', 0, 23)
data = data[data['date/time'].dt.hour == hour]


st.markdown('Vehicle Collisions between %i:00 and %i:00' % (hour, (hour + 1) % 24))
# calculate the average of latitude and longitude so as to determine where NYC is
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    # Choose the map type
    map_style = 'mapbox://styles/mapbox/light-v9',
    initial_view_state = {
        # Set the latitude to zoom into based on midpoint calculated
        'latitude': midpoint[0],
        # Set the latitude to zoom into based on midpoint calculated
        'longitude': midpoint[1],
        'zoom': 11,
        'pitch': 50,
    },
    layers =[
        pdk.Layer(
        'HexagonLayer',
        data = data[['date/time', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        # radius of each point on the map
        radius = 100,
        # extruded is to set whether you want it as 2D (flat) or 3D (sticking out from ground)
        extruded = True,
        pickable = True,
        elevantion_scale = 4,
        elevation_range = [0, 1000],
        ),
    ],
))

st.subheader('Breakdown by minute between %i:00 and %i:00' % (hour, (hour + 1) %24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range = (0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x = 'minute', y = 'crashes', hover_data = ['minute', 'crashes'], height = 400)
st.write(fig)


st.header('Top 5 dangerous streets by affected type')
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrains':
    # Upon choosing pedestrians, the data shown will include, the street name and number of injured pesdestrians which will be sorted in
    # descending order based on the number of injured pedestrains. Rows with NA will be dropped as well and only top 5 results will be shown
    st.write(original_data.query('injured_pedestrians >= 1')[['on_street_name', 'injured_pedestrians']].sort_values(by = ['injured_pedestrians'], ascending = False).dropna(how = 'any')[:5])

if select == 'Cyclists':
    st.write(original_data.query('injured_cyclists >= 1')[['on_street_name', 'injured_cyclists']].sort_values(by = ['injured_cyclists'], ascending = False).dropna(how = 'any')[:5])

if select == 'Motorists':
    st.write(original_data.query('injured_motorists >= 1')[['on_street_name', 'injured_motorists']].sort_values(by = ['injured_motorists'], ascending = False).dropna(how = 'any')[:5])


if st.checkbox('Show Raw Data', False):
    st.subheader('Raw Data')
    st.write(data)
