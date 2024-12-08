from pathlib import Path

import pandas as pd
from joblib import Parallel, delayed


BASE_DIR = Path(__file__).parent.parent.absolute()
COINMETRICS_CSV_PATH = BASE_DIR / "csv"
ALL_COIN_DATA_PATH = BASE_DIR / "all_coin_data" / "all_coin_data.csv"


def get_frame_for_path(path: Path) -> (str, pd.DataFrame):
    ticker = path.name.split(".")[0]
    frame = pd.read_csv(path, low_memory=False).assign(ticker=ticker)
    frame['time'] = pd.to_datetime(frame.time)
    frame.set_index(['ticker', 'time'], inplace=True)
    return ticker, frame


def main():
    paths = COINMETRICS_CSV_PATH.glob('*.csv')
    it = (delayed(get_frame_for_path)(path) for path in paths)
    frame_dict: dict[str, pd.DataFrame] = dict(Parallel(n_jobs=-1)(it))
    btc_cols = frame_dict['btc'].columns
    appended = pd.concat(frame_dict.values())[btc_cols]
    appended.to_csv(ALL_COIN_DATA_PATH)


if __name__ == '__main__':
    main()
