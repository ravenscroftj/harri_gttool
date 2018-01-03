from . import create_app

# WSGI tries to import application object - here we create one with the factory
app = application = create_app()
