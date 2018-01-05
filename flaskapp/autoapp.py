from . import create_app
from .model import db
from flask_migrate import Migrate

# generate an app using factory function
app = create_app()

# register migration tool
Migrate(app, db)
