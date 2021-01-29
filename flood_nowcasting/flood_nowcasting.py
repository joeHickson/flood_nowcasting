"""
Flood Nowcasting
Using the environment agency api to estimate if a section of river is in flood and publicising this via twitter
Useful where key infrastructure is within flood defences and not considered "in flood" by the EA
- such as the E1 / NCN34 along the edge of the river exe between Exeter St Davids and Exeter Quay
"""
from typing import Set

import numpy.polynomial.polynomial as poly
from numpy.core.multiarray import ndarray

from entities import FloodStates, Location
from load_ea_data import get_data


# import matplotlib.pyplot as plt


def main():
    """ Actually do something """

    # loop over locations
    for location in get_locations():
        # load up the data
        x_values, y_values = get_data(location)

        current_level = y_values[-1]
        forecast_levels = nowcast(x_values, y_values)

        # load the current published state and calculate the new state
        current_output_state = get_current_output_state(location)
        new_state = calculate_new_state(
            prior_state=current_output_state,
            current_level=current_level,
            forecast=forecast_levels,
            warn_threshold=location.warn,
            wet_threshold=location.wet
        )

        if new_state != current_output_state:  # publicise change:
            message = location.get_message(new_state)

            publish(location, message)


def nowcast(x_values, y_values):
    # estimate the coefficients
    coefficients = poly.polyfit(x_values, y_values, 2)
    # optionally plot the outcome
    # x_new = np.linspace(x_values[0], x_values[-1] * 1.5, num=len(x_values) * 10)
    # ffit = poly.polyval(x_new, coefficients)
    #
    # plt.plot(x_new, ffit)
    # plt.plot(x_values, y_values, 'o')
    # plt.show()
    # use the calculated coefficients to estimate t+30 and t+60 minutes
    forecast_levels = poly.polyval([x_values[-1] + 1800, x_values[-1] + 3600], coefficients)
    return forecast_levels


def get_locations() -> Set[Location]:
    """
    get a list of all the defined locations
    :return: Set[Location]
    """
    locations = {
        # Exeter flood defence cycle path - trews wier at 3.89 (and slowly falling) path is part covered
        # .../flood-monitoring/data/readings/45128-level-stage-i-15_min-m/2021-01-28T17-45-00Z
        Location(
            name="Exeter flood defence cycle path",
            monitoring_station="45128",
            wet=3.88,
            warn=3.86,
            messages={
                FloodStates.DRY: "Flood defence cycle path all clear",
                FloodStates.WARN: "Possibility of flooding soon on flood defence cycle path",
                FloodStates.CARE: "Flood defence cycle path may be passable",
                FloodStates.WET: "Flood defence cycle path is wet. Plan an alternative route",
                FloodStates.CLEAR_SOON: "Flood defence cycle path may be dry in 1 hour",
                FloodStates.CLEAR_VERY_SOON: "Flood defence cycle path may be dry in 1/2 hour"
            }
        )
    }
    return locations


def get_current_output_state(location: Location) -> FloodStates:
    """
    load the previously published output state
    :param location: Location
    :return: FloodStates
    """
    wet = location.wet
    wet += 1
    return FloodStates.CARE


def calculate_new_state(prior_state: FloodStates, current_level: float, forecast: ndarray, warn_threshold: float,
                        wet_threshold: float) -> FloodStates:
    """
    Calculate the new state for the warning at the given location
    :param prior_state: FloodStates - the old flood state
    :param current_level: float - the latest river level reading
    :param forecast: ndarray - a 2 deep array estimating +30 and +60 minutes based on the previous readings
    :param warn_threshold: float - the water depth warning level for the current location
    :param wet_threshold: float - the water depth considered flooding for the current location
    :return: FloodStates - the new flood state
    """
    calc_state = prior_state
    if current_level < warn_threshold:  # check if need to warn
        if prior_state == FloodStates.DRY and max(forecast) > warn_threshold:
            calc_state = FloodStates.WARN
        else:
            calc_state = FloodStates.DRY
    elif current_level < wet_threshold:  # check if warning issued
        if prior_state > FloodStates.CARE:  # may be passable
            calc_state = FloodStates.CARE
        elif prior_state == FloodStates.DRY:  # issue warning
            calc_state = FloodStates.WARN
    elif prior_state >= FloodStates.WET:  # check if dry soon
        if max(forecast) < wet_threshold:  # down in 30 mins
            calc_state = FloodStates.CLEAR_VERY_SOON
        elif forecast[1] < wet_threshold:  # down in an hour
            calc_state = FloodStates.CLEAR_SOON
    return calc_state


def publish(location: Location, message: str):
    """
    Publish the message to twitter
    :param location: Location
    :param message: str
    :return:
    """
    output = message
    output += f" {location.name}"


if __name__ == '__main__':
    main()
