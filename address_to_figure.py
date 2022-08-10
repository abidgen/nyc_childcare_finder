import dill
import json
import string
from ediblepickle import checkpoint
import gmaps
import pandas as pd
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString
from shapely.geometry import Point
import shapely.geometry as shp_geo
import shapely.wkt as shp_wkt
import pyproj
import polyline
from datetime import datetime
import googlemaps
import collections
import streamlit as st
collections.Iterable = collections.abc.Iterable

from dotenv import load_dotenv
import os


load_dotenv()

# from retrying import retry
@st.experimental_singleton
def load_app_data():
    with open('./data/final_data_for_app.pkl', 'rb') as g:
        final_data_for_app = dill.load(g)

    return final_data_for_app



# cache_dir = 'cache'
# if not os.path.exists(cache_dir):
#     os.mkdir(cache_dir)

API_key =os.getenv('API_key')

g_maps = googlemaps.Client(key=API_key)

gmaps.configure(api_key=API_key)


PROJECTION_IN = pyproj.Proj(
    proj="utm",
    zone=18,  # UTM Zone for NY
    ellps="WGS84",
    datum="WGS84"
)


def toUTM(shp, proj, inv=False):

    geoInterface = shp.__geo_interface__

    shpType = geoInterface['type']
    coords = geoInterface['coordinates']

    if shpType == 'Polygon':
        newCoord = [[proj(*point[::-1]) for point in linring]
                    for linring in coords]
    elif shpType == 'MultiPolygon':
        newCoord = [[[proj(*point[::-1]) for point in linring]
                     for linring in poly] for poly in coords]
    elif shpType == 'LineString':
        newCoord = [proj(*point[::-1]) for point in coords]
    elif shpType == 'Point':
        newCoord = proj(*coords[::-1])

    return shp_geo.shape({'type': shpType, 'coordinates': tuple(newCoord)})


def FromUTM(shp, proj):

    geoInterface = shp.__geo_interface__

    shpType = geoInterface['type']
    coords = geoInterface['coordinates']

    if shpType == 'Polygon':
        newCoord = [[proj(*point, inverse=True)[::-1]
                     for point in linring] for linring in coords]
    elif shpType == 'MultiPolygon':
        newCoord = [[[proj(*point, inverse=True)[::-1] for point in linring]
                     for linring in poly] for poly in coords]
    elif shpType == 'LineString':
        newCoord = [proj(*point, inverse=True)[::-1] for point in coords]
    elif shpType == 'Point':
        newCoord = proj(*coords, inverse=True)[::-1]

    return shp_geo.shape({'type': shpType, 'coordinates': tuple(newCoord)})


def transform_wkt_with_buffer(wkt_str: str, buffer: float) -> str:
    """Transform WKT string to WKT Polygon with buffer.
    Parameters:
    wkt_str (str): WKT or Well-known text representation of geometry
    buffer (float): Buffer length(in meters) surrounding give shape.
    Returns:
    dict: JSON style dict object
    How to use?
    >>> output_wkt = transform_wkt_with_buffer('LINESTRING(76.46019279956818 15.335048625850606,76.46207302808762 15.334717526558398)', 10)
    """

    shp_obj = shp_wkt.loads(wkt_str)

    init_shape_utm = toUTM(shp_obj, PROJECTION_IN)
    buffer_shape_utm = init_shape_utm.buffer(buffer)
    buffer_shape_lonlat = FromUTM(buffer_shape_utm, PROJECTION_IN)
    return buffer_shape_lonlat





# @checkpoint(key=string.Template('get_home_ponits_{0}.pkl'), work_dir=cache_dir,  refresh=False)
def get_home_ponits(home=None):
    result = g_maps.geocode(home)
    address_point = [result[0]['geometry']['location']
                     ['lat'], result[0]['geometry']['location']['lng']]
    address_point_wkt = Point(address_point).wkt
    return address_point, address_point_wkt


#     if home and work :
#     directions_result = g_maps.directions(home,
#                                      work,
#                                      mode="driving",
#                                      departure_time=now)

#     route_points = polyline.decode(directions_result[0]['overview_polyline']['points'])
#     route_points_wkt = LineString(route_points).wkt
#     return route_points, route_points_wkt

# @checkpoint(key=string.Template('get_home_work_ponits_{0}_{1}.pkl'), work_dir=cache_dir,  refresh=False)
def get_home_work_ponits(home=None, work=None):
    now = datetime.now()
    directions_result = g_maps.directions(home,
                                          work,
                                          mode="driving",
                                          departure_time=now)

    route_points = polyline.decode(
        directions_result[0]['overview_polyline']['points'])
    route_points_wkt = LineString(route_points).wkt
    return route_points, route_points_wkt

@st.cache
def get_polygon(home=None, work=None, buffer=1):
    buffer_meters = buffer * 1609.34
    if home and work:
        _points, _points_wkt = get_home_work_ponits(home, work)
    elif home and not work:
        _points, _points_wkt = get_home_ponits(home)

    _polygon = transform_wkt_with_buffer(_points_wkt, buffer_meters)

    return _points, _polygon


@st.cache
def filter_data(data, child_care_type , age_range_type, max_capacity_type, total_educational_workers_type, home=None, work=None, buffer=1, number_results=20):

    def filter_fn(row, polygon_):
        if polygon_.contains(row['_coordinate_Point']):
            return True
        else:
            return False


    _points, _polygon = get_polygon(home, work, buffer)

    a = data.apply(filter_fn, polygon_=_polygon, axis=1)
    b = data['Child Care Type'].isin(child_care_type)
    c = data['Age Range'].isin(age_range_type)
    d = data['Max Capacity Range'].isin(max_capacity_type)
    e = data['Total Educational Workers Range'].isin(total_educational_workers_type)

    data_f = data[a & b & c & d & e].sort_values(['Safety score','Inspection day Count'],ascending=[False, False] )[:number_results]
    data_f['Rank'] = data_f[["Safety score","Inspection day Count"]].apply(tuple,axis=1)\
             .rank(method='dense',ascending=False).astype(int)

    return data_f.reset_index().drop('index',axis=1) , _points , _polygon

@st.experimental_memo
def make_map_figure(filtered_data, _points, _polygon, home=None, work=None):
    figure_layout = {
        'width': 'auto',
        'height': '700px',
        # 'padding': '1px'
    }
    json_data = json.loads(filtered_data[['Day Care ID', 'Coordinates', 'Center Name',
                           'Address', 'Phone', 'URL','Rank']].to_json(orient='records'))

    fig = gmaps.figure(layout=figure_layout, center=(
        _polygon.centroid.coords.xy[0][0], _polygon.centroid.coords.xy[1][0]), zoom_level=12)

    buffer_feature = [
        gmaps.Polygon(
            list(_polygon.exterior.coords),
            stroke_color='rgba(200, 0, 0, 0.6)', fill_color='rgba(200, 0, 0, 0.6)'
        )]

    drawing = gmaps.drawing_layer()

    if home and work:
        home_work_location = [_points[0], _points[-1]]
        home_work_info = [home, work]
        marker_layer = gmaps.marker_layer(
            home_work_location, info_box_content=home_work_info)
        drawing.features =[gmaps.Line(_points[i], _points[i+1], stroke_weight=4,
                                   stroke_color='rgba(0,191,255, 1)') for i in range(len(_points)-1)] + buffer_feature
        fig.add_layer(marker_layer)
    elif home and not work:
        marker = gmaps.Marker(_points, info_box_content=home)
        drawing.features =  buffer_feature + [marker]

    locations = filtered_data['Coordinates']
    info_box_template = """
    <dl>
    <dd><b>ID: </b>{Day Care ID}</dd>
    <dd><b>Center Name: </b>{Center Name}</dd>
    <dd><b>Address: </b>{Address}</dd>
    <dd><b>Phone: </b>{Phone}</dd>
    <dd><b>URL: </b>{URL}</dd>
    <dd><b>Rank: </b>{Rank}</dd></dl>
    """
    _info = [info_box_template.format(**facility) for facility in json_data]
    symbol_layer = gmaps.symbol_layer(locations, fill_color='rgba(0, 0, 0, 0.8)',
                                      stroke_color='rgba(0, 200, 0, 0.5)', scale=6, info_box_content=_info)

    fig.add_layer(symbol_layer)
    fig.add_layer(drawing)

    return fig



@st.experimental_memo
def make_map_figure_2(filtered_data, _points, _polygon, home=None, work=None):
    figure_layout = {
        'width': 'auto',
        'height': '600px',
        # 'padding': '1px'
    }
    json_data = json.loads(filtered_data[['Day Care ID', 'Coordinates', 'Center Name',
                           'Address', 'Phone', 'URL','Rank']].to_json(orient='records'))

    fig = gmaps.figure(layout=figure_layout, center=(
        _polygon.centroid.coords.xy[0][0], _polygon.centroid.coords.xy[1][0]), zoom_level=11)

    buffer_feature = [
        gmaps.Polygon(
            list(_polygon.exterior.coords),
            stroke_color='rgba(200, 0, 0, 0.6)', fill_color='rgba(200, 0, 0, 0.6)'
        )]

    drawing = gmaps.drawing_layer()

    if home and work:
        home_work_location = [_points[0], _points[-1]]
        home_work_info = [home, work]
        marker_layer = gmaps.marker_layer(
            home_work_location, info_box_content=home_work_info)
        drawing.features =[gmaps.Line(_points[i], _points[i+1], stroke_weight=4,
                                   stroke_color='rgba(0,191,255, 1)') for i in range(len(_points)-1)] + buffer_feature
        fig.add_layer(marker_layer)
    elif home and not work:
        marker = gmaps.Marker(_points, info_box_content=home)
        drawing.features =  buffer_feature + [marker]

    locations = filtered_data['Coordinates']
    info_box_template = """
    <dl>
    <dd><b>ID: </b>{Day Care ID}</dd>
    <dd><b>Center Name: </b>{Center Name}</dd>
    <dd><b>Address: </b>{Address}</dd>
    <dd><b>Phone: </b>{Phone}</dd>
    <dd><b>URL: </b>{URL}</dd>
    <dd><b>Rank: </b>{Rank}</dd></dl>
    """
    _info = [info_box_template.format(**facility) for facility in json_data]
    symbol_layer = gmaps.symbol_layer(locations, fill_color='rgba(0, 0, 0, 0.8)',
                                      stroke_color='rgba(255, 0, 0, 0.5)', scale=6, info_box_content=_info)

    fig.add_layer(symbol_layer)
    fig.add_layer(drawing)

    return fig
