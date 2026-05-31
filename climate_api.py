import logging
import requests
import numpy as np

logger = logging.getLogger('geoapp.climate_api')

OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'


def fetch_openmeteo(points, days=16):
    lats = ','.join(f'{p.y:.4f}' for p in points)
    lons = ','.join(f'{p.x:.4f}' for p in points)

    params = {
        'latitude': lats,
        'longitude': lons,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
        'forecast_days': days,
        'timezone': 'auto',
    }

    logger.info('Fetching Open-Meteo for %d points', len(points))
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, list):
        dates = data[0]['daily']['time']
        t2m_max = np.array([loc['daily']['temperature_2m_max'] for loc in data]).mean(axis=0)
        t2m_min = np.array([loc['daily']['temperature_2m_min'] for loc in data]).mean(axis=0)
        precip = np.array([loc['daily']['precipitation_sum'] for loc in data]).mean(axis=0)
    else:
        dates = data['daily']['time']
        t2m_max = np.array(data['daily']['temperature_2m_max'])
        t2m_min = np.array(data['daily']['temperature_2m_min'])
        precip = np.array(data['daily']['precipitation_sum'])

    t2m_mean = (t2m_max + t2m_min) / 2.0

    result = {
        'dates': dates,
        't2m_mean': t2m_mean.tolist(),
        't2m_max': t2m_max.tolist(),
        't2m_min': t2m_min.tolist(),
        'precipitation': precip.tolist(),
    }
    logger.info('Fetched %d forecast days', len(dates))
    return result


DATA_SOURCES = {
    'Open-Meteo': {
        'fetch': fetch_openmeteo,
        'needs_key': False,
    },
    'ECMWF Open Data (cle requise)': {
        'fetch': None,
        'needs_key': True,
    },
    'Copernicus CDS (cle requise)': {
        'fetch': None,
        'needs_key': True,
    },
    'NASA POWER (gratuit)': {
        'fetch': None,
        'needs_key': False,
    },
}
