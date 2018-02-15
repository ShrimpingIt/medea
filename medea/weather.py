import gc
from medea.auth import weatherAppId

weatherBaseUrl = "https://api.openweathermap.org/data/2.5/"


def createUrl(apiPath, getParams):
    url = weatherBaseUrl + apiPath + "?"
    url += "&".join(["{}={}".format(key, value) for key, value in getParams.items()])
    gc.collect()
    return url


def createCityUrl(city="Morecambe", country="uk"):
    return createUrl("forecast", dict(
        q="{},{}".format(city, country),
        appid=weatherAppId,
    ))