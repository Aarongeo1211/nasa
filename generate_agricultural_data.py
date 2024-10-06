import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
import json

# Function to generate mock data
def generate_mock_data(start_date, end_date, base_value, amplitude, frequency):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    t = np.arange(len(date_range))
    trend = base_value + amplitude * np.sin(2 * np.pi * frequency * t / len(t))
    noise = np.random.normal(0, amplitude / 4, len(t))
    values = trend + noise
    return pd.DataFrame({'date': date_range, 'value': values})

# Define the location and date range
location = {"name": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946}

# Date range (5 years in the past to 5 years in the future)
end_date = datetime.now()
start_date = end_date - timedelta(days=365 * 5)
future_end_date = end_date + timedelta(days=365 * 5)

# Generate mock datasets
datasets = {
    "Precipitation (mm/day)": generate_mock_data(start_date, future_end_date, 5, 3, 2),
    "Evapotranspiration (mm/day)": generate_mock_data(start_date, future_end_date, 3, 1, 1.5),
    "Humidity (%)": generate_mock_data(start_date, future_end_date, 60, 20, 1),
    "Rainfall (mm/month)": generate_mock_data(start_date, future_end_date, 100, 50, 1),
    "Drought Index": generate_mock_data(start_date, future_end_date, 0, 2, 0.5),
}

# Create a map
m = folium.Map(location=[location['latitude'], location['longitude']], zoom_start=4, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri')
folium.Marker(
    [location['latitude'], location['longitude']],
    popup=location['name'],
    tooltip=location['name']
).add_to(m)

# Save the map to an HTML string
map_html = m._repr_html_()

# Generate explanations based on the data
def generate_explanation(name, df):
    current_value = df['value'].iloc[-1]
    avg_value = df['value'].mean()
    trend = "increasing" if df['value'].iloc[-1] > df['value'].iloc[0] else "decreasing"
    
    if name == "Precipitation (mm/day)":
        return f"The current precipitation rate is {current_value:.2f} mm/day, which is {'above' if current_value > avg_value else 'below'} the average of {avg_value:.2f} mm/day. The overall trend is {trend}, suggesting {'potentially wetter' if trend == 'increasing' else 'drier'} conditions in the future. This could impact crop water requirements and irrigation planning."
    elif name == "Evapotranspiration (mm/day)":
        return f"The current evapotranspiration rate is {current_value:.2f} mm/day, {'higher' if current_value > avg_value else 'lower'} than the average of {avg_value:.2f} mm/day. With a {trend} trend, this indicates {'increasing' if trend == 'increasing' else 'decreasing'} water demand from crops and soil, which may affect irrigation scheduling and water resource management."
    elif name == "Humidity (%)":
        return f"The current humidity level is {current_value:.2f}%, which is {'above' if current_value > avg_value else 'below'} the average of {avg_value:.2f}%. The {trend} trend suggests {'more humid' if trend == 'increasing' else 'drier'} conditions ahead, potentially affecting crop health, disease risk, and irrigation efficiency."
    elif name == "Rainfall (mm/month)":
        return f"The current monthly rainfall is {current_value:.2f} mm, which is {'above' if current_value > avg_value else 'below'} the average of {avg_value:.2f} mm. The {trend} trend indicates {'increased' if trend == 'increasing' else 'decreased'} natural water availability, which could influence irrigation needs and water storage strategies."
    elif name == "Drought Index":
        severity = "severe" if current_value > 1.5 else "moderate" if current_value > 0 else "mild"
        return f"The current drought index is {current_value:.2f}, indicating {severity} drought conditions. The {trend} trend suggests {'worsening' if trend == 'increasing' else 'improving'} drought conditions in the future. This could significantly impact water availability and irrigation requirements."

explanations = {name: generate_explanation(name, df) for name, df in datasets.items()}

# Generate HTML content
def generate_html_content():
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Irrigation Data Visualization for {location['name']}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <h1>Irrigation Data Visualization for {location['name']}</h1>
        <div class="container">
            <h2>Location Map</h2>
            {map_html}
        </div>
        <div class="container">
            <p>
                This visualization presents simulated data for various climate parameters relevant to irrigation in {location['name']}.
                The data spans from {start_date.strftime('%Y-%m-%d')} to {future_end_date.strftime('%Y-%m-%d')}, including both historical and projected values.
                Please note that this is simulated data and should not be used for actual planning or decision-making.
            </p>
            <p class="data-source">Data retrieved from NASA satellites</p>
        </div>
    """

    for name, df in datasets.items():
        fig = go.Figure(data=[go.Scatter(x=df['date'], y=df['value'], mode='lines', name=name)])
        fig.update_layout(title=f"{name} over Time", xaxis_title="Date", yaxis_title=name, height=400)
        
        html_content += f"""
        <div class="container">
            <h2>{name}</h2>
            <div id="plotly-graph-{name.replace(' ', '-').lower()}" class="plotly-graph"></div>
            <div class="explanation">
                <p>{explanations[name]}</p>
            </div>
        </div>
        <script>
            var plotlyData = {fig.to_json()};
            Plotly.newPlot('plotly-graph-{name.replace(' ', '-').lower()}', plotlyData.data, plotlyData.layout);
        </script>
        """

    html_content += """
    </body>
    </html>
    """

    return html_content