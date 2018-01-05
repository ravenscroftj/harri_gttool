from . import create_app
from .model import db
from .cli import register_cli_functions
from flask_migrate import Migrate

# generate an app using factory function
app = create_app()

# register migration tool
Migrate(app, db)

# register cli functions
register_cli_functions(app)
