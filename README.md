# Real Estate Listings Aggregator and Scorer 🏠

This project was created as part of a Bachelor's thesis.

This project scrapes Czech real estate platforms sreality.cz and bezrealitky.cz, unifies the scraped listings data, scores the listings based on user-defined preferences and notifies the user about new listings that match their selected criteria using a Discord webhook. The results are also accessible via a web app, where users can view the listings and set their preferences.

## Features ✨
- Data Scraping 📊: Automates scraping of listings from sreality.cz and bezrealitky.cz.
- Data Cleaning 🧹: Unifies the data format from different sources.
- Listing Scoring ⚖️: Listings are scored based on user defined weights.
- Notification System 📬: User is notified via Discord webhook about new listings that match their preferences.
- Web Interface 💻: A Flask-based web application for viewing the listings and setting preferences.

## Prerequisites 🛠️
- Docker
- Python - developed using Python 3.11 and 3.12.

## Getting started 🚀

Initialize and Update Submodules
```
git submodule init
git submodule update
```
Setup Python Environment
```
python3 -m venv .venv
pip install -r requirements.txt
```
Modify the .env.example file, rename it to .env and insert the discord webhook
```
cp userdata/.env.example userdata/.env
vim userdata/.env
```
Build Docker Containers
```
docker compose build --no-cache
```
Scrape the listings
```
docker compose up crawler
```
Start webapp and schedule scraping every 10 minutes
```
docker compose up -d webapp
(crontab -l 2>/dev/null; echo "*/10 * * * * /usr/bin/docker compose -f $(pwd)/docker-compose.yml up -d crawler") | crontab -
```
## Acessing the web app
http://127.0.0.1:5000

## Accessing logs 📜
```
docker compose logs webapp
docker compose logs crawler
```