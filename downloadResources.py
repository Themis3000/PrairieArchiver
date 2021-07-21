import requests
import concurrent.futures
from pathlib import Path
from utils import deserialize_resources, Resource, get_valid_filename

# Reads scraping data
with open("out.csv", "r") as f:
    resource_iter = deserialize_resources(f)
    resources = [resource for resource in resource_iter]

# Creates completed log file is it doesn't already exist
if not Path("./completed.txt").is_file():
    Path("./completed.txt").touch()

# Reads the created log file and creates a list of all the links already downloaded
with open("completed.txt", "r") as f:
    downloaded = f.read().splitlines()


# create a requests session so that all requests are made under the same tcp connection.
session = requests.session()


def download_resource(resource: Resource) -> None:
    """Downloads a single mp3 file and logs it"""
    filename = get_valid_filename(f"{resource.formatted_date}-{resource.title}")
    full_filename = f"./downloads/{filename}.mp3"
    with session.get(resource.url, stream=True) as r:
        r.raise_for_status()
        with open(full_filename, "wb") as f:
            # Higher chunk size is used in order to achieve better write performance while threaded
            for chunk in r.iter_content(chunk_size=1048576 * 8):  # Chunk size of 8 mebibytes
                f.write(chunk)
    log_download(resource)


def log_download(resource: Resource) -> None:
    """Logs each successful download"""
    with open("completed.txt", "a") as f:
        f.write(f"{resource.url}\n")


def download_if_new(resource: Resource) -> None:
    """Downloads an mp3 file if it hasn't already been downloaded"""
    if resource.url in downloaded:
        print(f"skipping {resource.title} ({resource.url}) - already downloaded")
        return
    download_resource(resource)
    print(f"download {resource.title} ({resource.url}) complete")


# uses multiple threads in order to download more then one file at once
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(download_if_new, resources)
