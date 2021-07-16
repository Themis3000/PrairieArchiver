"""A really, really simple script that links the web scraper and media downloader scripts into one."""

from pathlib import Path

if not Path("./out.csv").is_file():
    print("Running resource grabber and scraping webpages...")
    import resourceGrabber

print("Running resource downloader and downloading audio files...")
import downloadResources
print("scraping and downloads complete!")
