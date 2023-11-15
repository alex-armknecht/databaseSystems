import mechanicalsoup as ms
import redis


def crawl(browser, r, url):
    print("download the webpage...")
    # download url
    browser.open(url)

    # parse the webpage for links
    a_tags = browser.page.find_all("a")
    hrefs = [a.get("href") for a in a_tags]

    # add links to redis queue
    wikipedia_domain = "https://en.wikipedia.org"
    print("parse the webpage for links...")
    links = [wikipedia_domain+a for a in hrefs if a and a.startswith("/wiki/")]
    r.lpush("links", *links)


r = redis.Redis()
browser = ms.StatefulBrowser()
start_url = "https://en.wikipedia.org/wiki/Ten_Commandments"
r.lpush("links", start_url)
while link := r.rpop("links"):
    if "jesus" in (str(link)).lower():
        print("found jesus!")
        break
    crawl(browser, r, link)
