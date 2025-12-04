import os
import sys
import pickle
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = logging.getLogger(__name__)


def main():
    """Utility script to add EV loads and (optionally) calculate irradiances.

    This file previously executed code at import time and printed debug lines.
    To avoid side-effects on import, the behavior is wrapped in main()
    and uses logging instead of print. Run it as a script when needed.
    """

    # Add Load_EV_kW_no_SC & Load_EV_kW_with_SC columns to each dataset
    def load_and_add(path):
        with open(path, 'rb') as f:
            df = pickle.load(f)
        df.add_EV_load()
        with open(path, 'wb') as f:
            pickle.dump(df, f)
        logger.info("Processed %s", path)

    load_and_add('data/initialized_dataframes/pd_S_30')
    load_and_add('data/initialized_dataframes/pd_EW_30')
    load_and_add('data/initialized_dataframes/pd_EW_opt_32')
    load_and_add('data/initialized_dataframes/pd_S_opt_37.5')
    load_and_add('data/initialized_dataframes/pd_E_30')
    load_and_add('data/initialized_dataframes/pd_W_30')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
