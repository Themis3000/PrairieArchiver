from typing import List, Tuple, Union
from bs4 import BeautifulSoup
import concurrent.futures

from utils import Article, Resource, get_soup, serialize_resources


def analyze_page(soup: BeautifulSoup) -> List[Article]:
    """Handles scraping pages"""
    a_headers = soup.select("li > a.mod_header")
    articles = []
    for a_header in a_headers:
        header = a_header.h3.string
        url = a_header.get("href")
        article = Article(header, url)
        articles.append(article)
    return articles


def get_last_page(soup: BeautifulSoup) -> int:
    """Given the input of a page soup, this gives the output of the last page number"""
    a_last = soup.select("nav > span.last > a")[0]
    last_url = a_last.get("href")
    # The first 11 characters will always be "shows/page/" and the last 5 will always be ".html". This cuts off those
    # characters and grabs the number between that text
    return int(last_url[11:-5])


def analyze_article(soup: BeautifulSoup) -> Union[Resource, None]:
    """Handles scraping articles"""
    # gets download link
    players = soup.select("div.player.player-inline.js-player", limit=1)
    if len(players) == 0:
        return None
    player = players[0]
    source = player.get("data-src")

    # gets title
    header = soup.select("div.page_header > h1.hdg.hdg-1", limit=1)[0]
    header_content = header.string

    # gets date
    info = soup.select("div.hList.hList-divided > span", limit=2)
    if "Show #" in info[0].string:
        date = info[1].string
    else:
        date = info[0].string
    date_content = date.string

    return Resource(header_content, date_content, source)


def get_page_soup(page: int) -> Tuple[int, BeautifulSoup]:
    """Gets the soup for a given page number"""
    assert page > 0, "Page number passed in was less then 1"
    if page == 1:
        return get_soup("https://www.prairiehome.org/index.html")
    return get_soup(f"https://www.prairiehome.org/shows/page/{page}.html")


pages_complete = 0
resources = []
status, first_page = get_page_soup(1)
pages = get_last_page(first_page)


def thread_worker(page: int) -> None:
    """The function used by each worker. Scrapes a single page and each article on it"""
    page_status, page_soup = get_page_soup(page)
    articles = analyze_page(page_soup)

    for article in articles:
        article_status, article_soup = get_soup(article.full_url)
        if article_status != 200:
            print(f"!! failed to fetch article {article.title} ({article.full_url}) with status code {article_status}")
            continue

        resource = analyze_article(article_soup)
        if resource is None:
            print(f"Skipping article {article.title} ({article.full_url}), no player found")
            continue

        resources.append(resource)
    global pages_complete
    pages_complete += 1
    print(f"completed page {pages_complete}/{pages}")


# Starts scraping in multiple threads
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    executor.map(thread_worker, range(pages+1))


# Saves all scraped information to a csv like format file
with open("out.csv", "w") as f:
    serialized_resources = serialize_resources(resources)
    for resource in serialized_resources:
        f.write(resource + "\n")
