from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import re
from selenium import webdriver


class TelechargeShow:

    def __init__(self,driver:webdriver.Remote,  showDiv :WebElement, config: dict[str:str] = {'DEBUG' : False} ) -> None:

        self.div = showDiv
        self.config = config
        self.driver = driver
        self.refreshInfo()
    
    def refreshInfo(self):
        """Loads all info from div into object"""
        self.title = self.div.find_element(By.CLASS_NAME,"lottery_show_title").text
        self.dateTime = self.div.find_element(By.CLASS_NAME,"lottery_show_date").text
        self.price = self.div.find_element(By.CLASS_NAME,"lottery_show_price_discount").text
        self.maxTickets = 2 #Always 2 for Telecharge
        entered_text = self.div.find_element(By.CLASS_NAME,"entered-text")
        self.already_entered = entered_text.is_displayed()
        #Get Event ID
        onclick = self.div.get_attribute("onclick")
        self.event_id = re.search(r'\d+', onclick).group()

    def isAlive(self):
        """Returns true if connection to showDiv is Alive"""
        try:
            self.div.text
            return True
        except:
            return False
    
    def __str__(self) -> str:
        return ("Title: " + self.title + " Date: " + self.dateTime + " Price: " + self.price + " Max Tickets: " + str(self.maxTickets) + " Already Entered: " + str(self.already_entered) + " Event ID: " + self.event_id + " Alive: " + str(self.isAlive()))
    @staticmethod
    def createShowsFromDivs(driver: webdriver.Remote, showDivs : list[WebElement], config:dict[str:str] = {'DEBUG' : False}) -> list['TelechargeShow']:
        """Returns a list of TelechargeShows from a list of showDivs"""
        shows = []
        for div in showDivs:
            title = div.find_element(By.CLASS_NAME,"lottery_show_title").text
            if(title != ''):
                shows.append(TelechargeShow(driver, div, config))
        return shows
    


    #Assuming alive 
    def enterLottery(self, numTickets: int) -> bool:
        ##TODO : Check if already entered, and if alive
        """Enters the lottery for this show with the given number of tickets, returns true if successul, false otherwise"""
        if numTickets == 0:
            return False

        if(self.config['DEBUG']):
            print("Entering " + self.title)
        
        if (self.already_entered):
            if(self.config['DEBUG']):
                print("already entered for " + self.title)
            return False
        
        #Get Event ID
        #Select No of Tickets
        if(self.config['DEBUG']):
            print("numTickets: " + str(numTickets))
        ticketSelect= Select(self.div.find_element(By.ID,"tickets_" + self.event_id))
        ticketSelect.select_by_value(str(numTickets))
        #Click Enter Button
        enterButton = self.div.find_element(By.LINK_TEXT,"ENTER")
        self.driver.execute_script("arguments[0].scrollIntoView();",enterButton)
        self.driver.execute_script("window.scrollBy(0,-300)", "")
        #time.sleep(1)
        #print("should be showing {}".format(self.title))
        # self.driver.get_screenshot_as_file("screenshots/{}_{}_{}.png".format(self.title, self.dateTime, self.event_id))

        #Click all dispalyed Notifications to remove them
        self.clickNotifications()
        #Wait until Notifications are gone to click enter button
        WebDriverWait(self.driver, 10).until_not(TelechargeShow.notificationsDisplayed)
        ActionChains(self.driver).move_to_element(enterButton).click().perform()
        #TODO: check if there is something I can do to confirm it went through when not online
        #If Debug, print entered
        if(self.config['DEBUG']):
            print("Entered " + self.title)
        #time.sleep(1)
        return True
    
    #Click Notification to Dissapear it
    def clickNotifications(self):
        notifications = self.driver.find_elements(By.XPATH,"//ul[@id='st-notification-list']/li")
        for notification in notifications:
            if notification.is_displayed():
                ActionChains(self.driver).move_to_element(notification).click().perform()
    
    
    @staticmethod
    def notificationsDisplayed(d):
        """Helper Method to determine that no notification is displayed by the time lottery is entered (potentially covering enter button)
        Takes: Driver, returns true if any notifications displayed"""
        notifications = d.find_elements(By.XPATH,"//ul[@id='st-notification-list']/li")
        for notification in notifications:
            if notification.is_displayed():
                return True
        return False


        