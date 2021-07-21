import requests
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Tuple, List, Iterator
from datetime import datetime

session = requests.session()  # a single session is used for all requests


def get_soup(url: str) -> Tuple[int, BeautifulSoup]:
    """handles getting a soup from a given url"""
    page = session.get(url)
    return page.status_code, BeautifulSoup(page.content, 'html.parser')


@dataclass
class Article:
    """Class for keeping track of an article"""
    title: str
    url: str

    def __post_init__(self):
        url_path = self.url.replace("../", "shows/")
        self.full_url = f"https://www.prairiehome.org/{url_path}"


@dataclass
class Resource:
    """Class for keeping track of audio resources"""
    title: str
    date: str
    thumbnail: str
    desc: str
    url: str

    def get_formatted_date(self) -> str:
        dt = datetime.strptime(self.date, "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")  # YYYY-MM-DD format


def serialize_resources(resources: List[Resource]) -> Iterator[str]:
    """serializes a list of resources into a csv like format"""
    for resource in resources:
        yield " /||\\ ".join([resource.title, resource.date, resource.thumbnail, resource.desc, resource.url])


def deserialize_resources(resource_iter: Iterator[str]) -> Iterator[Resource]:
    """deserializes a csv like format into resources"""
    for line in resource_iter:
        elements = line.split(" /||\\ ")
        yield Resource(*elements)


def get_valid_filename(s: str) -> str:
    """Returns a valid filename given an input. Removes any characters unable to be in a filename"""
    s = str(s).strip()
    return re.sub(r'(?u)[^-\w.\[\]() ]', '', s)
