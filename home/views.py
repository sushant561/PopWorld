from django.shortcuts import render
from django.http import HttpResponse
import folium
import json
from folium.features import GeoJson, GeoJsonTooltip

# Create your views here.

def home(request):
    # Create a folium map centered at [0, 0] with zoom level 2
    world_map = folium.Map(location=[20, 0], zoom_start=2, control_scale=True)
    
    # Add country boundaries with hover functionality
    folium.GeoJson(
        'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json',
        name='World Countries',
        style_function=lambda x: {
            'fillColor': '#3186cc',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.2,
        },
        highlight_function=lambda x: {
            'fillColor': '#ff0000',
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.5,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['name'],
            aliases=['Country:'],
            style=('background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;')
        )
    ).add_to(world_map)
    
    # Add layer control
    folium.LayerControl().add_to(world_map)
    
    # Get the HTML representation of the map
    map_html = world_map._repr_html_()
    
    # Pass the map HTML to the template
    context = {
        'map_html': map_html
    }
    
    return render(request, 'home.html', context)
