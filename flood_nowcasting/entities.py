"""
Entities for the flood nowcasting project
"""
# pylint: disable=R0913,R0903

from enum import Enum
from typing import Dict


class FloodStates(Enum):
    """
    Flood State Enumerations.
    Enum can be compared as an integer for easy logic (<, >, = type comparisons)
    """
    DRY = 10
    WARN = 20
    CARE = 30
    WET = 40
    CLEAR_SOON = 50
    CLEAR_VERY_SOON = 60

    def __int__(self):
        """
        Let it be interpreted as an integer
        :return: int
        """
        return self.value

    # magic methods to allow comparison to numbers!

    def __lt__(self, other):
        return int(self.value) < other

    def __gt__(self, other):
        return int(self.value) > other

    def __eq__(self, other):
        return int(self.value) == other

    def __hash__(self):
        return int(self.value)



class Location:
    """
    Location configuration object
    """

    def __init__(self, name: str, monitoring_station: str, wet: float,
                 warn: float, messages: Dict[FloodStates, str]):
        """

        :param name: str - Name of the location. must be unique
        :param monitoring_station: str - identifier for the monitoring station to use
        :param wet: float - river depth at monitoring station to be considered flooded
        :param warn: float - river depth at monitoring station at which a warning should be issued
        :param messages: Dict[FloodStates,str] - list of messages to output for the change to each state. Should
                                                    contain every FloodStates
        """
        self.name = name
        self.monitoring_station = monitoring_station
        self.wet = wet
        self.warn = warn
        if len(messages) != len(FloodStates):
            raise AttributeError("It seems you have the wrong number of messages")
        self.messages = messages

    def get_message(self, state: FloodStates) -> str:
        """
        Return the string for a given flood state
        :param state: FloodStates
        :return: str
        """
        return self.messages[state]
