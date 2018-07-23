# Fires Summary Microservice Overview

Query MODIS and VIIRS fire alerts with the [Global Forest Watch (GFW)](http://globalforestwatch.org) API

- Analyze datasets by Country, State and Districts (defined by the [GADM Database](http://www.gadm.org/))
- Analyze datasets by GFW Land Use features (Managed Forest Concessions, Oil Palm Concessions, Mining Concessions and Wood Fiber Concessions- available in select countries)
- Analyze datasets by Protected Areas (defined by the [WDPA database](http://www.wdpa.org/))
- Summarize analysis results by day, week, month, quarter or year
- Get dataset date range/ latest date

## API Endpoints
For endpoint documentation, please visit our [API documentation page for Fires](https://production-api.globalforestwatch.org/documentation/#/?tags=Fires)

# Getting Started
Perform the following steps:
* [Install docker](https://docs.docker.com/engine/installation/)
* [Install control tower](https://github.com/control-tower/control-tower)
* Clone this repository: ```git clone https://github.com/gfw-api/fires-summary-stats.git```
* Enter in the directory (cd fires-summary-stats)
* Open a terminal (if you have mac or windows, open a terminal with the 'Docker Quickstart Terminal') and run the gladanalysis.sh shell script in development mode:

```ssh
./fireSummary.sh develop
```
## Testing
Testing API endpoints

```ssh
./fireSummary.sh test
```

## Config

## register.json
This is the configuration file for the rest endpoints in the microservice. This json connects to the API Gateway. It contains variables such as:
* #(service.id) => Id of the service set in the config file by environment
* #(service.name) => Name of the service set in the config file by environment
* #(service.uri) => Base uri of the service set in the config file by environment

Example:
````
{
	"name": "#(service.name)",
	"endpoints": [
		{
			"path": "/v1/fire-alerts/summary-stats/:polyname/:iso",
			"method": "GET",
			"binary": true,
			"redirect": {
				"method": "GET",
				"path": "/api/v1/fire-alerts/summary-stats/:polyname/:iso"
			}
		},
		{
		"path": "/v1/fire-alerts/summary-stats/:polyname/:iso/:adm1_code",
		"method": "GET",
		"binary": true,
		"redirect": {
			"method": "GET",
			"path": "/api/v1/fire-alerts/summary-stats/:polyname/:iso/:adm1_code"
					}
		},
		{
		"path": "/v1/fire-alerts/summary-stats/:polyname/:iso/:adm1_code/:adm2_code",
		"method": "GET",
		"binary": true,
		"redirect": {
			"method": "GET",
			"path": "/api/v1/fire-alerts/summary-stats/:polyname/:iso/:adm1_code/:adm2_code"
					}
		}
	]
}
````
