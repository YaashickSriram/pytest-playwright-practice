import allure
from playwright.sync_api import Page
from pages.login_page import LoginPage
from configs.config import Config

@allure.feature("Authentication")
@allure.severity(allure.severity_level.CRITICAL)
def test_login(app_page, config : Config):
    #login page instance
    login_page = LoginPage(app_page, config)

    #actions
    login_page.navigate()
    login_page.login(username= config["username"], password=config["password"])

    #assertion
    assert login_page.is_logged_in() == True