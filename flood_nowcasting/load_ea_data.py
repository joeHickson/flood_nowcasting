"""
Everything to do with making the api calls to the EA and parsing the result
"""
import json
from datetime import datetime
from typing import Tuple, List
from urllib.request import urlopen

from entities import Location

BASE_URL = "https://environment.data.gov.uk/flood-monitoring/id/measures/"


def get_data(location: Location, readings: int = 24) -> Tuple[List[int], List[float]]:
    """
    Return x and y data
    :param location: Location
    :param readings: int
    :return: Tuple[List[int], List[float]] - X in seconds, Y in decimal meters
    """
    url = f"{BASE_URL}{location.monitoring_station}-level-stage-i-15_min-m/readings?_sorted&_limit={readings}"
    with urlopen(url) as response:
        raw = response.read()
        json_data = json.loads(raw)
        x_data = [datetime.strptime(reading['dateTime'],
                                    '%Y-%m-%dT%H:%M:%SZ').timestamp() for reading in
                  json_data['items']]
        # need to rebase the time-series as big numbers don't work very well for plotting and
        # exact time doesn't matter, just relative
        x_min = min(x_data)
        x_data = [int(point - x_min) for point in x_data]
        y_data = [float(reading['value']) for reading in json_data['items']]
    return x_data, y_data
