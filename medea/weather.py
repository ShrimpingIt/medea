import gc
from medea.auth import weatherAppId

weatherBaseUrl = "https://api.openweathermap.org/data/2.5/"


def createUrl(apiPath, **k):
    url = weatherBaseUrl + apiPath + "?"
    url += "&".join(["{}={}".format(key, value) for key, value in k.items()])
    gc.collect()
    return url


def createCityUrl(city="Morecambe", country="uk", **k):
    params = dict(
        q="{},{}".format(city, country),
        appid=weatherAppId.decode('utf-8'),
        cnt=8, # retrieves just 8x 3-hourly records by default (respecting limit of 8192 TLS record buffer)
    )
    params.update(k)
    return createUrl("forecast", **params)
