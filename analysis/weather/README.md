# Weather

Pulling weather data from NOAA for every ZIP code
and computing the number of rainy, sunny, cloudy,
snowy, and extreme weather days within a year

## Install

On a Mac from scratch:

```bash
python3 -m venv env
pip install -r requirements.txt
```

Copy `.env.template` to `.env` and fill in the values.

## Run

```bash
$(cat .env) python fetch.py
```
