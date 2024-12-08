const fs = require('fs');
const fetch = require('node-fetch');
const path = require('path');
const pl = require('nodejs-polars');

const API_ROOT = 'https://community-api.coinmetrics.io/v4';
const MIN_FETCH_INTERVAL = 600; // rate limit interval in ms (used only for debugging)
const PAGE_SIZE = 10000;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchDataWithRetry(url) {
  let response;
  for (let attempt = 1; 1; attempt++) {
    try {
      response = await fetch(API_ROOT + url);
      if (response.ok) {
        const jsonResponse = await response.json();
        return jsonResponse.data;
      }
	  console.warn(`Fetch attempt ${attempt} failed due to HTTP: ${response.status} ${response.statusText}. See cf-ray: ${response.headers.get('cf-ray')} Retrying...`);
    } catch (error) {
        console.warn(`Fetch attempt ${attempt}: ${error}`);
    }
	await sleep(1000);
  }
}

const emitInfo = msg => {
	console.log(`[INF ${timestamp()}] ${msg}`);
};

const emitVerbose = msg => {
	if (process.env.VERBOSE) {
		emitInfo(msg);
	}
};

const emitErrorAndDie = msg => {
	console.error(`[ERR ${timestamp()}] ${msg} (status: ${lastStatus}`);
	process.exit(1);
};

let lastStatus = null;
const apiFetch = async path => fetch(API_ROOT + path)
	.then(res => {
		lastStatus = res.status;
		return res;
	})
	.then(res => res.json())
	.then(res => res.data);

const fsWrite = (filename, content) => {
	let ticker = filename;
	let oldFilename = path.resolve("../csv", `${ticker}.csv`);
	let oldFrame = pl.readCSV(oldFilename);
	let cols = oldFrame.columns;
	let dtypes = oldFrame.dtypes;
	let dtypeMap = {}
	for (let i = 0; i < cols.length; i++) {
		dtypeMap[cols[i]] = dtypes[i];
	}
	let newFrame = pl.readCSV(content, {dtypes: dtypeMap});
	newFrame.with

	let filteredOldFrame = oldFrame.filter(pl.col("time").lt(pl.col("time").max()));
	let filteredNewFrame = newFrame.join(filteredOldFrame, {on: "time", how:"anti"});
	let outFrame = pl.concat([filteredOldFrame, filteredNewFrame], {how: "diagonal"});

	filename = path.resolve(process.env.OUT, `${ticker}.csv`);
	// fs.writeFileSync(filename, content);
	outFrame.writeCSV(filename)
	emitVerbose(`Written ~${content.length} bytes to ${filename}`);
};

const metricIdsFromAssetInfo = assetInfo => assetInfo.metrics
	.filter(metric => metric.frequencies.find(freq => freq.frequency === '1d'))
	.map(metric => metric.metric);

const dataPointToCsvCols = (dataPoint, metricIds) => metricIds.map(metricId => dataPoint[metricId] ?? '').join(',');

const timestamp = () => new Date().toISOString();

const wait = interval => new Promise(res => setTimeout(res, interval));

const shouldOmitAsset = assetInfo => {
	return assetInfo.metrics == null || assetInfo.metrics.every(metric => metric.metric.startsWith('ReferenceRate'));
};

(async () => {
	const assetIndex = {};
	const assetIds = [];

	// build an asset info index and a list of asset IDs
	const assetInfo = await apiFetch('/catalog/assets');
	if (assetInfo == null) {
		emitErrorAndDie('Failed to fetch asset info');
		process.exit(1);
	}
	for (const info of assetInfo) {
		if (shouldOmitAsset(info)) {
			emitVerbose(`Omitting ${info.asset}`);
			continue;
		}
		assetIndex[info.asset] = info;
		assetIds.push(info.asset);
	}
	assetIds.sort();

	// retrieve metrics for every asset

	const totalAssets = assetIds.length;
	let fetchedAssets = 0;
	let lastFetchTime = 0;

	for (const assetId of (process.env.ASSETS?.split(',') ?? assetIds)) {
		const timeSinceLastFetch = Date.now() - lastFetchTime;
		if (process.env.THROTTLE && timeSinceLastFetch < MIN_FETCH_INTERVAL) {
			emitVerbose(`Pausing for ${MIN_FETCH_INTERVAL - timeSinceLastFetch}ms`);
			await wait(MIN_FETCH_INTERVAL - timeSinceLastFetch);
		}
		fetchedAssets++;
		const info = assetIndex[assetId];
		const metricIds = metricIdsFromAssetInfo(info);

		// fetch data
		emitInfo(`Fetching ${assetId} data with ${metricIds.length} metrics... (${fetchedAssets}/${totalAssets})`);
		lastFetchTime = Date.now();
		if (metricIds.length === 0) {
		    emitInfo(`Skipping asset: ${assetId} because there is no available metrics`)
		    continue
		}
		const seriesData = await fetchDataWithRetry(`/timeseries/asset-metrics/?assets=${assetId}&metrics=${encodeURIComponent(metricIds.join(','))}&page_size=${PAGE_SIZE}`);

		if (seriesData == null) {
			emitErrorAndDie(`Failed to fetch data for ${assetId}`);
		}

		// build CSV
		let csv = `time,${metricIds.join(',')}\n`;
		for (let dataPoint of seriesData) {
			csv += `${dataPoint.time.split('T')[0]},${dataPointToCsvCols(dataPoint, metricIds)}\n`;
		}

		// write to file
		fsWrite(assetId, csv);
		await sleep(750)
	}

	emitInfo('Finished');
})();
