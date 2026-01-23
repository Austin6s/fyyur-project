import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
POSTGRES_PWD = os.getenv("POSTGRES_PWD")
DB_NAME = "fyyur_test" if os.getenv("TEST_DATABASE") else "fyyur"
SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:{POSTGRES_PWD}@localhost:5432/{DB_NAME}"
