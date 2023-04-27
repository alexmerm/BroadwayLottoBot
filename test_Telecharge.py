import unittest
from Telecharge import Telecharge
import json
from urllib.parse import parse_qs
from unittest.mock import patch,Mock



CONFIG_PATH = "config_offline.json"
class TelechargeTestCase(unittest.TestCase):
    def setUp(self):
        self.tc = Telecharge(config_path = CONFIG_PATH)
    def tearDown(self) -> None:
        if(self.tc.driver != None):
            self.tc.driver.quit()
    
    #Test Loading config from file
    def test_load_config(self):
        config = {
            "DEBUG": True,
            "SELENIUM_URL": "http://localhost:4444/wd/hub",
            "DEBUG_OFFLINE": True,
            "FACEBOOK_EMAIL": "email@gmail.com",
            "OFFLINE_URL": "file:///mnt/offlinePages/Become a User The Shubert Organization, Inc - LotteryPage.html",
            "FACEBOOK_PASSWORD": "password",
            "NUM_TICKETS_FOR_NEW_SHOWS": 0
        }
        self.assertEqual(self.tc.config, config)

    
    def test_numShows(self):
        titles = self.tc.getShowTitles()
        self.assertEqual(len(titles), 13) #bc 2 tytanique
        self.assertEqual(len(self.tc.shows), 14)

    #Assert DriverIsAlive fails before initiation
    def test_driverIsAlive(self):
        self.assertEqual(self.tc.driverIsAlive(), False)
    

    #Verify that if driver dies, it is restarted and run again, and old divs are removed
    def test_resilience(self):
        self.tc.setup()
        self.tc.driver.quit()
        self.assertEqual(self.tc.driverIsAlive(), False)
        self.assertEqual(len(self.tc.getShowTitles()), 13)
        for show in self.tc.shows:
            # print(show)
            self.assertEqual(show.isAlive(), True)

    #Test Enter Lottery of show already entered
    def test_enterLottery_alreadyEntered(self):
        ARAPP = "ANTHONY RAPP'S WITHOUT YOU"
        show = self.tc.getShow(ARAPP)
        self.assertFalse(show.enterLottery(2))

    #Test Enter Lottery of show already entered
    def test_enterLottery_successful(self):
        BADCIN = "ANDREW LLOYD WEBBER'S BAD CINDERELLA"
        show = self.tc.getShow(BADCIN)
        #Before doing entry, request log so next log request will only have this request
        log_entries = self.tc.driver.get_log("performance")
        self.assertTrue(show.enterLottery(2))
        logentries = self.tc.driver.get_log('performance')
        postData = None
        for line in logentries:
            event = json.loads(line['message'])['message']
            if(event['method'] == 'Network.requestWillBeSent'):
                postData = event['params']['request']['postData']
        self.assertIsNotNone(postData)
        args = parse_qs(postData)
        self.assertEqual(args['event_id'][0], show.event_id)
        self.assertEqual(args['tickets'][0],'2')


    #Verify calls entry on each show
    def test_enter_lotteries_calls(self):
        toGet = {"ANDREW LLOYD WEBBER'S BAD CINDERELLA" :2,
            "BOB FOSSE'S DANCIN'" : 1,
            'KIMBERLY AKIMBO' : 2,
            'PETER PAN GOES WRONG' :2
            }
        BADCIN = Mock(name = "ANDREW LLOYD WEBBER'S BAD CINDERELLA")
        BADCIN.title = "ANDREW LLOYD WEBBER'S BAD CINDERELLA"
        BADCIN.enterLottery.return_value = True
        KIMBERLY = Mock(name = 'KIMBERLY AKIMBO')
        KIMBERLY.title = 'KIMBERLY AKIMBO'
        KIMBERLY.enterLottery.return_value = True
        self.tc.setup()
        self.tc.shows = [BADCIN, KIMBERLY]
        self.tc.enterLotteries(toGet)
        BADCIN.enterLottery.assert_called_with(2)
        KIMBERLY.enterLottery.assert_called_with(2)
    

    #Helper Method to verify all of the lotteries have been entered
    def verify_lotteries_entered(self, toGet, log_entries):
        lottery_entry_requests = []
        for line in log_entries:
            event = json.loads(line['message'])['message']
            if '/st/lottery_enter/' in line['message'] and event['method'] == 'Network.requestWillBeSent':
                #This is a lottery entry request
                lottery_entry_requests.append(event)
        #TODO: verify len is equal to num of >= shows
        ticketsRequests = {} #Dict str:int (event_id: num_tickets)
        for event in lottery_entry_requests:
            postData = event['params']['request']['postData']
            args = parse_qs(postData)
            event_id = args['event_id'][0]
            tickets = int(args['tickets'][0])
            ticketsRequests[event_id] = tickets
        failedShows = []
        for show in toGet:
            #If no tickets requested, then show was not requested
            if(toGet[show] == 0):
                continue
            showObj = self.tc.getShow(show)
            if(showObj == None):
                continue
            if(showObj.already_entered):
                continue
            event_id = showObj.event_id
            #self.assertTrue(event_id in ticketsRequests, msg="testing + {}".format(showObj.title) )
            #self.assertTrue(ticketsRequests[event_id] == toGet[show])
            if(not event_id in ticketsRequests):
                failedShows.append(showObj.title)
        self.assertTrue(len(failedShows) == 0, msg="Failed to enter lotteries for {}".format(failedShows))
            

    def test_enter_lotteries_Kimb(self):
        toGet = {
            "KIMBERLY AKIMBO": 2
            }
            
        self.tc.setup()
        #Before doing entry, request log so next log request will only have this request
        log_entries = self.tc.driver.get_log("performance")
        self.tc.enterLotteries(toGet)
        log_entries = self.tc.driver.get_log("performance")
        self.verify_lotteries_entered(toGet, log_entries)
        
    #Test EnterLotteries() enters all shows its supposed to
    def test_enter_lotteries_stress(self):
        toGet = {
            "ANTHONY RAPP'S WITHOUT YOU": 2,
            "ANDREW LLOYD WEBBER'S BAD CINDERELLA": 2,
            "BOB FOSSE'S DANCIN'": 2,
            "KIMBERLY AKIMBO": 2,
            "PETER PAN GOES WRONG": 2,
            "PARADE": 2,
            "SOME LIKE IT HOT": 2,
            "LEOPOLDSTADT": 2,
            "LIFE OF PI": 2,
            "A BEAUTIFUL NOISE: THE NEIL DIAMOND MUSICAL": 2,
            "THE PLAY THAT GOES WRONG": 2,
            "THE VERY HUNGRY CATERPILLAR SHOW": 2,
            "TITANIQUE": 2,
            "GOOD NIGHT, OSCAR": 2,
            "CAMELOT": 2,
            "LITTLE SHOP OF HORRORS": 2,
            "PRIMA FACIE": 2
            }
            
        self.tc.setup()
        #Before doing entry, request log so next log request will only have this request
        log_entries = self.tc.driver.get_log("performance")
        self.tc.enterLotteries(toGet)
        log_entries = self.tc.driver.get_log("performance")
        self.verify_lotteries_entered(toGet, log_entries)

    #Test EnterLotteries() enters all shows its supposed to on Lottery2 Page
    def test_lottery_stress_2(self):
        self.tc.config['OFFLINE_URL'] = "file:///mnt/offlinePages/Become a User The Shubert Organization, Inc- Lottery2.html"
        toGet = {
            "ANTHONY RAPP'S WITHOUT YOU": 2,
            "ANDREW LLOYD WEBBER'S BAD CINDERELLA": 2,
            "BOB FOSSE'S DANCIN'": 2,
            "KIMBERLY AKIMBO": 2,
            "PETER PAN GOES WRONG": 2,
            "PARADE": 2,
            "SOME LIKE IT HOT": 2,
            "LEOPOLDSTADT": 2,
            "LIFE OF PI": 2,
            "A BEAUTIFUL NOISE: THE NEIL DIAMOND MUSICAL": 0,
            "THE PLAY THAT GOES WRONG": 2,
            "THE VERY HUNGRY CATERPILLAR SHOW": 2,
            "TITANIQUE": 2,
            "GOOD NIGHT, OSCAR": 2,
            "CAMELOT": 2,
            "LITTLE SHOP OF HORRORS": 2,
            "PRIMA FACIE": 2,
            "THE SIGN IN SIDNEY BRUSTEIN'S WINDOW": 2
            }
        self.tc.setup()
        #Before doing entry, request log so next log request will only have this request
        log_entries = self.tc.driver.get_log("performance")
        self.tc.enterLotteries(toGet)
        log_entries = self.tc.driver.get_log("performance")
        self.verify_lotteries_entered(toGet, log_entries)
    
    def test_lottery_stress_3(self):
        self.tc.config['OFFLINE_URL'] = "file:///mnt/offlinePages/Become a User The Shubert Organization, Inc - Lottery3.html"
        toGet = {
            "ANTHONY RAPP'S WITHOUT YOU": 2,
            "ANDREW LLOYD WEBBER'S BAD CINDERELLA": 2,
            "BOB FOSSE'S DANCIN'": 2,
            "KIMBERLY AKIMBO": 2,
            "PETER PAN GOES WRONG": 2,
            "PARADE": 2,
            "SOME LIKE IT HOT": 2,
            "LEOPOLDSTADT": 2,
            "LIFE OF PI": 2,
            "A BEAUTIFUL NOISE: THE NEIL DIAMOND MUSICAL": 0,
            "THE PLAY THAT GOES WRONG": 2,
            "THE VERY HUNGRY CATERPILLAR SHOW": 2,
            "TITANIQUE": 2,
            "GOOD NIGHT, OSCAR": 2,
            "CAMELOT": 2,
            "LITTLE SHOP OF HORRORS": 2,
            "PRIMA FACIE": 2,
            "THE SIGN IN SIDNEY BRUSTEIN'S WINDOW": 2
            }
        self.tc.setup()
        #Before doing entry, request log so next log request will only have this request
        log_entries = self.tc.driver.get_log("performance")
        self.tc.enterLotteries(toGet)
        log_entries = self.tc.driver.get_log("performance")
        self.verify_lotteries_entered(toGet, log_entries)




     







    

#TODO: what is behavior if show is not present in shows(?) aka lottery not running today


if __name__ == '__main__':
    unittest.main()