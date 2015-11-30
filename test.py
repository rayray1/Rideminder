"""To Unit test then Integration Test my Transit Alert Application"""
import unittest
from unittest import TestCase
import doctest
from process_data import convert_to_e164, gets_a_list_of_available_line, selects_closest_vehicle, gets_a_dic_of_vehicle, validates_bound_direction_of_vehicles_in_line, gets_geolocation_of_a_vehicle, sorts_vehicles_dic_by_distance, selects_closest_vehicle, processes_line_and_bound_selects_closest_vehicle
from firebase import firebase
import process_data
import tasks
from tasks import process_transit_request
from server import app
import server
from model import Transit_Request
import model
from flask_sqlalchemy import SQLAlchemy
from twilio_process import send_text_message
from nose.tools import eq_ #to test Celery

# to test:
# python test.py
# coverage:
# coverage run --omit=env/* test.py
# coverage run --source=. test.py
# for report:
# coverage report -m

mock_db = SQLAlchemy()

#######################################################
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

	def test_send_text_message(self):
		self.assertEqual(send_text_message(+12025550141), None)

########################################################
class UnitTestTransitData(unittest.TestCase):
	def test_gets_a_list_of_available_line(self):
		self.assertTrue(gets_a_list_of_available_line() > 64)
		print "complete gets a list of aviable lines test "

	def test_selects_closest_vehicle(self):
		print "testing the selects_closest_vehicle"
		self.assertEqual(selects_closest_vehicle([(0.9338186621320413, u'1472'), (0.9338186621320413, u'1488'), (1.0398499771587593, u'1455'), (1.0498968948022667, u'1548'), (1.0620705886593063, u'1542'), (1.0644210057899908, u'1528'), (1.0687742887784755, u'1431'), (2.8519879512450164, u'1495'), (4.1161739909827215, u'1535'), (4.820269824445265, u'1459'), (4.890819705827765, u'1442'), (4.893685411614527, u'1519'), (6.297064411922732, u'1476')], [(1.031659187344977, u'1455'), (1.0580960246268907, u'1548'), (1.0626269823073644, u'1528'), (1.0687742887784755, u'1431'), (1.074272454517364, u'1542'), (1.1370610262790521, u'1472'), (1.1370610262790521, u'1488'), (2.739059251454709, u'1495'), (4.219898289028735, u'1535'), (4.819294276261407, u'1459'), (4.890819705827765, u'1442'), (4.893685411614527, u'1519'), (6.303176742628762, u'1476')]), '1472')

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
		self.assertEqual(gets_geolocation_of_a_vehicle(1402),(37.7213, -122.46912))

	def test_sorts_vehicles_dic_by_distance(self):
		dic = gets_a_dic_of_vehicle("N")
		bound_dic = validates_bound_direction_of_vehicles_in_line(dic, "O")
		results = [(0.9313235948899348, u'1426'), (4.275886490639952, u'1415'), (4.7115931592023585, u'1410'), (5.526469350242915, u'1402'), (5.59359790362578, u'1413')]
		self.assertEqual(sorts_vehicles_dic_by_distance(bound_dic, 37.7846810, -122.4073680), results)

	def test_selects_closest_vehicle(self): 
		vehicle_list1 = [(0.12315312469250524, u'1426'), (0.12315312469250524, u'1438'), (0.4675029273179666, u'1520'), (0.4675029273179666, u'1539'), (0.4926871038219716, u'1484')]
		vehicle_list2 = [(0.016675650192621124, u'1426'), (0.048622709177496184, u'1438'), (0.3983583482037339, u'1484'), (0.5805606158286056, u'1539'), (0.6169215360786691, u'1520')]
		self.assertEqual(selects_closest_vehicle(vehicle_list1, vehicle_list2), "1426")

	def test_processes_line_and_bound_selects_closest_vehicle(self):
		user_lat= 37.7846810
		user_lon = -122.4073680
		destination_lat = 37.7846810
		destination_lon = -122.4073680
		bound = "O"
		line = "N"
		results = "1426"
		self.assertEqual(processes_line_and_bound_selects_closest_vehicle(line, bound, destination_lat, destination_lon, user_lat, user_lon), results)

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




class IntergrationServerTest(unittest.TestCase):
	"""Integration Test: testing flask sever"""

	def setUp(self):
		print "(setUp ran)"
		self.client = server.app.test_client()

	def test_homepage(self):
		result = self.client.get("/")
		self.assertEqual(result.status_code, 200)

	def test_user_input_form(self):
		print "testing user_input page"
		test_client = server.app.test_client()

		result = test_client.post('/user_input', data={'fname': 'Jessica', "phone":"13604508678", "line":"N", "bound":"O", "destination":"37.76207,-122.4693199"})
		self.assertIn('<!doctype html>\n<html>\n    <head>\n      <title>Rideminder</title>\n      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">\n      <meta name="viewport" content="width=device-width, initial-scale=1">\n      <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css" rel="stylesheet">\n    <link rel="stylesheet" type="text/css" href="/static/css/styling.css">\n    \n \n\n    </head>\n\n<body>\n    <div class="container-fluid">\n        <p class="navbar-brand">Rideminder</p>\n      </div>\n    </div><!-- /.container-fluid -->\n\n\n\n  <hr>\n\n  \n\n<div class="row">\n\t<div clase="row">\n  \t\t<div class="container thankyou">\n  \t\t\t<p class="center"> Thank you Jessica! </p>\n  \t\t\t<p class="center"> We will text you at +13604508678 when you are within 3 blocks of your destination. </p>\n  \t\t\t<p class="center"> Have a wonderful day! </p>\n\t\t</div>\n \t</div>\n</div>\n\n<div class="row">\n  <div class="col-md-6 col-md-offset-3 center img"><img src="static/sleepingdog.jpg" alt="Picture of a baby sleeping"> <p class="center">Enjoy your nap </p></div>\n</div>\n\n\n\n\n</body>\n</html>', result.data)




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



