# thesis



# Getting started

install Docker - https://docs.docker.com/engine/install/

```
git submodule init
git submodule update
python3 -m venv .venv
pip install -r requirements.txt
docker compose build --no-cache
```
modify the .env.example file, rename it to .env
```
docker compose up -d webapp
(crontab -l 2>/dev/null; echo "*/10 * * * * /usr/bin/docker compose -f $(pwd)/docker-compose.yml up -d crawler") | crontab -
```
# Accessing logs
```
docker compose logs webapp
docker compose logs crawler
```