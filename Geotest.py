# -*- coding: utf-8 -*-
import re

import pytest
from numpy import arange
from requests import request

base_url = "https://nominatim.openstreetmap.org/"


def get_info(url):
    payload = {}
    headers = {}
    response = request("GET", url, headers=headers, data=payload)
    obj_info = response.json()
    return obj_info


test_ids = [
    "The Atomium",
    "The Boyana church",
    "GUM",
    "Eiffel Tower",
    "Statue of Liberty",
    "Tower Bridge",
]


obj_coordinates = {
    "1, Place de l'Atomium - Atomiumplein, City of Brussels, 1020, Belgium": (
        50.89493,
        4.34153,
    ),
    "Boyana Church, Sofia": (42.64480599864499, 23.26622591319648),
    "Red Square, 3, Moscow, 109012": (55.754693599999996, 37.621455538022964),
    "5, Avenue Anatole France,Paris": (48.85850419523487, 2.2945027557477826),
    "Flagpole Plaza, Manhattan Community Board 1, Manhattan, New York, 10004, United States": (
        40.689582377087724,
        -74.04453701258359,
    ),
    "Tower Bridge North Tower": (51.505808162690705, -0.07528999431308425),
}


@pytest.mark.parametrize(
    "obj_address,coordinates",
    obj_coordinates.items(),
    ids=test_ids,
)
def test_direct_geocoding(obj_address, coordinates):
    url = f"{base_url}/search?q={obj_address}&format=json&polygon_geojson=0&addressdetails=1&accept-language=en,ru"
    info = get_info(url)
    coordinates = tuple(round(i, ndigits=5) for i in coordinates)
    checked_obj_coordinates = info[0]["boundingbox"]
    checked_obj_coordinates = [
        round(float(i), ndigits=5) for i in checked_obj_coordinates
    ]
    assert coordinates[0] not in arange(
        checked_obj_coordinates[0], checked_obj_coordinates[1], 0.00001
    ) and coordinates[1] not in arange(
        checked_obj_coordinates[2], checked_obj_coordinates[3], 0.00001
    ), "Сервис указал неверные координаты для указанного адреса"


@pytest.mark.parametrize(
    "obj_address,coordinates", obj_coordinates.items(), ids=test_ids
)
def test_reverse_geocoding(obj_address, coordinates):
    url = f"{base_url}/reverse?lat={coordinates[0]}&lon={coordinates[1]}&format=json&polygon_geojson=0&addressdetails=1&accept-language=en"
    info = get_info(url)
    address = re.findall(r"\d+|\w+", info["display_name"].lower())
    correct_addr_list = re.findall(r"\d+|\w+", obj_address.lower())
    checked_addr_list = [x for x in correct_addr_list if x in address]
    assert (
        correct_addr_list == checked_addr_list
    ), "Сервис вывел неверный адрес для указанной точки"
