import requests
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Tuple, List, Iterator

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
    url: str


def serialize_resources(resources: List[Resource]) -> Iterator[str]:
    """serializes a list of resources into a csv like format"""
    for resource in resources:
        yield " /||\\ ".join([resource.title, resource.date, resource.url])


def deserialize_resources(resources_str: str) -> List[Resource]:
    """deserializes a csv like format into a list of resources"""
    resources = []
    for line in resources_str.split("\n"):
        elements = line.split(" /||\\ ")
        if len(elements) != 3:
            continue
        resource = Resource(*elements)
        resources.append(resource)
    return resources


def get_valid_filename(s: str) -> str:
    """Returns a valid filename given an input. Removes any characters unable to be in a filename"""
    s = str(s).strip()
    return re.sub(r'(?u)[^-\w.\[\]() ]', '', s)
