import logging

import yaml

from flood_nowcasting.flood_nowcasting import FloodNowcasting

logging.basicConfig(filename='run.log', level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


if __name__ == '__main__':
    logging.info("run starting")
    config = load_config()

    nowcast = FloodNowcasting(app_key=config['APP_KEY'],
                              app_secret=config['APP_SECRET'],
                              access_token=config['ACCESS_TOKEN'],
                              access_token_secret=config[
                                  'ACCESS_TOKEN_SECRET'])
    nowcast.main()
    logging.info("run complete")
