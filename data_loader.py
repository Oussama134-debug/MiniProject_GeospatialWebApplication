import geopandas as gpd
import os
import logging
import numpy as np
from shapely import Point

logger = logging.getLogger('geoapp.data_loader')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

_REGIONS = None
_PROVINCES = None
_COMMUNES = None
_MS_REGION = None
_MS_PROVINCES = None
_MS_COMMUNES = None


def _load_all():
    global _REGIONS, _PROVINCES, _COMMUNES
    global _MS_REGION, _MS_PROVINCES, _MS_COMMUNES
    if _REGIONS is not None:
        return

    path_r = os.path.join(DATA_DIR, 'Regions_WGS84.shp')
    path_p = os.path.join(DATA_DIR, 'Provinces_WGS84.shp')
    path_c = os.path.join(DATA_DIR, 'communes_WGS84.shp')

    _REGIONS = gpd.read_file(path_r).to_crs(epsg=4326)
    _PROVINCES = gpd.read_file(path_p).to_crs(epsg=4326)
    _COMMUNES = gpd.read_file(path_c).to_crs(epsg=4326)

    _MS_REGION = _REGIONS[_REGIONS['code_reg'] == 7.0].iloc[0]
    _MS_PROVINCES = _PROVINCES[_PROVINCES['code_reg'] == 7.0].copy()
    ms_prov_names = _MS_PROVINCES['libelle_fr'].tolist()
    _MS_COMMUNES = _COMMUNES[_COMMUNES['FIRST_prov'].isin(ms_prov_names)].copy()

    logger.info('Loaded: %d MS provinces, %d MS communes', len(_MS_PROVINCES), len(_MS_COMMUNES))


def get_provinces():
    _load_all()
    return _MS_PROVINCES[['code_prov', 'libelle_fr']].sort_values('libelle_fr')


def get_communes(province_name):
    _load_all()
    com = _MS_COMMUNES[_MS_COMMUNES['FIRST_prov'] == province_name].copy()
    return com[['CC_g', 'FIRST_com_']].sort_values('FIRST_com_')


def get_entity_name(level, province_name=None, commune_name=None):
    _load_all()
    if level == 'region':
        return _MS_REGION['libelle_fr']
    elif level == 'province':
        return province_name
    elif level == 'commune':
        return commune_name
    return 'Marrakech-Safi'


def get_entity_geometry(level, province_name=None, commune_name=None):
    _load_all()
    if level == 'region':
        return _MS_REGION['geometry']
    elif level == 'province':
        row = _MS_PROVINCES[_MS_PROVINCES['libelle_fr'] == province_name]
        if len(row) == 0:
            return _MS_REGION['geometry']
        return row.iloc[0]['geometry']
    elif level == 'commune':
        row = _MS_COMMUNES[(_MS_COMMUNES['FIRST_prov'] == province_name) & (_MS_COMMUNES['FIRST_com_'] == commune_name)]
        if len(row) == 0:
            return get_entity_geometry('province', province_name)
        return row.iloc[0]['geometry']
    return _MS_REGION['geometry']


def get_polygon_sample_points(geometry, target_points=9):
    bounds = geometry.bounds
    minx, miny, maxx, maxy = bounds
    grid_size = max(3, int(np.sqrt(target_points)) + 1)
    xs = np.linspace(minx, maxx, grid_size)
    ys = np.linspace(miny, maxy, grid_size)
    points = []
    for x in xs:
        for y in ys:
            p = Point(x, y)
            if geometry.contains(p):
                points.append(p)
    if not points:
        centroid = geometry.centroid
        points = [centroid]
    return points


def get_centroid_lonlat(geometry):
    c = geometry.centroid
    return c.y, c.x


def get_bbox(geometry):
    return geometry.bounds
