# _*COMMUNITY EDITION API NO LONGER PULLS REFERENCE RATES*_

It appears that the community API no longer pulls reference rates further back than 7 days. As such the current Coin Metrics repo has overwritten all reference rate information. The `PriceUSD` field is still available for further back than 7 days, however there are a number of large market cap coins that do not have this field. 

This repository is here for historical purposes under the license it was originally released under. I will likely update the current script or add a new one that instead appends to current CSVs rather than overwrites them.

Checkout the last full branch with:

```shell
git checkout 60839f1935448fbd76355e160106a19b3759096f
```

# Free Coin Metrics data archives

These data archives are produced using free Community tier of [Coin Metrics API](https://docs.coinmetrics.io/api).

Scripts for data generation are in [scripts](scripts) directory.

## Available data

### CSV archives

This data is similar to Coin Metrics [Community Data Downloads](https://coinmetrics.io/community-network-data/).

Files:

* `csv/<coin>.csv` - CSV file per coin with all available free metrics
* `https://github.com/coinmetrics/data/archive/refs/heads/master.zip` - All CSV files in a zip archive

The archives are updated daily.

## Stability

We will try to keep the layout and file formats of this repository stable, but there is no guarantee. In particular, sets of available assets and metrics can be changed at any time.

## Environment variables

- `OUT` - **required** - the output folder
- `THROTTLE` - when set, throttles the requests to honor the rate limit
- `VERBOSE` - when set, emits additional messages to STDOUT
- `ASSETS` - generate files for the comma-separated list of assets (default: all assets)

Example of a full local debug invocation to generate only BTC and ETH:

```shell
yarn --cwd scripts
mkdir test
OUT=./test THROTTLE=1 VERBOSE=1 ASSETS=btc,eth node ./scripts/generate.js
```

## License

This data is published in the hope it will be useful, but without any warranty. You are using it at your own risk.

Data is made available under the [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) license.
