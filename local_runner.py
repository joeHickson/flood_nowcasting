import yaml
import logging
from flood_nowcasting.flood_nowcasting import FloodNowcasting

logging.basicConfig(filename='cron.log', level=logging.INFO)

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


if __name__ == '__main__':
    logging.info("running")
    config = load_config()

    nowcast = FloodNowcasting(app_key=config['APP_KEY'],
                              app_secret=config['APP_SECRET'],
                              access_token=config['ACCESS_TOKEN'],
                              access_token_secret=config[
                                  'ACCESS_TOKEN_SECRET'])
    nowcast.main()
    logging.info("run complete")
