# Prairie archiver
This script is meant to archive all radio broadcasts as published on https://www.prairiehome.org/index.html. This script leverages multi threading for faster scraping and downloads, as well as progress saving so that if the script is stopped for any reason it can pick up right where it left off.

the title of the audio files are in the following format: `{article title} [{article post date}]`, where `article` is a single post as seen on the home page of prairie home

Run main.py in order to start this script. the process is completely automatic and all downloads will be put into `./downloads`