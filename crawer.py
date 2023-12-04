import mechanicalsoup as ms
import redis
from elasticsearch import Elasticsearch, helpers
from neo4j import GraphDatabase


class Neo4JConnector:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def print_greeting(self, message):
        with self._driver.session() as session:
            greeting = session.execute_write(
                self._create_and_return_greeting, message)
            print(greeting)

    def add_links(self, page, links):
        with self._driver.session() as session:
            session.execute_write(self._create_links, page, links)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)",
                        message=message)
        return result.single()[0]

    @staticmethod
    def _create_links(tx, page, links):
        for link in links:
            tx.run(
                "CREATE (:Page {url: $link}) -[:LINKS_TO]-> (:Page {url: $page})", link=link, page=page)


neo4j_connector = Neo4JConnector(
    "bolt://127.0.0.1:7687", "neo4j", "abeiscool")


def write_to_neo4j(conn, page_url, links):
    neo4j_connector.add_links(page_url, links)


def crawl(browser, r, neo, url):
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
    write_to_neo4j(neo, url, links)


r = redis.Redis()
browser = ms.StatefulBrowser()
start_url = "https://en.wikipedia.org/wiki/Ten_Commandments"
r.lpush("links", start_url)
while link := r.rpop("links"):
    if "jesus" in (str(link)).lower():
        print("found jesus!")
        break
    crawl(browser, r, neo4j_connector, link)
