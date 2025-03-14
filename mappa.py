# %%
import geopandas as gpd
import folium
from folium import GeoJson, Element
import json
import webbrowser
import os
import unicodedata
import re

# %% Helper function to normalize strings (remove diacritics and parentheses)
def normalize_string(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")  # Remove diacritics
    return re.sub(r"[()]", "", s).strip().lower()  # Remove parentheses

# %% Function to assign colors to provinces
def get_province_color(province_code):
    color_map = {
        81: "#FFB400",  # Warm Gold
        84: "#FF6F61",  # Soft Coral Red
        85: "#9370DB",  # Medium Purple
        86: "#E9967A",  # Muted Salmon
        88: "#708090",  # Slate Grey
        89: "#D9534F",  # Rich Tomato Red
        280: "#00A86B", # Deep Jade Green
        282: "#4682B4", # Soft Steel Blue
        283: "#40E0D0", # Turquoise
        287: "#9932CC", # Dark Orchid Purple
    }
    return color_map.get(province_code, "#2F4F4F")  # Default: Dark Slate Grey for contrast

# %% Load geographical data
map_data = gpd.read_file("../finaiti/cumuna/cumuna.shp")
provinces = gpd.read_file("../finaiti/pruvinci/pruvinci.shp")

# %% Map province codes to names
province_mapping = {row["PROVINCE"]: row["SCN"] for _, row in provinces.iterrows()}

# %% Create the map
min_lat, max_lat = 34.7, 39.7
min_lon, max_lon = 12.0, 17.5
m = folium.Map(
    location=(37.2, 15.0),
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

# %% Inject global JavaScript functions
global_js = """
<script>
  function highlightFeature(id) {
      for (var key in window.layer_map) {
          if (window.layer_map.hasOwnProperty(key)) {
              var lyr = window.layer_map[key];
              var origColor = lyr.options.originalColor || lyr.options.color;
              lyr.setStyle({ fillOpacity: 0.3, color: origColor });
              lyr.selected = false;
          }
      }
      var layer = window.layer_map[id];
      if (layer) {
          layer.setStyle({ fillOpacity: 0.8, color: '#1E90FF' });
          layer.selected = true;
      }
  }

  function toggleSidebarInfo(id) {
      var sidebar = document.getElementById("sidebar");
      var infoBoxes = document.querySelectorAll('[id^="info_layer_"]');
      infoBoxes.forEach(function(div) {
          div.style.display = 'none';
      });
      var infoDiv = document.getElementById("info_" + id);
      if (!infoDiv) return;
      if (infoDiv.style.display === "none" || infoDiv.style.display === "") {
          infoDiv.innerHTML = window.layer_info[id] || "No info available.";
          infoDiv.style.display = "block";
          var offset = 75;
          sidebar.scrollTo({ top: infoDiv.offsetTop - offset, behavior: "smooth" });
      } else {
          infoDiv.style.display = "none";
      }
  }

    function expandSectionForLayer(layer_id) {
      var infoElem = document.getElementById("info_" + layer_id);
      if(infoElem) {
          var placesList = infoElem.parentElement.parentElement;
          if(placesList && placesList.classList.contains("places-list")) {
              placesList.style.transition = "max-height 0.4s ease-out";
              placesList.style.maxHeight = placesList.scrollHeight + "px";
              placesList.classList.add("expanded");
              setTimeout(function(){
                  var sidebar = document.getElementById("sidebar");
                  var offset = 75;
                  sidebar.scrollTo({ top: infoElem.offsetTop - offset, behavior: "smooth" });
              }, 400);
          }
      }
    }

  window.layer_map = {};
  window.layer_info = {};
  console.log("Global JS functions and objects defined.");
</script>
"""
m.get_root().html.add_child(Element(global_js))

# %% Prepare HTML for the sidebar
layer_info_dict = {}
locations_html = "<ul id='location-list'>"

# Group the cumuna data by the 'PROVINCE' field.
grouped = map_data.groupby('PROVINCE')

# Group cumuna data by province and sort alphabetically
sorted_province_codes = sorted(
    grouped.groups.keys(),
    key=lambda pc: normalize_string(province_mapping.get(pc, f"Province {pc}"))
)

for province_code in sorted_province_codes:
    province_name = province_mapping.get(province_code, f"Province {province_code}")
    province_color = get_province_color(province_code)

    group_df = grouped.get_group(province_code)
    group_sorted = group_df.sort_values("SCN", key=lambda s: s.fillna("").apply(normalize_string))

    place_items_html = []
    scn_to_layerid = {}

    # Iterate over places
    for idx, row in group_sorted.iterrows():
        layer_id = f"layer_{idx}"
        local_name = row["LOCAL"] if row["LOCAL"] != row["SCN"] else None

        info_str = f"""
            <div class="info-box">
                <span class="info-italian">{row['ITA']}</span>
        """
        if local_name:
            info_str += f"""
                <span class="info-location">
                    &#128205; {local_name}
                </span>
            """
        if row.get('DEMONYM'):
            info_str += f"""
                <span class="info-demonym">
                    &#129489; {row['DEMONYM']} <!-- 🧑 Demonym -->
                </span>
            """
        else:
            info_str += """
                <span class="info-demonym">
                    &#129489; ?
                </span>
            """
        info_str += "</div>"

        layer_info_dict[layer_id] = info_str

        # Sidebar list item
        place_items_html.append(f"""
        <li class="place-item">
          <a href="#" onclick="toggleSidebarInfo('{layer_id}'); highlightFeature('{layer_id}'); expandSectionForLayer('{layer_id}'); return false;">
            {row["SCN"] if row["SCN"] else "?"}
          </a>
          <div id="info_{layer_id}" style="display:none;"></div>
        </li>
        """)

        if row["SCN"]:
            scn_to_layerid[row["SCN"]] = layer_id

        # Create a GeoJson layer for each place
        lyr = GeoJson(
            row["geometry"],
            name=row["ITA"],
            style_function=lambda _, color=province_color: {
                "color": color,
                "weight": 1.5,
                # "fillColor": color,
                "fillOpacity": 0.3
            },
        ).add_to(m)
        lyr.options["originalColor"] = province_color

        # Attach events to the layer
        layer_js_name = lyr.get_name()
        js_assign = f"""
        <script>
          document.addEventListener("DOMContentLoaded", function() {{
              window.layer_map["{layer_id}"] = {layer_js_name};
              {layer_js_name}.on("click", function(e) {{
                  toggleSidebarInfo("{layer_id}");
                  highlightFeature("{layer_id}");
                  expandSectionForLayer("{layer_id}");
              }});
              {layer_js_name}.on("mouseover", function(e) {{
                  if (!{layer_js_name}.selected) {{
                      {layer_js_name}.setStyle({{ fillOpacity: 0.6, color: '#1E90FF' }});
                  }}
              }});
              {layer_js_name}.on("mouseout", function(e) {{
                  if (!{layer_js_name}.selected) {{
                      var origColor = {layer_js_name}.options.originalColor || {layer_js_name}.options.color;
                      {layer_js_name}.setStyle({{ fillOpacity: 0.3, color: origColor }});
                  }}
              }});
          }});
        </script>
        """
        m.get_root().html.add_child(Element(js_assign))

    # Province header with expandable list
    locations_html += f"""
    <li class="province-block" style="border-left: 6px solid {province_color};">
      <span class="province-header">{province_name}</span>
      <ul class="places-list" style="max-height: 0; overflow: hidden; transition: max-height 0.4s ease-out;">
        {''.join(place_items_html)}
      </ul>
    </li>
    """

locations_html += "</ul>"

# Inject layer info into global JS
js_layer_info = f'<script>window.layer_info = {json.dumps(layer_info_dict)};</script>'
m.get_root().html.add_child(Element(js_layer_info))

# %% Add collapse toggle functionality for province headers with smooth transitions
collapse_js = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    var headers = document.querySelectorAll(".province-header");
    headers.forEach(function(header) {
        header.addEventListener("click", function() {
            var placesList = header.nextElementSibling;
            var provinceBlock = header.parentElement;
            if (placesList) {
                if (placesList.classList.contains("expanded")) {
                    placesList.style.transition = "max-height 0.3s ease-in";
                    placesList.style.maxHeight = "0";
                    placesList.classList.remove("expanded");
                    provinceBlock.classList.remove("expanded");
                } else {
                    placesList.style.transition = "max-height 0.4s ease-out";
                    placesList.style.maxHeight = placesList.scrollHeight + "px";
                    placesList.classList.add("expanded");
                    provinceBlock.classList.add("expanded");
                }
            }
        });
    });
});
</script>
"""
m.get_root().html.add_child(Element(collapse_js))

# %% Sidebar HTML
sidebar_html = f"""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" rel="stylesheet"
      integrity="sha384-Zenh87qX5JnK2Jl1vWaP+4M9N9Q+6dJ4niLQc8Y9RS+ok1N8kzJ1qdh+Lfb8I1T"
      crossorigin="anonymous">
<link rel="stylesheet" type="text/css" href="css/sidebar.css">
<div id="sidebar">
    {locations_html}
</div>
"""
m.get_root().html.add_child(Element(sidebar_html))

# %% Save and open the map
m.save('./mappa.html')
webbrowser.open(f"file://{os.path.abspath('mappa.html')}")
