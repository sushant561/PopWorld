from django.shortcuts import render
from django.http import HttpResponse
import folium
import json
import requests
from folium.features import GeoJson, GeoJsonTooltip

# Create your views here.

def home(request):
    # Get selected country from request
    selected_country = request.GET.get('country', None)
    countries = []  # Ensure countries is always defined
    
    # Create a folium map centered at [0, 0] with zoom level 2
    world_map = folium.Map(
        location=[20, 0],
        zoom_start=2,
        control_scale=True
    )

    # Add a white rectangle for ocean background
    folium.Rectangle(
        bounds=[[-90, -180], [90, 180]],
        color=None,
        fill=True,
        fill_color='white',
        fill_opacity=1,
        z_index=0
    ).add_to(world_map)
    
    # Function to determine country style
    def style_function(feature):
        country_id = feature['id']
        if selected_country and country_id == selected_country:
            return {
                'fillColor': '#ff0000',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.5,
            }
        return {
            'fillColor': '#3186cc',
            'color': 'black',
            'weight': 0.2,
            'fillOpacity': 0.2,
        }

    # Add country boundaries with hover functionality
    countries_geojson = folium.GeoJson(
        'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json',
        name='World Countries',
        style_function=style_function,
        highlight_function=lambda x: {
            'fillColor': '#ff0000',
            'color': 'black',
            'weight': 1,
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

    # Add JavaScript for handling country selection
    map_html += """
    <script>
    document.getElementById('countrySelect').addEventListener('change', function() {
        var selectedCountry = this.value;
        if (selectedCountry) {
            window.location.href = '?country=' + selectedCountry;
        }
    });
    </script>
    """
    
    # Fetch world population data from API
    try:
        # World population data from World Population API
        population_response = requests.get('https://restcountries.com/v3.1/all?fields=population,name,flags,area,region,capital,cca3')
        population_response.raise_for_status()
        countries_data = population_response.json()
        
        # Calculate total world population
        total_population = sum(country.get('population', 0) for country in countries_data)
        
        # Get regions data
        regions = {}
        for country in countries_data:
            region = country.get('region')
            if region:
                if region not in regions:
                    regions[region] = {
                        'population': 0,
                        'countries': 0
                    }
                regions[region]['population'] += country.get('population', 0)
                regions[region]['countries'] += 1
        
        # Sort regions by population
        sorted_regions = dict(sorted(regions.items(), key=lambda item: item[1]['population'], reverse=True))
        
        # Format region population numbers and calculate percentages
        max_region_population = max(region_data['population'] for region_data in regions.values()) if regions else 0
        for region, data in sorted_regions.items():
            data['formatted_population'] = format_population(data['population'])
            # Calculate percentage for bar width (0-100%)
            if max_region_population > 0:
                data['percentage'] = (data['population'] / max_region_population) * 100
            else:
                data['percentage'] = 0
        
        # Get top 5 most populous countries
        top_countries = sorted(countries_data, key=lambda x: x.get('population', 0), reverse=True)[:5]
        
        # Format population numbers
        for country in top_countries:
            country['formatted_population'] = format_population(country.get('population', 0))
        
        world_data = {
            'total_population': format_population(total_population),
            'total_countries': len(countries_data),
            'regions': sorted_regions,
            'top_countries': top_countries
        }
    except Exception as e:
        # If API fails, provide some default data
        world_data = {
            'total_population': 'Data unavailable',
            'total_countries': 'Data unavailable',
            'error': str(e),
            'regions': {},
            'top_countries': []
        }
    
    try:
        countries = [
            {'code': c.get('cca3', ''), 'name': c['name']['common']} for c in countries_data if c.get('cca3') and c.get('name', {}).get('common')
        ]
        countries = sorted(countries, key=lambda x: x['name'])
    except Exception as e:
        # If API fails, provide some default data
        world_data = {
            'total_population': 'Data unavailable',
            'total_countries': 'Data unavailable',
            'error': str(e),
            'regions': {},
            'top_countries': []
        }
        countries = []
    
    # Pass the map HTML and countries to the template
    context = {
        'map_html': map_html,
        'countries': countries,
        'world_data': world_data,
        'selected_country': selected_country
    }
    
    return render(request, 'home.html', context)


def format_population(number):
    """Format large numbers for better readability"""
    if number >= 1_000_000_000:
        return f"{number/1_000_000_000:.2f} Billion"
    elif number >= 1_000_000:
        return f"{number/1_000_000:.2f} Million"
    elif number >= 1_000:
        return f"{number/1_000:.2f} Thousand"
    else:
        return str(number)
