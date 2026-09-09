import importlib
import os
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient


class JourneyMomentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ['JOURNEY_DB'] = self.temp.name + '/moments.sqlite3'
        import app
        self.game = importlib.reload(app)
        self.client = TestClient(self.game.app)
        self.client.post('/api/register', json={'username':'owner','password':'moment-test-123'})
        self.client.post('/api/animal', json={'kind':'frog','name':'小满'})

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()
        os.environ.pop('JOURNEY_DB', None)

    def test_each_length_and_note_stays_hidden_until_its_time(self):
        for label, multiplier in self.game.TRIP_LENGTHS:
            with patch.object(self.game.random, 'choice', side_effect=[(label,multiplier),'我在路上，一切都好。']), patch.object(self.game.random, 'random', return_value=0):
                self.assertEqual(self.client.post('/api/travel',json={'food':'rice_ball'}).status_code,201)
            state = self.client.get('/api/state').json()
            trip = state['travel']
            self.assertEqual(trip['ends_at']-trip['started_at'], self.game.DURATION*multiplier)
            self.assertEqual(trip['duration_label'],label)
            self.assertIsNone(trip['note'])
            self.assertIsNone(state['diary'][0]['note'])
            self.assertIsNone(state['diary'][0]['place'])
            self.assertNotIn('trail_note',trip)
            self.assertEqual(self.client.post('/api/trips/'+str(trip['id'])+'/unpack').status_code,409)
            importlib.reload(self.game)
            with patch.object(self.game.time,'time',return_value=(trip['started_at']+trip['ends_at'])/2):
                state = self.client.get('/api/state').json()
                self.assertEqual(state['travel']['note']['message'],'我在路上，一切都好。')
                self.assertEqual(state['diary'][0]['note'],state['travel']['note'])
            with self.game.database() as con:
                con.execute('UPDATE trips SET ends_at=1 WHERE settled=0')
            self.client.get('/api/state')

    def test_unpacked_state_persists_and_cannot_duplicate_rewards(self):
        self.client.post('/api/travel',json={'food':'rice_ball'})
        with self.game.database() as con:
            con.execute('UPDATE trips SET ends_at=1')
        importlib.reload(self.game)
        state = self.client.get('/api/state').json()
        arrival = state['arrival']
        self.assertIsNotNone(arrival)
        inventory = state['inventory']
        self.assertEqual(arrival['place'],state['postcards'][0]['place'])
        route = '/api/trips/'+str(arrival['id'])+'/unpack'
        for _ in range(3):
            response = self.client.post(route)
            self.assertEqual(response.status_code,200)
            self.assertTrue(all(card['opened'] for card in response.json()['postcards']))
        importlib.reload(self.game)
        state = self.client.get('/api/state').json()
        self.assertIsNone(state['arrival'])
        self.assertEqual(state['inventory'],inventory)
        self.assertEqual(len(state['diary']),1)
        self.assertTrue(state['diary'][0]['unpacked'])
        self.assertEqual(len(state['diary'][0]['cards']),1)

    def test_diary_and_luggage_are_private_and_no_note_is_supported(self):
        with patch.object(self.game.random,'random',return_value=.99):
            self.client.post('/api/travel',json={'food':'rice_ball'})
        trip = self.client.get('/api/state').json()['travel']
        with patch.object(self.game.time,'time',return_value=trip['ends_at']-1):
            self.assertIsNone(self.client.get('/api/state').json()['travel']['note'])
        with TestClient(self.game.app) as other:
            self.assertEqual(other.post('/api/trips/'+str(trip['id'])+'/unpack').status_code,401)
            other.post('/api/register',json={'username':'other','password':'moment-test-456'})
            self.assertEqual(other.get('/api/state').json()['diary'],[])
            self.assertEqual(other.post('/api/trips/'+str(trip['id'])+'/unpack').status_code,404)
            with self.game.database() as con:
                con.execute('UPDATE trips SET ends_at=1')
            self.assertIsNone(other.get('/api/state').json()['arrival'])
            self.assertEqual(other.post('/api/trips/'+str(trip['id'])+'/unpack').status_code,404)
