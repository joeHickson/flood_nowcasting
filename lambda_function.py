import json
import os

from flood_nowcasting import flood_nowcasting


def lambda_handler(event, context):
    try:
        flood_nowcasting.setup(app_key=os.environ['APP_KEY'],
                               app_secret=os.environ['APP_SECRET'],
                               access_token=os.environ['ACCESS_TOKEN'],
                               access_token_secret=os.environ['ACCESS_TOKEN_SECRET'])
        flood_nowcasting.main()

        return {
            'statusCode': 200,
            'body': json.dumps('Run complete')
        }
    except Exception:

        return {
            'statusCode': 500,
            'body': json.dumps('Server Error')
        }
