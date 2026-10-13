import allure
from playwright.sync_api import Page
from utils.logger import get_logger

class LoginPage:

    logger = get_logger() 

    #Locators
    user_name= "#user-name"
    password = "#password"
    login_btn = "#login-button"
    assert_header = ".title"


    def __init__(self, page: Page, config):
        self.page = page
        self.config = config

    @allure.step("Open Login Page")    
    def navigate(self):
        self.logger.info("Navigating to the login page")
        self.page.goto(self.config["base_url"])

    @allure.step("Login as {username}")    
    def login(self, username, password):
        self.logger.info("Attempting Login")

        self.page.locator(self.user_name).fill(username)
        self.page.locator(self.password).fill(password)
        self.page.locator(self.login_btn).click()
        self.logger.info("Login button clicked Successful")

        
        #Logging records the failure; raise preserves the failure for pytest.

    @allure.step("Verify Products page is shown")    
    def is_logged_in(self) -> bool:
       return self.page.locator(self.assert_header).inner_text() == "Products"