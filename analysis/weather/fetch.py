import requests
import os
import pandas as pd
import numpy as np

NOAA_TOKEN = os.environ['NOAA_TOKEN']

NOAA_BASE = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/'

def get_data(url, params=None):
    headers = {'token': NOAA_TOKEN}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        raise Exception(r.text)
    return r.json()

def get_stations():
    url = NOAA_BASE + 'locations'
    params = {
        'datasetid': 'GHCND',
        'locationcategoryid': 'CITY',
        'limit': 1000,
    }
    stations = []
    while True:
        data = get_data(url, params)
        stations.extend(data['results'])
        if 'next' not in data['metadata']['resultset']:
            break
        params['offset'] = data['metadata']['resultset']['offset'] + 1000
    return stations

def get_station_data(station_id, start_date, end_date):
    url = NOAA_BASE + 'data'
    params = {
        'datasetid': 'GHCND',
        'stationid': station_id,
        'startdate': start_date,
        'enddate': end_date,
        'limit': 1000,
    }
    data = []
    while True:
        r = get_data(url, params)
        print(r)
        data.extend(r['results'])
        if 'next' not in r['metadata']['resultset']:
            break
        params['offset'] = r['metadata']['resultset']['offset'] + 1000
    return data

def get_station_data_for_date(station_id, date):
    url = NOAA_BASE + 'data'
    params = {
        'datasetid': 'GHCND',
        'stationid': station_id,
        'startdate': date,
        'enddate': date,
        'limit': 1000,
    }
    r = get_data(url, params)
    return r['results']

def get_station_data_for_dates(station_id, start_date, end_date):
    url = NOAA_BASE + 'data'
    params = {
        'datasetid': 'GHCND',
        'stationid': station_id,
        'startdate': start_date,
        'enddate': end_date,
        'limit': 1000,
    }
    data = []
    while True:
        r = get_data(url, params)
        data.extend(r['results'])
        if 'next' not in r['metadata']['resultset']:
            break
        params['offset'] = r['metadata']['resultset']['offset'] + 1000
    return data

def get_station_data_for_dates_and_elements(station_id, start_date, end_date, elements):
    url = NOAA_BASE + 'data'
    params = {
        'datasetid': 'GHCND',
        'stationid': station_id,
        'startdate': start_date,
        'enddate': end_date,
        'limit': 1000,
    }
    data = []
    while True:
        r = get_data(url, params)
        data.extend(r['results'])
        if 'next' not in r['metadata']['resultset']:
            break
        params['offset'] = r['metadata']['resultset']['offset'] + 1000
    return data
