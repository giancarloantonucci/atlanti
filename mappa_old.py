# %%
from geopandas import read_file
from folium import Map, GeoJson, Popup

# %% Càrrica mappa dî dati
map_data = read_file("../finaiti/cumuna/cumuna.shp")

# %% Finaiti e mpustazzioni dâ mappa
min_lat, max_lat = 35.0, 40.0
min_lon, max_lon = 11.0, 16.5

m = Map(
    location=(37.1, 14.0),
    zoom_start=8,
    max_bounds=True,
    min_lat=min_lat,
    max_lat=max_lat,
    min_lon=min_lon,
    max_lon=max_lon,
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}',
    attr='Tiles &copy; Esri &mdash; Source: Esri',
    # tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    # attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
    # tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png',
    # attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
)

# Mudeḍḍu HTML pî popup
# popup_template = """
#     <meta charset="utf-8">
#     <div style="font-family: Noto Sans, Helvetica, sans-serif; width: max-content; max-width: 400px; height: max-content;">
#         <h2 style="color:#333;">
#             %s
#         </h2>
#         <p style="margin:0; color:#666;">
#             %s %s %s %s
#         </p>
#     </div>
# """
popup_template = """
    <meta charset="utf-8">
    <div style="font-family: Noto Sans, Helvetica, sans-serif; width: max-content; max-width: 400px; height: max-content;">
        <h2 style="color:#333;">{scn}</h2>
        <p style="margin:0; color:#666;">
            &#127470;&#127481; {ita}
            {location}
            {demonym}
        </p>
    </div>
"""

# %% Funzioni pi culurari sicunnu pruvincia
def get_province_color(province_code):
    color_map = {
        81: 'green',          # Tràpani
        84: 'orangered',      # Girgenti
        85: 'orchid',         # Nissa
        86: 'darkgoldenrod',  # Castruggiuvanni
        88: 'darkgrey',       # Ragusa
        89: 'maroon',         # Saragusa
        282: 'darkblue',      # Palermu
        283: 'deepskyblue',   # Missina
        287: 'darkslateblue'  # Catania
    }
    return color_map.get(province_code, 'black')

# %% Junci i carattarìstichi â mappa
for _, row in map_data.iterrows():
    local_name = row['LOCAL'] if row['LOCAL'] else row['SCN']
    province_color = get_province_color(row['PROVINCE'])
    popup_content = popup_template.format(
        scn=row['SCN'] if row['SCN'] else "?",
        ita=row['ITA'],
        location=f"<br>&#128205; {local_name}" if local_name else "",
        demonym=f"<br>&#129489; {row['DEMONYM']}" if row['DEMONYM'] else "?"
    )

    GeoJson(
        row['geometry'],
        style_function=lambda feature, color=province_color: {
            'color': color,
            'weight': 1,
            'fillOpacity': 0.2
        },
        highlight_function=lambda feature: {
            'fillColor': '#778899',
            'color': '#555555',
            'weight': 1,
            'fillOpacity': 0.9
        },
        name=row['ITA'],
        tooltip=row['SCN'],
        popup=Popup(popup_content)
    ).add_to(m)

# %% Riggistra a mappa
m.save('mappa.html')

# %%
import webbrowser
import os

file_path = os.path.abspath("mappa.html")
webbrowser.open(f"file://{file_path}")
