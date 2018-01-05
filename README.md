# James' Flask Boilerplate

I got fed up of creating new Flask projects all the time so I made a Boilerplate.

This code is based on [Nino](https://github.com/ofir123/Nino) with a few customisations.


## Requirements




## Installing (for Development)

```shell
virtualenv -p python3 env/
source env/bin/activate
pip install -r requirements.txt
python setup.py develop

```

## Configuring - Config file

You need to make a copy of `server.cfg.example` and call it `server.cfg`.
You will then need to and provide a valid `SQLALCHEMY_DATABASE_URI`

Many of the other variables in `server.cfg` can be customised for your use case
and there are comments indicating the purpose of each of these variables in
the `server.cfg.example` file

## Configuring - Environment

The framework uses an environment variable `FLASKAPP_SETTINGS`, to locate and
load the `server.cfg` file from which it configures itself.

You also need to configure the `FLASK_APP` environment variable so that the
database migration system works.

```shell
export FLASKAPP_SETTINGS=/home/user/flask_boilerplate/server.cfg
export FLASK_APP=/home/user/flask_boilerplate/flaskapp/wsgi.py:application
...
```

You might want to consider putting these two lines at the end of the `activate`
script in your virtualenv so that they get set up automatically when you enter
your virtualenv.
