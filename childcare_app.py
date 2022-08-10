import collections
collections.Iterable = collections.abc.Iterable

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from ipywidgets import embed
import streamlit.components.v1 as components
from address_to_figure import *


padding = 0
st.set_page_config(page_title="NYC Childcare Finder", layout="wide", page_icon="👶")

st.markdown(
    """
<style>

.big-font {
    font-size:150% !important;
}

.stTextInput > label {
    font-size:105%;
    font-weight:bold; color:white;
}

.stSelect_Box > label {
    font-size:105%;
    font-weight:bold; color:white;
}

.stMultiSelect > label {font-size:105%; font-weight:bold; color:white;}

.stNumberInput > label {
    font-size:105%;
    font-weight:bold; color:white;
}

.stSelectbox > label {
    font-size:105%;
    font-weight:bold; color:white;
}

label[data-testid="stMetricLabel"] > div {
    font-size:105%;
    font-weight:bold; color:white;
}

div[data-testid="stMetricValue"] > div {
    font-size:70%;
    font-weight:bold;
    color:white;
}

</style>
""",
    unsafe_allow_html=True,
)

#title###########################
st.title("NYC Childcare Finder")

#Sidebar#########################

# init session value
if 'btn' not in st.session_state:
    st.session_state['btn'] = False


def callback1():
    st.session_state['btn'] = True


def callback2():
    st.session_state['btn'] = False



with st.sidebar:
    st.header('Search Parameters')
    home = st.text_input('Home Address', '7127 Sutton Pl, Flushing, NY 11365', on_change=callback2)
    work = st.text_input('Work Address', '187 Mulberry St, New York, NY 10012', on_change=callback2)
    buffer = number = st.number_input(
        'Buffer Radius (Mile(s))',
        value=0.5,
        min_value=0.1,
        step=0.1, on_change=callback2)

    st.header('Filtering Parameters')
    child_care_type = st.multiselect("Select Childcare Type",
        ['Child Care - Pre School',
        'School Based Child Care',
        'Child Care - Infants/Toddlers',
        'Camp'],
        ['Child Care - Pre School'], on_change=callback2)

    age_range_type = st.multiselect("Select Age Range",
        ['0 YEARS - 2 YEARS',
        '2 YEARS - 5 YEARS',
        '3 YEARS - 5 YEARS',
        '0 YEARS - 16 YEARS',
        '6 YEARS - 16 YEARS'],
        ['0 YEARS - 2 YEARS',
        '2 YEARS - 5 YEARS',
        '3 YEARS - 5 YEARS',
        '0 YEARS - 16 YEARS',
        '6 YEARS - 16 YEARS'], on_change=callback2)

    max_capacity_type = st.multiselect("Select Max Capacity",
        ['<=10', '11-30', '30-50', '50-100', '>100'],
        ['<=10', '11-30', '30-50', '50-100', '>100'], on_change=callback2)

    total_educational_workers_type = st.multiselect("Select Number of Educational workers",
        ['<=1', '1-5', '5-8', '8-15', '>15'],
        ['<=1', '1-5', '5-8', '8-15', '>15'], on_change=callback2)


    number_results = st.number_input(
        """Select Top 'N' Childcare Facilities""",
        value=20,
        min_value=1,
        max_value=100,
        step=1,
        format="%i", on_change=callback2
    )


    st.markdown(
        f"""<p class="small-font">Results limited to available top {number_results} childcare facilities</p>""",
        unsafe_allow_html=True,
    )


    pressed = st.button("Find Childcare", on_click=callback1)

expander = st.sidebar.expander("App Info")
expander.write(
    """
    Users can find top childcare facilities according to their requirements.

    If no results are showing. The user need to relax the search restrictions.

    """
)


### body


app_data = load_app_data()

col1, col2  = st.columns([2,1])
if st.session_state['btn']:
    data_f , _points , _polygon = filter_data(app_data, child_care_type , age_range_type, max_capacity_type, total_educational_workers_type, home, work, buffer, number_results)

### upper container --- 2 cols -- mapp and dataframe

with st.container():
    with col1:
        if st.session_state['btn']:
            st.header('Childcare facility Locations')
            map_figure = make_map_figure(data_f, _points, _polygon, home, work)
            snippet = embed.embed_snippet(views=map_figure)
            html = embed.html_template.format(title="Childcare locations", snippet=snippet)
            components.html(html , height=700)

    with col2:
        if st.session_state['btn']:
            st.header('Childcare Ranking')

            st.dataframe(data_f[['Day Care ID','Rank', 'Center Name','Address']].set_index('Day Care ID'), height=700)

### mid thin container for comparison buttons
if st.session_state['btn']:
    with st.container():
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            f_chioce =st.selectbox(
            'First Choice',
            list(data_f['ID_Name']),
            key=1,
            )
        with col2:
            s_choice = st.selectbox(
            'Second Choice',
            list(data_f['ID_Name']),
            key=2,
            )
        with col3:
            st.write('Compare Selected two Choldcare facilities')
            compare = st.button(label="Compare")

        data_c = data_f[data_f['ID_Name'].isin([f_chioce,s_choice])][['Day Care ID', 'Coordinates', 'Center Name',
                               'Address', 'Phone', 'URL','Rank']]

        data_c1 = data_f[data_f['ID_Name'].isin([f_chioce])][['Day Care ID', 'Center Name', 'Address', 'Phone', 'URL',
        'Borough', 'Zipcode', 'Date Permitted', 'Status', 'Permit Expiration',
        'Program Type', 'Facility Type', 'Child Care Type', 'Age Range',
        'Maximum Capacity',  'Total Educational Workers',
        'Average Total Educational Workers',
        'Violation Rate Percent', 'Average Violation Rate Percent',
        'Public Health Hazard Violation Rate',
        'Average Public Health Hazard Violation Rate',
        'Critical Violation Rate', 'Average Critical Violation Rate',
        'Inspection day Count', 'Inspection Days With Violation',
        'Public Health Hazard Violation Count', 'Critical Violation Count',
        'General Violation Count', 'Total Violation Count',
        'Inspection Data Per Inspection']].reset_index()

        data_c2 = data_f[data_f['ID_Name'].isin([s_choice])][['Day Care ID', 'Center Name', 'Address', 'Phone', 'URL',
        'Borough', 'Zipcode', 'Date Permitted', 'Status', 'Permit Expiration',
        'Program Type', 'Facility Type', 'Child Care Type', 'Age Range',
        'Maximum Capacity',  'Total Educational Workers',
        'Average Total Educational Workers',
        'Violation Rate Percent', 'Average Violation Rate Percent',
        'Public Health Hazard Violation Rate',
        'Average Public Health Hazard Violation Rate',
        'Critical Violation Rate', 'Average Critical Violation Rate',
        'Inspection day Count', 'Inspection Days With Violation',
        'Public Health Hazard Violation Count', 'Critical Violation Count',
        'General Violation Count', 'Total Violation Count',
        'Inspection Data Per Inspection']].reset_index()

    ### bottom thin container for comparison results
    with st.container():
        if compare:
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                st.metric(label ='Child Care Type', value=str(data_c1['Child Care Type'][0]))
                st.metric(label ='Maximum Capacity', value=str(data_c1['Maximum Capacity'][0]))
                st.metric(label ='Total Educational Workers', value=str(data_c1['Total Educational Workers'][0]))
                st.metric(label ='Inspection day Count', value=str(data_c1['Inspection day Count'][0]))
                st.metric(label ='Inspection Days With Violation', value=str(data_c1['Inspection Days With Violation'][0]))
                st.metric(label ='Total Violation Count', value=str(data_c1['Total Violation Count'][0]))
                st.metric(label ='Public Health Hazard Violation Count', value=str(data_c1['Public Health Hazard Violation Count'][0]))
                st.metric(label ='Critical Violation Count', value=str(data_c1['Critical Violation Count'][0]))
                st.metric(label ='General Violation Count', value=str(data_c1['General Violation Count'][0]))



                with st.expander("Detailed Info"):
                    data_c1_ = data_c1[['Day Care ID', 'Center Name', 'Address', 'Phone', 'URL',
                    'Borough', 'Zipcode', 'Date Permitted', 'Status', 'Permit Expiration',
                    'Program Type', 'Facility Type', 'Age Range',
                    'Total Educational Workers',
                    'Average Total Educational Workers',
                    'Violation Rate Percent', 'Average Violation Rate Percent',
                    'Public Health Hazard Violation Rate',
                    'Average Public Health Hazard Violation Rate',
                    'Critical Violation Rate', 'Average Critical Violation Rate']].set_index('Day Care ID').transpose()

                    st.dataframe(data_c1_.astype(str))

                with st.expander("Detailed Inspection Info"):
                    st.dataframe((data_c1['Inspection Data Per Inspection'][0]))



                # st.markdown('<p class="big-font">{}</p>'.format(str(data_c1['Child Care Type'][0])), unsafe_allow_html=True)

                #

            with col2:
                st.metric(label ='Child Care Type', value=str(data_c2['Child Care Type'][0]))
                st.metric(label ='Maximum Capacity', value=str(data_c2['Maximum Capacity'][0]))
                st.metric(label ='Total Educational Workers', value=str(data_c2['Total Educational Workers'][0]))
                st.metric(label ='Inspection day Count', value=str(data_c2['Inspection day Count'][0]))
                st.metric(label ='Inspection Days With Violation', value=str(data_c2['Inspection Days With Violation'][0]))
                st.metric(label ='Total Violation Count', value=str(data_c2['Total Violation Count'][0]))
                st.metric(label ='Public Health Hazard Violation Count', value=str(data_c2['Public Health Hazard Violation Count'][0]))
                st.metric(label ='Critical Violation Count', value=str(data_c2['Critical Violation Count'][0]))
                st.metric(label ='General Violation Count', value=str(data_c2['General Violation Count'][0]))


                with st.expander("Detailed Info"):
                    data_c2_ = data_c2[['Day Care ID', 'Center Name', 'Address', 'Phone', 'URL',
                    'Borough', 'Zipcode', 'Date Permitted', 'Status', 'Permit Expiration',
                    'Program Type', 'Facility Type', 'Age Range',
                    'Total Educational Workers',
                    'Average Total Educational Workers',
                    'Violation Rate Percent', 'Average Violation Rate Percent',
                    'Public Health Hazard Violation Rate',
                    'Average Public Health Hazard Violation Rate',
                    'Critical Violation Rate', 'Average Critical Violation Rate']].set_index('Day Care ID').transpose()

                    st.dataframe(data_c2_.astype(str))

                with st.expander("Detailed Inspection Info"):
                    st.dataframe((data_c2['Inspection Data Per Inspection'][0]))

                with col3:
                    map_figure_2 = make_map_figure_2(data_c, _points, _polygon, home, work)
                    snippet_2 = embed.embed_snippet(views=map_figure_2)
                    html_2 = embed.html_template.format(title="Childcare locations 2", snippet=snippet_2)
                    components.html(html_2 , height=650)
