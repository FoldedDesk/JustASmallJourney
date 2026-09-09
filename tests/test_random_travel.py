import importlib
import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from content import destination_weights, FOOD_DESTINATIONS, TOOL_DESTINATIONS


class RandomTravelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ['JOURNEY_DB'] = self.temp.name + '/random.sqlite3'
        import app
        self.game = importlib.reload(app)
        self.client = TestClient(self.game.app)
        self.client.post('/api/register', json={'username':'owner','password':'random-test-123'})
        self.client.post('/api/animal', json={'kind':'frog','name':'小满'})

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()
        os.environ.pop('JOURNEY_DB', None)

    def test_equipment_bias_keeps_all_destinations_possible(self):
        self.assertEqual(set(FOOD_DESTINATIONS), set(self.game.FOODS))
        self.assertEqual(set(TOOL_DESTINATIONS), set(self.game.TOOLS))
        self.assertEqual(set(destination_weights('rice_ball', None).values()), {10})
        for food in self.game.FOODS:
            for tool in [None, *self.game.TOOLS]:
                weights = destination_weights(food, tool)
                self.assertEqual(set(weights), set(self.game.PLACES))
                self.assertTrue(all(w > 0 for w in weights.values()))
                for place in FOOD_DESTINATIONS[food]:
                    self.assertGreater(weights[place], weights[next(p for p in weights if p not in FOOD_DESTINATIONS[food])])
        weights = destination_weights('lemon_soda', 'camera')
        self.assertAlmostEqual(weights['sea']/sum(weights.values()), 210/900)
        self.assertAlmostEqual(weights['desert']/sum(weights.values()), 160/900)

    def test_client_cannot_choose_and_route_is_drawn_only_once(self):
        before = self.client.get('/api/state').json()['inventory']['foods']
        self.assertEqual(self.client.post('/api/travel', json={'place':'sea','food':'rice_ball'}).status_code, 422)
        self.assertEqual(self.client.post('/api/travel', json={'food':'rice_ball','charm':'lucky'}).status_code, 422)
        self.assertEqual(self.client.get('/api/state').json()['inventory']['foods'], before)
        with patch('random.choices', return_value=['snow']) as draw:
            self.assertEqual(self.client.post('/api/travel', json={'food':'rice_ball','tool':'camera'}).status_code, 201)
            self.assertEqual(self.client.post('/api/travel', json={'food':'rice_ball'}).status_code, 409)
            state = self.client.get('/api/state').json()
            self.assertNotIn('place', state['travel'])
            self.assertNotIn('combination', state['travel'])
            draw.assert_called_once()
        importlib.reload(self.game)
        self.assertNotIn('place', self.client.get('/api/state').json()['travel'])
        with self.game.database() as con:
            self.assertEqual(con.execute('SELECT place FROM trips').fetchone()['place'], 'snow')
            con.execute('UPDATE trips SET ends_at=1')
        self.assertEqual(self.client.get('/api/state').json()['postcards'][0]['place'], 'snow')

    def test_encounter_and_friends_do_not_reveal_destination_early(self):
        with TestClient(self.game.app) as friend:
            friend.post('/api/register', json={'username':'friend','password':'random-test-456'})
            friend.post('/api/animal', json={'kind':'cat','name':'团团'})
            with patch.object(self.game, 'choose_destination', return_value='sea'):
                self.client.post('/api/travel', json={'food':'rice_ball'})
                friend.post('/api/travel', json={'food':'rice_ball'})
            state = friend.get('/api/state').json()
            self.assertTrue(state['friends'][0]['traveling'])
            self.assertNotIn('place', state['friends'][0])
            self.assertEqual(len(state['events']), 2)
            self.assertTrue(all('海岸' not in e['message'] and '相遇' not in e['message'] for e in state['events']))
            with self.game.database() as con:
                con.execute('UPDATE trips SET ends_at=1 WHERE pet_id=1')
            self.assertEqual(len(friend.get('/api/state').json()['events']), 2)
            self.assertEqual(friend.get('/api/state').json()['postcards'], [])
            with self.game.database() as con:
                con.execute('UPDATE trips SET ends_at=1')
            state = friend.get('/api/state').json()
            self.assertEqual(len(state['events']), 3)
            self.assertIn('日落海岸', state['events'][0]['message'])
            self.assertEqual(len(state['postcards']), 2)

    def test_upgrade_hides_existing_departure_and_pending_encounter_events(self):
        with TestClient(self.game.app) as friend:
            friend.post('/api/register', json={'username':'oldfriend','password':'random-test-789'})
            friend.post('/api/animal', json={'kind':'cat','name':'旧朋友'})
            with patch.object(self.game, 'choose_destination', return_value='sea'):
                self.client.post('/api/travel', json={'food':'rice_ball'})
                friend.post('/api/travel', json={'food':'rice_ball'})
        with self.game.database() as con:
            con.execute("DELETE FROM settings WHERE key='hidden_routes_v1'")
            con.execute('UPDATE events SET encounter_id=NULL')
            con.execute("UPDATE events SET message='owner的小满去了日落海岸。' WHERE id=1")
        importlib.reload(self.game)
        state = self.client.get('/api/state').json()
        self.assertEqual(len(state['events']), 2)
        self.assertTrue(all('海岸' not in e['message'] for e in state['events']))
        with self.game.database() as con:
            con.execute('UPDATE trips SET ends_at=1')
        self.assertEqual(len(self.client.get('/api/state').json()['events']), 3)
