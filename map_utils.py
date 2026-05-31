import folium
import logging
from shapely.geometry import mapping

logger = logging.getLogger('geoapp.map_utils')

OPENTOPOMAP_URL = 'https://tile.opentopomap.org/{z}/{x}/{y}.png'
OPENTOPOMAP_ATTR = (
    'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> '
    '&copy; <a href="https://opentopomap.org">OpenTopoMap</a> '
    '(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
)


def build_map(geometry, entity_name):
    centroid = geometry.centroid
    bounds = geometry.bounds

    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=9,
        tiles='OpenStreetMap',
        control_scale=True,
    )

    folium.TileLayer(
        tiles=OPENTOPOMAP_URL,
        attr=OPENTOPOMAP_ATTR,
        name='MNT - Modele Numerique de Terrain',
        overlay=True,
        opacity=0.7,
    ).add_to(m)

    folium.GeoJson(
        data=mapping(geometry),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#E74C3C',
            'weight': 3,
            'dashArray': '6, 4',
        },
        name='Limite de l entite',
        tooltip=folium.Tooltip(entity_name),
    ).add_to(m)

    folium.LayerControl(position='topright').add_to(m)
    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    title_html = '<div style="position: fixed; top: 10px; left: 80px; z-index: 1000; background-color: white; padding: 8px 16px; border-radius: 4px; box-shadow: 0 0 8px rgba(0,0,0,0.3); font-size: 14px; font-weight: bold;">' + entity_name + '</div>'
    m.get_root().html.add_child(folium.Element(title_html))

    logger.info('Map created for %s', entity_name)
    return m
