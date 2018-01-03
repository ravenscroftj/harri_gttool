"""Default settings for totem rest"""

import os

default_settings = {}

default_settings["PROJECT_FOLDER"] = os.path.dirname(__file__)

default_settings["STATIC_FOLDER"] = os.path.join(default_settings["PROJECT_FOLDER"] , 'client')

default_settings["TEMPLATE_FOLDER"] = os.path.join(default_settings["STATIC_FOLDER"], 'build')

default_settings["TEMP_FOLDER"] = r'C:\Temp\Nino' if os.name == 'nt' else '/tmp'
