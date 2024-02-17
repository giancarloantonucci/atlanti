from geopandas import read_file
from folium import Map, GeoJson, Popup

map_data = read_file("./basa/cumuna/cumuna.shp")

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

html = """
    <meta charset="utf-8">
    <div style="font-family: Noto Sans, Helvetica, sans-serif; width: max-content; max-width: 400px; height: max-content;">
        <h2 style="color:#333;">
            %s
        </h2>
        <p style="margin:0; color:#666;">
            %s %s %s %s
        </p>
    </div>
    """

def colour_by_province(idx):
    if idx == 81: # Tràpani
        return 'green'
    elif idx == 84: # Girgenti
        return 'orangered'
    elif idx == 85: # Nissa
        return 'orchid'
    elif idx == 86: # Castruggiuvanni
        return 'darkgoldenrod'
    elif idx == 88: # Ragusa
        return 'darkgrey'
    elif idx == 89: # Saragusa
        return 'maroon'
    elif idx == 282: # Palermu
        return 'darkblue'
    elif idx == 283: # Missina
        return 'deepskyblue'
    elif idx == 287: # Catania
        return 'darkslateblue'

for idx, row in map_data.iterrows():
    local_name = row['LOCAL']
    if row['LOCAL'] is None:
        local_name = row['SCN']
    pronunciation = row['IPA']
    if row['IPA'] is None:
        pronunciation = ''
    GeoJson(
        row['geometry'],
        style_function=lambda feature, idx=row['PROVINCE']: {
            'color': colour_by_province(idx),
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
        popup=Popup(
            html % (
                "%s" % (row['SCN'] if row['SCN'] is not None else "?"),
                "&#127470;&#127481; %s" % row['ITA'],
                "<br>&#128205; %s" % row['LOCAL'] if row['LOCAL'] is not None else "",
                row['IPA'] if row['IPA'] is not None else "",
                "<br>&#129489; %s" % (row['DEMONYM'] if row['DEMONYM'] is not None else "?"),
            ),
        )
    ).add_to(m)

m.save('mappa.html')
m
