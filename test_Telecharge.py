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
        self.tc.getShowDivs()
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
        self.assertTrue(show.enterLottery(2))
        self.tc.driver.implicitly_wait(2)
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

    # @patch.object(Telecharge,'driverIsAlive', return_value = True)
    def test_enter_lotteries(self):
        toGet = {"ANDREW LLOYD WEBBER'S BAD CINDERELLA" :2,
            "BOB FOSSE'S DANCIN'" : 1,
            'KIMBERLY AKIMBO' : 2,
            'PETER PAN GOES WRONG' :2
            }
        BADCIN = Mock(name = "ANDREW LLOYD WEBBER'S BAD CINDERELLA")
        BADCIN.title = "ANDREW LLOYD WEBBER'S BAD CINDERELLA"
        BADCIN.enterLottery.return_value = True
        self.tc.setup()
        self.tc.shows = [BADCIN]
        self.tc.enterLotteries(toGet)
        BADCIN.enterLottery.assert_called_with(2)

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
     







    

#TODO: what is behavior if show is not present in shows(?) aka lottery not running today


if __name__ == '__main__':
    unittest.main()