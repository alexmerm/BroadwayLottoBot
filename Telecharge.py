from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
from TelechargeShow import TelechargeShow
from typing import List,Set


class Telecharge:
#For now : not keepign track of if alive, quit after everything
    START_PAGE =  "https://my.socialtoaster.com/st/lottery_select/?key=BROADWAY&source=iframe"

    def __init__(self,
                 config = {
        'DEBUG' : True,
        'SELENIUM_URL' : "http://localhost:4444/wd/hub",
        'DEBUG_OFFLINE' : True,
        'FACEBOOK_EMAIL' : "alex.kaish+selenium@gmail.com",
        'FACEBOOK_PASSWORD' : '"WKN2hrz.yap1bku_fcf"',
        'OFFLINE_URL' : 'file:///mnt/offlinePages/Become a User The Shubert Organization, Inc - LotteryPage.html'
    }
    ) -> None:
        self.driver:webdriver.Remote = None
        self.shows:List[TelechargeShow] =  []
        self.config = config

    def driverIsAlive(self):
        """
        Returns True if driver is alive, False otherwise"""
        if(self.driver == None):
            return False
        try:
            self.driver.current_url
            return True
        except: 
            return False

    def setup(self):
        """ Sets up driver and logs into account
        """
        #print starting setup if debug
        if(self.config['DEBUG']):
            print("Starting Setup")
        #
        if(not self.driverIsAlive()):
            self.shows = []
            #print creating new driver if debug
            if(self.config['DEBUG']):
                print("Creating new driver")
            #Enable logging of requests
            chrome_options = webdriver.ChromeOptions()
            chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
            self.driver = webdriver.Remote(command_executor=self.config['SELENIUM_URL'], options=chrome_options)
        if(self.config['DEBUG_OFFLINE']):
            #print getting OFFLINE_URL if debug
            if(self.config['DEBUG']):
                print("Getting OFFLINE_URL")
            self.driver.get(self.config['OFFLINE_URL'])
            print("test")
            print("Setup Complete, self.driver = " + str(self.driver))
        else:
            self.driver.get(self.START_PAGE)
            #Click Facebook Login Button
            #TODO: CHeck if facbook button there, if not then just continue
            facebook_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID,"st_campaign_social_media_button_long_facebook")))
            ActionChains(self.driver).move_to_element(facebook_button).click(facebook_button).perform()
            #Wait until 2 windows open
            WebDriverWait(self.driver,10).until(EC.number_of_windows_to_be(2))
            #Switch to Facebook Login Window
            for handle in self.driver.window_handles:
                if(self.driver.title == "Facebook"):
                    break
                self.driver.switch_to.window(handle)
            #Login to Facebook
            email_field = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID,"email")))
            ActionChains(self.driver).move_to_element(email_field).click().send_keys(self.config['FACEBOOK_EMAIL']).perform()
            password_field = self.driver.find_element(By.ID, "pass")
            ActionChains(self.driver).move_to_element(password_field).click().send_keys(self.config['FACEBOOK_PASSWORD']).perform()
            loginButton = self.driver.find_element(By.ID,"loginbutton")
            ActionChains(self.driver).move_to_element(loginButton).click().perform()
            #Once thorugh Facebook, switch back to main window
            WebDriverWait(self.driver,10).until(EC.number_of_windows_to_be(1))
            self.driver.switch_to.window(self.driver.window_handles[0])
            #Go to lottery tab from top bar
            lottery_button = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,"//a[@href='/st/lottery_select/?key=BROADWAY&source=iframe']")))
            ActionChains(self.driver).move_to_element(lottery_button).click().perform()
            #click the lower lottery button as opposed to results button
            lottery_events_button = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,"//a[@data-section='lottery_block_events']")))
            ActionChains(self.driver).move_to_element(lottery_events_button).click().perform()
            #if debug, print setup complete
        if(self.config['DEBUG']):
            print("Setup Complete, self.driver = " + str(self.driver))
        


    #Keeping Seperate from self.Setup in case there's some issues with page reloading upoon entering lottery
    def getShowDivs(self) -> None:
        """Loads shows into self.shows"""
        if(self.config['DEBUG']):
            print("Getting Show Divs")
        showDivs = self.driver.find_elements(By.XPATH,"//div[@class='lottery_show st_style_page_text_border']")
        self.shows = TelechargeShow.createShowsFromDivs(self.driver, showDivs, config=self.config)
        if(self.config['DEBUG']):
            print("Found " + str(len(self.shows)) + " shows")    
    
    def getShowTitles(self) -> Set[str]:
        """Returns set of show titles"""
        if(not self.driverIsAlive()):
            self.setup()
            self.getShowDivs()
        titles = set()
        for show in self.shows:
            titles.add(show.title)
        return titles
    
    def getShow(self,title):
        """Returns show with given title, or None if no show with that title"""
        if(not self.driverIsAlive()):
            self.setup()
            self.getShowDivs()
        for show in self.shows:
            if(show.title == title):
                return show
        return None
    
    def enterLotteries(self, showsToEnter: dict[str:int]):
        if(not self.driverIsAlive()):
            self.setup()
            self.getShowDivs()
        #call enterLottery for each show
        for show in self.shows:
            if(show.title in showsToEnter.keys()):
                show.enterLottery(showsToEnter[show.title])
     
        # self.driver.quit()








