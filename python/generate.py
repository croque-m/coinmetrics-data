from datetime import datetime

import pandas as pd
import asyncio
import httpx
import aiometer

from classes import CatalogV2AssetMetricsInfo, CatalogV2AssetMetricsResponse

API_ROOT = 'https://community-api.coinmetrics.io/v4'
PAGE_SIZE = 10000


async def fetch_data_with_retry(client: httpx.AsyncClient, url: str):
    attempt = 0
    while attempt < 5:
        try:
            resp = await client.get(url, timeout=10)
            # print(resp.text)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"There was an error fetching data from {url}: {e}")
            attempt += 1
            await asyncio.sleep(1)


async def api_fetch(client: httpx.AsyncClient, path: str):
    try:
        resp = await client.get(f'{API_ROOT}/{path}')
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        print(f"HTTP Exception for {e.request.url} - {path}")
    pass


def metric_ids_from_asset_info(asset_info: CatalogV2AssetMetricsInfo) -> set[str]:
    return {
        m.metric
        for m in asset_info.metrics
        if [f for f in m.frequencies if f.frequency == "1d"]
    }

# @star_args
async def query_api_and_write_csv(args):
    total, client, i, metrics, assets = args
    print(f"Fetching {i}/{total} - {datetime.today()} - {assets}")
    url = API_ROOT + f'/timeseries/asset-metrics?page_size={PAGE_SIZE}&metrics={metrics}&assets={assets}&start_time=2024-12-05'
    resp = await fetch_data_with_retry(client, url)
    out_data = resp['data']
    next_page_url = resp.get('next_page_url')
    page = 1
    while next_page_url is not None:
        page += 1
        print(f"....{i}/{total}: page {page}....")
        resp = await fetch_data_with_retry(client, next_page_url)
        out_data.extend(resp['data'])
        next_page_url = resp.get('next_page_url')
    pd.DataFrame(out_data).to_csv(f"csv3/{i}.csv", index=False)


async def main():
    async with httpx.AsyncClient() as client:
        asset_metrics_resp = await api_fetch(client, '/catalog-v2/asset-metrics?page_size=10000')
        await asyncio.sleep(.6)
        asset_metrics = CatalogV2AssetMetricsResponse.from_dict(asset_metrics_resp)
        am_map = asset_metrics.combined_assets_and_metrics()

        total = len(am_map)
        it = [(total, client, i + 1, m, a) for i, (m, a) in enumerate(am_map.items())]
        await aiometer.run_on_each(query_api_and_write_csv, it, max_per_second=.6)


if __name__ == '__main__':
    asyncio.run(main())
