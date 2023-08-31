india_alerts = {
    "data": [{"SUM(alerts)": 28514}],
    "meta": {
        "cloneUrl": {
            "http_method": "POST",
            "url": "/v1/dataset/4145f642-5455-4414-b214-58ad39b83e1e/clone",
            "body": {
                "dataset": {
                    "datasetUrl": "/v1/query/4145f642-5455-4414-b214-58ad39b83e1e?sql=SELECT%20SUM%28alerts%29%20FROM%20data%20WHERE%20polyname%20%3D%20%27gadm28%27%20AND%20iso%20%3D%20%27IDN%27%20AND%20%28alert_date%20%3E%3D%20%272001-01-01%27%20AND%20alert_date%20%3C%3D%20%272018-09-25%27%29%20and%20adm1%20%3D%201",
                    "application": ["your", "apps"],
                }
            },
        }
    },
}
