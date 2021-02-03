"""
Flood Nowcasting
Using the environment agency api to estimate if a section of river is in flood and publicising this via twitter
Useful where key infrastructure is within flood defences and not considered "in flood" by the EA
- such as the E1 / NCN34 along the edge of the river exe between Exeter St Davids and Exeter Quay
"""
import argparse
from typing import Set

import numpy.polynomial.polynomial as poly
import tweepy
from numpy.core.multiarray import ndarray

from entities import FloodStates, Location
from load_ea_data import get_data


# import matplotlib.pyplot as plt
class FloodNowcasting:
    """ nowcasting lib """

    def __init__(self, app_key: str, app_secret: str, access_token: str, access_token_secret: str):
        """
        Configure API
        :param app_key:str
        :param app_secret:str
        :param access_token: str
        :param access_token_secret:str
        :return:
        """
        auth = tweepy.OAuthHandler(app_key, app_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def main(self):
        """ Actually do something """

        # loop over locations
        for location in self.get_locations():
            # load up the data
            x_values, y_values, latest_timestamp = get_data(location)

            current_level = y_values[-1]
            forecast_levels = self.nowcast(x_values, y_values)

            # load the current published state and calculate the new state
            current_output_state = self.get_current_output_state(location)
            new_state = self.calculate_new_state(
                prior_state=current_output_state,
                current_level=current_level,
                forecast=forecast_levels,
                warn_threshold=location.warn,
                wet_threshold=location.wet
            )

            if new_state != current_output_state:  # publicise change:
                message = location.get_message(new_state)
                message += f" (latest reading was at {latest_timestamp: %I:%M %p %d/%m/%Y})"
                self.publish(message)
            #     print(f"published message {message}")
            # else:
            #     print(f"no change for location {location.name}")

    @staticmethod
    def nowcast(x_values, y_values):
        """
        generate the nowcast for the next hour
        :param x_values:
        :param y_values:
        :return:
        """
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

    @staticmethod
    def get_locations() -> Set[Location]:
        """
        get a list of all the defined locations
        :return: Set[Location]
        """
        locations = {
            # Exeter flood defence cycle path - trews wier at 3.89 (and slowly falling) path is part covered
            # .../flood-monitoring/data/readings/45128-level-stage-i-15_min-m/2021-01-28T17-45-00Z
            Location(
                name="Millers Crossing and the Quay",
                monitoring_station="45128",
                wet=3.88,
                warn=3.86,
                messages={
                    FloodStates.DRY: "Flood defence path between Millers Crossing and the Quay is clear",
                    FloodStates.WARN: "Possibility of flooding soon on the flood defence path between "
                                      "Millers Crossing and the Quay",
                    FloodStates.CARE: "Flood defence path between Millers Crossing and the Quay may be passable",
                    FloodStates.WET: "Flood defence path between Millers Crossing and the Quay is wet. "
                                     "Plan an alternative route",
                    FloodStates.CLEAR_SOON: "Flood defence path between Millers Crossing and the Quay "
                                            "may be dry in 1 hour",
                    FloodStates.CLEAR_VERY_SOON: "Flood defence path between Millers Crossing and the Quay "
                                                 "may be dry in 1/2 hour"
                }
            ),
            Location(
                name="St David's and Millers Crossing",
                monitoring_station="45128",
                wet=4.03,
                warn=4.00,
                messages={
                    FloodStates.DRY: "Flood defence path between St David's and Millers Crossing is clear",
                    FloodStates.WARN: "Possibility of flooding soon on the flood defence path between "
                                      "St David's and Millers Crossing",
                    FloodStates.CARE: "Flood defence path between St David's and Millers Crossing may be passable",
                    FloodStates.WET: "Flood defence path between St David's and Millers Crossing is wet. "
                                     "Plan an alternative route",
                    FloodStates.CLEAR_SOON: "Flood defence path between St David's and Millers Crossing "
                                            "may be dry in 1 hour",
                    FloodStates.CLEAR_VERY_SOON: "Flood defence path between St David's and Millers Crossing "
                                                 "may be dry in 1/2 hour"
                }
            )
        }
        return locations

    def get_current_output_state(self, location: Location) -> FloodStates:
        """
        load the previously published output state
        :param location: Location
        :return: FloodStates
        """
        match = None
        recent = self.api.user_timeline(user_id='ExeFloodChannel')
        for tweet in recent:
            if tweet.text in location.messages.values():
                for state in location.messages.keys():
                    if tweet.text == location.messages[state]:
                        match = state
                        break
            if match:
                break

        return match

    @staticmethod
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
        elif current_level >= wet_threshold:
            calc_state = FloodStates.WET
        return calc_state

    def publish(self, message: str):
        """
        Publish the message to twitter
        :param message: str
        :return:
        """
        try:
            self.api.update_status(status=message)
        except tweepy.error.TweepError as error:
            if error.api_code == 187:  # Status is a duplicate
                pass
            else:
                raise


def args():
    """
    Generate args for app
    :return: dictionary of arguments
    """
    parser = argparse.ArgumentParser("Tweet the flood state")
    parser.add_argument("--app_key", type=str, required=True, help="Twitter App Key")
    parser.add_argument("--app_secret", type=str, required=True, help="Twitter App Secret")
    parser.add_argument("--access_token", type=str, required=True, help="Twitter Account Access Token")
    parser.add_argument("--access_token_secret", type=str, required=True, help="Twitter Account Access Token Secret")
    # process arguments
    return parser.parse_args()


if __name__ == '__main__':
    args = args()
    nowcast = FloodNowcasting(app_key=args.app_key, app_secret=args.app_secret, access_token=args.access_token,
                              access_token_secret=args.access_token_secret)
    nowcast.main()
