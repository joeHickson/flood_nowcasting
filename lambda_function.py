import json
import os
import sys

# bugger about with the path to include the package. not the right way really.
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/flood_nowcasting")

from flood_nowcasting.flood_nowcasting import FloodNowcasting


# import sys
#
# # bugger about with the path to include the package. not the right way really.
# sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/flood_nowcasting")


def lambda_handler(event, context):
    try:
        nowcast = FloodNowcasting(app_key=os.environ['APP_KEY'],
                                  app_secret=os.environ['APP_SECRET'],
                                  access_token=os.environ['ACCESS_TOKEN'],
                                  access_token_secret=os.environ['ACCESS_TOKEN_SECRET'])
        nowcast.main()

        return {
            'statusCode': 200,
            'body': json.dumps('Run complete')
        }
    except Exception:

        return {
            'statusCode': 500,
            'body': json.dumps('Server Error')
        }
