import datetime
from flask import make_response
import feedparser
import json
import urllib3
import urllib
from flask import Flask, render_template
from markupsafe import escape
from flask import request

app = Flask(__name__)

BBC_FEED = "http://feeds.bbci.co.uk/news/rss.xml"


RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {
    'publication': 'bbc',
    'city': 'London,UK'
}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=98fb7cf5323034819f13a187acf11f66"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=<your-api-key-here>"


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]

@app.route("/")
def home():
    #get customized headlines, based on user inpur or default
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)
    # get customized weather base on user input or default
    city = get_value_with_fallback("city")
    weather = get_weather(city)
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    response = make_response(render_template("home.html",
        articles=articles,
        weather=weather))
    expires=datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_weather(query):
    query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query)
    with urllib.request.urlopen(url) as response:
        data = response.read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {
            "description":
                    parsed["weather"][0]["description"],
                    "temperature": parsed["main"]["temp"],
                    "city": parsed["name"],
                    'country': parsed["sys"]["country"]
                }
    return weather




if __name__ == '__main__':
    app.run(port=5000, debug=True)