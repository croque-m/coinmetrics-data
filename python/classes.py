from dataclasses import dataclass
from typing import Optional

import pandas as pd


# @dataclass
# class CatalogV2AssetMetricsInfo:
#     pass



@dataclass
class AssetMetricFrequency:
    frequency: str
    min_time: str
    max_time: str
    min_height: Optional[str] = None
    max_height: Optional[str] = None
    min_hash: Optional[str] = None
    max_hash: Optional[str] = None
    community: Optional[str] = None
    experimental: Optional[str] = None


@dataclass
class MetricsId:
    metric: str
    frequencies: list[AssetMetricFrequency]

    @classmethod
    def from_dict(cls, metric):
        return cls(
            metric=metric.get('metric'),
            frequencies=[AssetMetricFrequency(**f) for f in metric.get('frequencies')]
        )


@dataclass
class CatalogV2AssetMetricsInfo:
    asset: str
    metrics: list[MetricsId]

    @classmethod
    def from_dict(cls, asset_metrics_info):
        return cls(
            asset=asset_metrics_info.get("asset"),
            metrics=[MetricsId.from_dict(m) for m in asset_metrics_info.get('metrics')]
        )

    def one_day_metrics(self):
        return {
            m.metric
            for m in self.metrics
            if [f for f in m.frequencies if f.frequency == "1d"]
        }


@dataclass
class CatalogV2AssetMetricsResponse:
    data: list[CatalogV2AssetMetricsInfo]
    next_page_token: str
    next_page_url: str

    @classmethod
    def from_dict(cls, asset_metrics_response):
        return cls(
            data=[CatalogV2AssetMetricsInfo.from_dict(o) for o in asset_metrics_response.get('data')],
            next_page_token=asset_metrics_response.get('next_page_token'),
            next_page_url=asset_metrics_response.get('next_page_url')
        )

    def assets_with_one_day_metrics(self):
        return {
            a.asset: a.one_day_metrics()
            for a in self.data
            if a.one_day_metrics()
        }

    def combined_assets_and_metrics(self):
        series = pd.Series(self.assets_with_one_day_metrics()).apply(lambda x: ",".join(sorted(x)))
        grouped: pd.Series = series.groupby(series).apply(lambda x: ",".join(sorted(x.index)))
        return grouped.to_dict()



if __name__ == '__main__':

    import requests

    resp = requests.get('https://community-api.coinmetrics.io/v4/catalog-v2/asset-metrics?page_size=10000')
    resp.raise_for_status()

    processed = CatalogV2AssetMetricsResponse.from_dict(resp.json())
    print(processed)
