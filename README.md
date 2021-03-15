# Martini
A kickbase-BOT for earnings-maximization.

## Files
All code can be found in `/martini`. The code is subdivided into the following sections:
* `/kickabse_api`: the extended [Kickbase API](https://github.com/kevinskyba/kickbase-api-python) repository
* `/martini`: root files containing settings, WSGI and URLs
* `/kickbase`: enpoint logic which handles requests (`views.py`)
* `/user`: the controller class that communicates with [Kickbase API](https://github.com/kevinskyba/kickbase-api-python) to handle requests
* `/prediction`: includes heuristic buy and sell prediction

## Prerequisites
Install all prerequisites within a virtual environment:
```
$ python3 -m venv <name_env>
$ source <name_env>/bin/activate
$ pip install -r requirements.txt
```

## Setup for each session
Activate the virtual environment for every new session:
```
$ source <name_env>/bin/activate
```

Run the project (`manage.py` is placed under `/martini`) using the following command:
```
$ python3 manage.py runserver
```

## HTTPS Requests
`POST /login`: (`/logout` is a GET request)
```
{
    "email": string,
    "pw": string
}
```

`POST /userstats`:
```
{
    "LOGIN": {
        "email": string,
        "pw": string
    }
}
```

`POST /player`:
```
{
    "LOGIN": {
        "email": string,
        "pw": string
    }
}
```

`POST /transactions`:
```
{
    "LOGIN": {
        "email": string,
        "pw": string
    }
}
```

`POST /predict`:
```
{
    "LOGIN": {
        "email": string,
        "pw": string
    },  
    "BUY": {
        "type": "LOGIC_BUY", # set to "ML" for machine learning; not implemented, just return an empty array
        "default": boolean,
        "complex_eval": boolean,
        "considered_days": integer
    },
    "SELL": {
        "default": false,
        "min_profit": 5
    }
}
```

`POST /trade` (Buy):
```
{
    "LOGIN": {
        "email": string,
        "pw": string
    },
    "type": "BUY",
    "player_id": string,
    "price": integer
}
```

`POST /trade` (Sell):
```
{
    "LOGIN": {
        "email": string,
        "pw": string
    },
    "type": "SELL",
    "player_id": string,
    "price": integer # enter any; won't be considered
}
```

`POST /offers`:
```
{
    "LOGIN": {
        "email": string,
        "pw": string
    }
}
```

`POST /acceptoffer`:
```
{
    "LOGIN": {
        "email": string,
        "pw": string
    },
    "offer_id": string,
    "player_id": string
}
```

## Credits
Thanks to [kevinskyba](https://github.com/kevinskyba) and his Kickbase API which made **Martini** possible.
