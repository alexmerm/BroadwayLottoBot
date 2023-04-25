from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
import re
import time



class Telecharge:
#For now : not keepign track of if alive, quit after everything
    START_PAGE =  "https://my.socialtoaster.com/st/lottery_select/?key=BROADWAY&source=iframe"

    config = {
        'DEBUG' : True,
        'SELENIUM_URL' : "http://localhost:4444/wd/hub",
        'DEBUG_OFFLINE' : True,
        'FACEBOOK_EMAIL' : "alex.kaish+selenium@gmail.com",
        'FACEBOOK_PASSWORD' : '"WKN2hrz.yap1bku_fcf"',
        'OFFLINE_URL' : 'file:///mnt/offlinePages/Become a User The Shubert Organization, Inc - LotteryPage.html'
    }

    def __init__(self) -> None:
        self.driver = None

    def driverIsAlive(self):
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
            #print creating new driver if debug
            if(self.config['DEBUG']):
                print("Creating new driver")
            chrome_options = webdriver.ChromeOptions()
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
        print("Setup Complete, self.driver = " + str(self.driver))
        if(self.config['DEBUG']):
            print("Setup Complete, self.driver = " + str(self.driver))
        return self.driver



    def getShowDivs(self) -> dict[str:list[WebElement]]:
        self.setup()
        if(self.config['DEBUG']):
            print("Getting Show Divs")
        shows = {}
        showDivs = self.driver.find_elements(By.XPATH,"//div[@class='lottery_show st_style_page_text_border']")
        if(self.config['DEBUG']):
            print("Found " + str(len(showDivs)) + " shows")
        for div in showDivs:
            title_block = div.find_element(By.CLASS_NAME,"lottery_show_title")
            title = title_block.text
            if(title != ''):
                if(title in shows):
                    shows[title].append(div)
                else: 
                    shows[title] = [div]
        if(self.config['DEBUG']):
            print("Found " + str(len(shows)) + " shows")    
        return shows
    
    def getShows(self):
        showDivs = self.getShowDivs()
        showList = showDivs.keys()
        self.driver.quit()
        return showList
    
    def enterLotteries(self, showsToEnter: dict[str:int]):
        showDivs = self.getShowDivs()
        #call enterLottery for each show
        for show in showsToEnter.keys():
            for performance in showDivs[show]:
                self.enterLottery(show,performance, showsToEnter[show])
                time.sleep(1)
        #self.driver.quit()

    
    #Assume Setup
    def enterLottery(self,showTitle: str, showDiv : list[WebElement], numTickets: int):
        if(self.config['DEBUG']):
            print("Entering " + showTitle)
        entered_text = showDiv.find_element(By.CLASS_NAME,"entered-text")
        if (entered_text.is_displayed()):
            if(self.config['DEBUG']):
                print("already entered for " + showTitle)
            return
        
        #Get Event ID
        onclick = showDiv.get_attribute("onclick")
        if(self.config['DEBUG']):
            print("onclick: " + onclick)
        event_id = re.search(r'\d+', onclick).group()
        if(self.config['DEBUG']):
            print("event_id: " + event_id)
        price = showDiv.find_element(By.CLASS_NAME,"lottery_show_price_discount").text
        if(self.config['DEBUG']): 
            print("price: " + price)
        #Select No of Tickets
        if(self.config['DEBUG']):
            print("numTickets: " + str(numTickets))
        ticketSelect= Select(showDiv.find_element(By.ID,"tickets_" + event_id))
        ticketSelect.select_by_value(str(numTickets))
        #Click Enter Button
        enterButton = showDiv.find_element(By.LINK_TEXT,"ENTER")
        self.driver.execute_script("arguments[0].scrollIntoView();",enterButton)
        self.driver.execute_script("window.scrollBy(0,-100)", "")
        ActionChains(self.driver).move_to_element(enterButton).click().perform()
        #If Debug, print entered
        if(self.config['DEBUG']):
            print("Entered " + showTitle)

        
        






