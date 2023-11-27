import mechanicalsoup as ms
import redis
from elasticsearch import Elasticsearch, helpers
import configparser

# set up config parser
config = configparser.ConfigParser()
config.read('example.ini')

# set up elastic search
es = Elasticsearch(
    cloud_id=config['ELASTIC']['cloud_id'],
    http_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
)


def write_to_elastic(es, url, html):
    link = url.decode("utf-8")
    es.index(
        index='webpages',
        document={
            'url': link,
            'html': html
        })


print(es.info())


# crawl wikipedia
def crawl(browser, r, es, url):
    print("download the webpage...")
    # download url
    browser.open(url)

    # cache page to elestic search
    write_to_elastic(es, url, str(browser.page))
    # parse the webpage for links
    a_tags = browser.page.find_all("a")
    hrefs = [a.get("href") for a in a_tags]
    # add links to redis queue
    wikipedia_domain = "https://en.wikipedia.org"
    print("parse the webpage for links...")
    links = [wikipedia_domain+a for a in hrefs if a and a.startswith("/wiki/")]
    r.lpush("links", *links)


browser = ms.StatefulBrowser()
r = redis.Redis()
r.flushall()

start_url = "https://en.wikipedia.org/wiki/List_of_New_Girl_episodes"
r.lpush("links", start_url)

while link := r.rpop("links"):
    if "jesus" in str(link):
        break
    crawl(browser, r, es, link)
