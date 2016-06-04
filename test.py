"""To Unit test then Integration Test my Transit Alert Application"""
import unittest
from unittest import TestCase
import doctest
from process_data import convert_to_e164, gets_a_list_of_available_line, selects_closest_vehicle, gets_a_dic_of_vehicle, validates_bound_direction_of_vehicles_in_line, gets_geolocation_of_a_vehicle, sorts_vehicles_dic_by_distance, selects_closest_vehicle, process_lat_lng_get_arrival_datetime
from firebase import firebase
import process_data
import tasks
from tasks import process_transit_request
from server import app
import server
from model import Transit_Request
import model
from flask_sqlalchemy import SQLAlchemy
from twilio_process import send_text_message_walk
from nose.tools import eq_ #to test Celery

# to test:
# python test.py
# coverage:
# coverage run --omit=env/* test.py
# coverage run --source=. test.py
# for report:
# coverage report -m

mock_db = SQLAlchemy()

######################################################
def load_tests(loader, tests, ignore):
    """Also run our doctests and file-based doctests."""

    tests.addTests(doctest.DocTestSuite(server))
    tests.addTests(doctest.DocFileSuite("tests.txt"))
    return tests

########################################################
class UnitTestTwillioTestCase(unittest.TestCase):
    def test_convert_to_e164(self):
        self.assertEqual(convert_to_e164("(843)323-2343"), u'+18433232343')
        print "complete phone number convertion test"

    def test_convert_to_e164_empty(self):
        self.assertEqual(convert_to_e164(""), None)
        print "complete phone number convertion test"

    def test_convert_to_e164_plus_sign(self):
        self.assertEqual(convert_to_e164("+18294039493"), u'+18294039493')
        print "complete phone number convertion test"

    def test_send_text_message_walk(self):
        self.assertEqual(send_text_message_walk(+12025550141), None)

########################################################
class UnitTestTransitData(unittest.TestCase):
    def test_gets_a_list_of_available_line(self):
        self.assertTrue(gets_a_list_of_available_line() > 64)
        print "complete gets a list of aviable lines test"

    def test_selects_closest_vehicle(self):
        user_lat = 37.785152
        user_lon = -122.406581
        vehicle_1 = 1426
        vehicle_1_distance = 0.12315312469250524
        vehicle_2 = 1438
        vehicle_2_distance = 0.12315312469250524
        self.assertEqual(selects_closest_vehicle(vehicle_1, vehicle_1_distance, vehicle_2, vehicle_2_distance, user_lat, user_lon), 1438)
        print "complete selects_closest_vehicle"

#######################################################
class UnitTestMockData(unittest.TestCase):
    """Testing wit Mock Data"""
    print"got into mock data class"

    def setUp(self):
        """Creating mock firebase to test aganist"""
        mock_transit_firebase = firebase.FirebaseApplication("https://popping-torch-2216.firebaseio.com/sf-muni", None)

        self._old_transit_firebase = process_data.transit_firebase
        process_data.transit_firebase = mock_transit_firebase

    def tearDown(self):
        """Resets my firebase to its normal one"""
        process_data.transit_firebase = self._old_transit_firebase

    def test_gets_a_dic_of_vehicle(self):
        print "test gets_a_dic_of_vehicle"
        results = {u'1426': u'True', u'1410': u'True', u'1402': u'True', u'1413': u'True', u'1415': u'True', u'1404': u'True'}
        self.assertEqual(gets_a_dic_of_vehicle("N"), results)

    def test_validates_bound_direction_of_vehicles_in_line(self):
        dic = gets_a_dic_of_vehicle("N")
        results = [u'1426', u'1410', u'1402', u'1413', u'1415']
        self.assertEqual(validates_bound_direction_of_vehicles_in_line(dic, "O"), results)

    def test_validates_bound_direction_not_be(self):
        dic = gets_a_dic_of_vehicle("N")
        negative_results = "1404"
        self.assertNotEqual(validates_bound_direction_of_vehicles_in_line(dic, "O"), negative_results)

    def test_gets_geolocation_of_a_vehicle(self):
        self.assertEqual(gets_geolocation_of_a_vehicle(1402), (37.7213, -122.46912))

    def test_sorts_vehicles_dic_by_distance(self):
        dic = gets_a_dic_of_vehicle("N")
        bound_dic = validates_bound_direction_of_vehicles_in_line(dic, "O")
        results = [(0.9313235948899348, u'1426'), (4.275886490639952, u'1415'), (4.7115931592023585, u'1410'), (5.526469350242915, u'1402'), (5.59359790362578, u'1413')]
        self.assertEqual(sorts_vehicles_dic_by_distance(bound_dic, 37.7846810, -122.4073680), results)

    def test_selects_closest_vehicle(self):
        vehicle_1 = 1426
        vehicle_1_distance = 0.12315312469250524
        vehicle_2 = 1438
        vehicle_2_distance = 0.12315312469250524
        user_lat = 37.785152
        user_lon = -122.406581
        self.assertEqual(selects_closest_vehicle(vehicle_1, vehicle_1_distance, vehicle_2, vehicle_2_distance, user_lat, user_lon), "1438")

    def test_selects_closest_vehicle(self):
        user_lat = 37.7846810
        user_lon = -122.4073680
        destination_lat = 37.7846810
        destination_lon = -122.4073680
        bound = "O"
        line = "N"
        results = "1426"
        self.assertEqual(selects_closest_vehicle(line, bound, destination_lat, destination_lon, user_lat, user_lon), line)

########################################################
class UnitTestMockDataForCelery(unittest.TestCase):
    """Testing wit Mock Data"""
    print"got into mock data class for celery"

    def setUp(self):
        """Creating mock firebase to test aganist"""
        mock_transit_firebase = firebase.FirebaseApplication("https://popping-torch-2216.firebaseio.com/sf-muni", None)

        self._old_transit_firebase = tasks.transit_firebase
        tasks.transit_firebase = mock_transit_firebase

        self.old_db = model.db
        model.db = mock_db

    def tearDown(self):
        """Resets my firebase to its normal one"""
        tasks.transit_firebase = self._old_transit_firebase
        model.db = self.old_db

    def test_process_transit_request(self):
        # results = "<@task: tasks.process_transit_request of <Flask 'server'>:0x10497a490 (v2 compatible)>"
        # self.assertTrue(process_transit_request, results)
        rst = task.apply().get()
        eq_(rst, 8)


class UnitTestDateTime(unittest.TestCase):
    """Test Datetime Functionality"""
    print "processing datetime test"

    def test_process_lat_lng_get_arrival_datetime(self):
        result = None
        self.assertEqual(process_lat_lng_get_arrival_datetime(user_lat, user_lon, destination_lat, destination_lon), line)


class IntergrationServerTest(unittest.TestCase):
    """Integration Test: testing flask sever"""

    def setUp(self):
        print "(setUp ran)"
        self.client = server.app.test_client()

    def test_homepage(self):
        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        print "completed homepage test"

    def test_user_input_form(self):
        test_client = server.app.test_client()
        result = test_client.post('/thank-you', data={'fname':'Jessica', 'phone':'13604508678',
                                                        'line':'N', 'bound':'O', 'destination':'37.76207,-122.4693199',
                                                        'lat': '37.785152', 'lan': '-122.406581'})
        import pdb; pdb.set_trace()
        self.assertIn('We will text you at +13604508678 when you are within 3 blocks of your destination', result.data)



def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example_data.db'
    mock_db.app = app
    mock_db.init_app(app)


if __name__ == '__main__':
    unittest.main()
    from server import app
    connect_to_db(app)
    mock_db.create_all()
    print "Connected to DB."
