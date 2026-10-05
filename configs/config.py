import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    environments = {
        "qa": {
            "base_url": os.getenv("QA_BASE_URL"),
            "username" : os.getenv("QA_USERNAME"),
            "password" : os.getenv("QA_PASSWORD"),
            "timeout" : int(os.getenv("PLAYWRIGHT_TIMEOUT")),
            "navigation_timeout" : int(os.getenv("NAVIGATION_TIMEOUT")),
            "viewport" :{
                "width" : 1920,
                "height" : 1080
            }
        },
        "staging": {
            "base_url": "https://www.saucedemo.com/"
        }
    }

    @classmethod
    def get_environment(cls, environment):
        return cls.environments[environment]

# pytest --env=qa
#        ↓
# environment = "qa"
#        ↓
# config fixture
#        ↓
# Config.get_environment("qa")
#        ↓
# {"base_url": "..."}
#        ↓
# test_login(page, config)
#        ↓
# LoginPage(page, config)
#        ↓
# navigate()
#        ↓
# config["base_url"]
#--------------------------------
# .env
#  ↓
# Config
#  ↓
# config fixture
#  ↓
# test_login
#  ↓
# LoginPage.login()
#--------------------------------
# .env
#  ↓
# Config
#  ↓
# config fixture
#  ↓
# test_login
#  ↓
# LoginPage
#  ↓
# Playwright