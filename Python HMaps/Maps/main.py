import csv
import webbrowser
import folium
import json
import os
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Step 1: Verify the CSV file path
file_path = "C:\\Users\\mbofh\\OneDrive\\Desktop\\Telkom Senmtiments Analysis\\Test_Sentiments_Analysis.csv"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

data = []

# Step 2: Read the CSV file
with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    print("Available columns:", reader.fieldnames)
    for row in reader:
        try:
            data.append({
                "province": row["Province"],
                "sentiment": float(row["Sentiments"].replace(',', '.'))
            })
        except ValueError:
            print(f"Skipping row due to invalid sentiment value: {row}")
            continue

# Step 3: Calculate average sentiment for each province
province_sentiments = {}
for entry in data:
    province = entry["province"]
    sentiment = entry["sentiment"]
    if province in province_sentiments:
        province_sentiments[province].append(sentiment)
    else:
        province_sentiments[province] = [sentiment]

province_avg_sentiment = {province: sum(sentiments) / len(sentiments) for province, sentiments in province_sentiments.items()}
print("Province Average Sentiments:", province_avg_sentiment)

# Step 4: Verify the GeoJSON file path
geojson_path = "C:\\Users\\mbofh\\OneDrive\\Desktop\\Telkom Senmtiments Analysis\\za.json"

if not os.path.exists(geojson_path):
    print(f"GeoJSON file not found: {geojson_path}")
    exit()

# Step 5: Load GeoJSON data
with open(geojson_path, mode='r', encoding='utf-8') as geojson_file:
    geojson_data = json.load(geojson_file)

# Function to get color based on sentiment score
def get_color(sentiment):
    if -1 <= sentiment <= -0.5:
        return "#FF4500"  # Strong negative (orange)
    elif -0.49 <= sentiment <= -0.01:
        return "lightblue"  # Weak negative (light blue)
    elif sentiment == 0:
        return "#FFD700"  # Neutral (gold)
    elif 0.01 <= sentiment <= 0.49:
        return "#ADFF2F"  # Weak positive (light green)
    elif 0.5 <= sentiment <= 1:
        return "#006400"  # Strong positive (dark green)
    else:
        return "gray"  # Default color for missing data

# Step 6: Create a Folium map centered on South Africa
m = folium.Map(location=[-30.5595, 22.9375], zoom_start=6)

# Add GeoJSON to the map and shade provinces
for feature in geojson_data["features"]:
    province_name = feature["properties"]["name"]

    avg_sentiment = province_avg_sentiment.get(province_name, None)

    if avg_sentiment is not None:
        color = get_color(avg_sentiment)
        folium.GeoJson(
            feature,
            style_function=lambda x, color=color: {
                "fillColor": color,
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.6,
            },
            tooltip=folium.Tooltip(f"{province_name}: Avg Sentiment {avg_sentiment:.2f}"),
        ).add_to(m)
    else:
        folium.GeoJson(
            feature,
            style_function=lambda x: {
                "fillColor": "gray",  # Default gray for missing data
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.6,
            },
            tooltip=folium.Tooltip(f"{province_name}: No Sentiment Data"),
        ).add_to(m)

# Step 7: Generate the bar chart
provinces = list(province_avg_sentiment.keys())
avg_sentiments = list(province_avg_sentiment.values())

plt.figure(figsize=(10, 6))
bars = plt.bar(provinces, avg_sentiments, color=['green' if s > 0 else 'red' for s in avg_sentiments])
plt.xlabel('Provinces')
plt.ylabel('Average Sentiment')
plt.title('Average Sentiment by Province')
plt.xticks(rotation=45, ha='right')

# Add values on bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom')

# Save the bar chart to a BytesIO object
buffer = BytesIO()
plt.tight_layout()
plt.savefig(buffer, format='png')
buffer.seek(0)
encoded_chart = base64.b64encode(buffer.read()).decode('utf-8')
buffer.close()

# Step 8: Add the bar chart to the map HTML file
legend_html = '''
<div style="
position: fixed; 
bottom: 50px; left: 50px; width: 250px; height: 180px; 
background-color: white; z-index:9999; font-size:14px;
border:2px solid grey; padding: 10px;">
<strong>Sentiment Legend</strong><br>
<i style="background: #FF4500; width: 20px; height: 20px; display: inline-block;"></i> Strong Negative (-1 to -0.5)<br>
<i style="background: lightblue; width: 20px; height: 20px; display: inline-block;"></i> Weak Negative (-0.49 to -0.01)<br>
<i style="background: #FFD700; width: 20px; height: 20px; display: inline-block;"></i> Neutral (0)<br>
<i style="background: #ADFF2F; width: 20px; height: 20px; display: inline-block;"></i> Weak Positive (0.01 to 0.49)<br>
<i style="background: #006400; width: 20px; height: 20px; display: inline-block;"></i> Strong Positive (0.5 to 1)<br>
<i style="background: gray; width: 20px; height: 20px; display: inline-block;"></i> No Data Available<br>
</div>
'''

m.get_root().html.add_child(folium.Element(legend_html))

# Embed the bar chart
chart_html = f'<img src="data:image/png;base64,{encoded_chart}" style="position:fixed; top:50px; right:50px; width:500px; height:300px; z-index:9999; border:2px solid grey;">'
m.get_root().html.add_child(folium.Element(chart_html))

# Step 9: Save and display the map
map_file = "sentiment_map.html"
m.save(map_file)
webbrowser.open(map_file)
print("Map opened in your default web browser!")
