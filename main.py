from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin
from scotch.crawl_urls import CrawlUrls

def crawl(urls: CrawlUrls):
    row = urls.get_new_url()
    while (row is not None):
        url = row[1]
        depth = row[2]
        soup = BeautifulSoup(urlopen(url), "lxml")
        if (depth > 0):
            for tag in soup.find_all("a"):
                href = urljoin(url, tag["href"])
                # TODO: filter url
                urls.add_new_url(href, depth - 1)
        # TODO: process docment
        urls.complete(url)
        row = urls.get_new_url()

if __name__ == "__main__":
    url = "https://calorie.slism.jp/"
    depth = 5
    dbname = "crawl.db"
    urls = CrawlUrls(dbname)
    urls.create_table()
    urls.add_new_url(url, depth)
    crawl(urls)
    urls.drop_table()