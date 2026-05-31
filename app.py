import streamlit as st
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import get_provinces, get_communes, get_entity_geometry, get_polygon_sample_points, get_centroid_lonlat
from climate_api import fetch_openmeteo, DATA_SOURCES
from map_utils import build_map

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('geoapp.app')

st.set_page_config(
    page_title='Mini-Projet SIG - Marrakech-Safi',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.title('Tableau de Bord Climatique - Region Marrakech-Safi')

provinces = get_provinces()
province_names = sorted(provinces['libelle_fr'].tolist())

with st.sidebar:
    st.header('Navigation Administrative')

    selected_region = st.selectbox('Region', ['Marrakech-Safi'], disabled=True)

    selected_province = st.selectbox('Province', ['Toutes'] + province_names, index=0)

    if selected_province != 'Toutes':
        communes = get_communes(selected_province)
        commune_names = sorted(communes['FIRST_com_'].tolist()) if not communes.empty else []
        selected_commune = st.selectbox('Commune', ['Toutes'] + commune_names)
    else:
        selected_commune = 'Toutes'

    st.markdown('---')
    st.header('Parametre Climatique')
    parameter = st.radio(
        'Afficher',
        ['Temperature 2m (°C)', 'Precipitation (mm)'],
        index=0,
    )

    st.markdown('---')
    st.header('Source de Donnees')
    source_keys = list(DATA_SOURCES.keys())
    source_labels = []
    for key in source_keys:
        label = key
        if DATA_SOURCES[key].get('needs_key'):
            label += ' (cle requise)'
        source_labels.append(label)

    selected_source_idx = st.radio(
        'Source',
        range(len(source_labels)),
        format_func=lambda i: source_labels[i],
        index=0,
    )
    selected_source = source_keys[selected_source_idx]

    if DATA_SOURCES[selected_source].get('needs_key'):
        st.warning('Cette source necessite une cle API.')
        api_key = st.text_input(
            'Cle API',
            type='password',
            key='api_key_input',
            placeholder='Entrez votre cle API',
        )
        if api_key:
            st.session_state['api_key'] = api_key
    if selected_source != 'Open-Meteo':
        st.info('Seul Open-Meteo est implemente pour le moment.')

    st.markdown('---')
    submit = st.button('Mettre a jour')

if selected_province:
    if selected_commune != 'Toutes':
        level = 'commune'
    elif selected_province != 'Toutes':
        level = 'province'
    else:
        level = 'region'

    commune_name = selected_commune if level == 'commune' else None
    province_name = selected_province if level != 'region' else None

    geometry = get_entity_geometry(
        level=level,
        province_name=province_name,
        commune_name=commune_name,
    )

    points = get_polygon_sample_points(geometry)
    centroid = get_centroid_lonlat(geometry)

    col1, col2 = st.columns([3, 1])

    with col1:
        if level == 'commune':
            entity_name = selected_commune
        elif level == 'province':
            entity_name = selected_province
        else:
            entity_name = 'Marrakech-Safi'
        m = build_map(geometry, entity_name)
        st.components.v1.html(m._repr_html_(), height=500)

    with col2:
        st.metric('Niveau', {'region': 'Region', 'province': 'Province', 'commune': 'Commune'}[level])
        st.metric('Entite', entity_name)
        st.metric('Points d echantillonnage', len(points))
        st.metric('Latitude', f'{centroid[1]:.4f}')
        st.metric('Longitude', f'{centroid[0]:.4f}')

    st.markdown('---')

    if submit or True:
        is_precip = parameter.startswith('Precipitation')

        with st.spinner('Chargement des donnees Open-Meteo...'):
            try:
                result = fetch_openmeteo(points)
                if result is not None:
                    dates = pd.to_datetime(result['dates'])
                    values = result['precipitation'] if is_precip else result['t2m_max']

                    if is_precip:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=dates,
                            y=values,
                            marker_color='#3498DB',
                            name='Precipitations',
                        ))
                        fig.update_layout(
                            title=f'Precipitations - {entity_name}',
                            xaxis_title='Date',
                            yaxis_title='Precipitation (mm)',
                            hovermode='x unified',
                        )
                    else:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=values,
                            mode='lines+markers',
                            marker_color='#E74C3C',
                            name='Temperature',
                        ))
                        fig.update_layout(
                            title=f'Temperature 2m - {entity_name}',
                            xaxis_title='Date',
                            yaxis_title='Temperature (°C)',
                            hovermode='x unified',
                        )

                    st.plotly_chart(fig, width='stretch')

                    with st.expander('Afficher les donnees brutes'):
                        df_display = pd.DataFrame({
                            'Date': dates.strftime('%Y-%m-%d'),
                            'Valeur': values,
                            'Unite': 'mm' if is_precip else '°C',
                        })
                        st.dataframe(df_display, hide_index=True)
                else:
                    st.error('Erreur lors de la recuperation des donnees Open-Meteo.')
            except Exception as e:
                st.error(f'Erreur: {e}')
                logger.exception('Failed to fetch climate data')
