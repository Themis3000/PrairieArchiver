"""Downloads scraped resources"""

import concurrent.futures
from pathlib import Path
import eyed3
from eyed3.id3.apple import PCST, PCST_FID, WFED, WFED_FID, TDES, TDES_FID
from utils import deserialize_resources, Resource, get_valid_filename, session

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
    set_metadata(full_filename, resource)
    log_download(resource)


def set_metadata(path: str, resource: Resource) -> None:
    """Adds metadata to audio file"""
    # Loads image
    image = session.get(resource.thumbnail).content

    # Loads audio file
    audio_file = eyed3.load(path)
    if audio_file.tag is None:
        audio_file.initTag()

    # Sets tags
    audio_file.tag.images.set(3, image, 'image/jpeg')
    audio_file.tag.title = resource.title
    audio_file.tag.album = "A Prairie Home Companion"
    audio_file.tag.comments.set(resource.desc)
    # Sets apple specific tags
    audio_file.tag.frame_set[PCST_FID] = PCST()  # Marks self as podcast
    audio_file.tag.frame_set[WFED_FID] = WFED(resource.url)  # Identifies source of the podcast
    audio_file.tag.frame_set[TDES_FID] = TDES(resource.desc)  # Adds description

    audio_file.tag.save()


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
