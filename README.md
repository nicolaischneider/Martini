# Martini

A kickbase-BOT for earnings-maximization.

## Prerequisites
* `virtualenv`
* `django`
* `requests`
* `kickbase_api`
* `djongo`
* `django-cors-headers`
* [MongoDB](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/)

## Setup for each session
Activate the virtual environment for every new session:
```
$ source bin/activate
$ deactivate #to deativate
```

Run the project using the following command:
```
$ python3 manage.py runserver
```

Sync new settings that were set in Settings.py:
```
$ python3 manage.py migrate
```

Save changes in-app:
```
$ python3 manage.py migrate
```

For more help/commands check out the following [Evernote-page](https://www.evernote.com/shard/s223/sh/1f2588a7-1963-757a-3fb3-fc79ad019987/b3334d09643601b749f3418fbd8bd5f7).

## Disclaimer
To connect to Kickbase you first need to add your **Kickbase-Credentials** within the code:
```
> martini
    > kickbase
        > models.py
````

Fill the following line with your credentials:
```
user, leagues = kickbase.login("<mail>", "<password>")
```
