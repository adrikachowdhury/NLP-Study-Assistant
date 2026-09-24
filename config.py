"""
Get the project's configuration information and
make it available to the rest of the application.
"""

import os # access to OS env variables
from dotenv import load_dotenv

load_dotenv() # looks for .env file and loads the variables inside it

# Get the value of GEMINI_API_KEY from the environment
# and store it in the Python variable GEMINI_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

"""sanity check to see if the variable is loaded correctly"""
# print(GEMINI_API_KEY is not None)