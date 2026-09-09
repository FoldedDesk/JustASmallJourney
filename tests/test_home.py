import test_journey_moments
import importlib
import unittest


class HomeTests(unittest.TestCase):
    setUp = test_journey_moments.JourneyMomentTests.setUp
    tearDown = test_journey_moments.JourneyMomentTests.tearDown
    def test_display_persistence_memory_and_validation(self):
        self.client.post('/api/travel', json={'food':'rice_ball'})
        with self.game.database() as con:
            con.execute('UPDATE trips SET ends_at=1')
        state = self.client.get('/api/state').json()
        card = state['postcards'][0]
        key = card['rewards'][0]['key']
        inventory = state['inventory']
        route = '/api/home/display/'
        self.assertEqual(self.client.post(route+'1',json={'item':'rice_ball'}).status_code,422)
        self.assertEqual(self.client.post(route+'4',json={'item':key}).status_code,422)
        self.assertEqual(self.client.post(route+'1',json={'item':key}).status_code,200)
        importlib.reload(self.game)
        state = self.client.get('/api/state').json()
        self.assertEqual(state['displays'][0]['memory']['card_id'],card['id'])
        self.assertEqual(state['inventory'],inventory)
        self.client.post(route+'2',json={'item':key})
        self.assertEqual([d['slot'] for d in self.client.get('/api/state').json()['displays']],[2])
        self.client.post('/api/logout')
        self.assertEqual(self.client.post(route+'1',json={'item':key}).status_code,401)
        self.client.post('/api/register',json={'username':'friend','password':'friend-test-123'})
        self.client.post('/api/animal',json={'kind':'cat','name':'小猫'})
        self.assertEqual(self.client.get('/api/state').json()['displays'],[])
        self.assertEqual(self.client.post(route+'1',json={'item':key}).status_code,409)
        self.client.post('/api/logout')
        self.client.post('/api/login',json={'username':'owner','password':'moment-test-123'})
        count = next(i['quantity'] for i in inventory['souvenirs'] if i['key']==key)
        for _ in range(count):
            self.assertEqual(self.client.post('/api/gifts',json={'to_username':'friend','item':key}).status_code,201)
        self.assertEqual(self.client.get('/api/state').json()['displays'],[])
        self.client.post('/api/logout')
        self.client.post('/api/login',json={'username':'friend','password':'friend-test-123'})
        self.client.post(route+'1',json={'item':key})
        display = self.client.get('/api/state').json()['displays'][0]
        self.assertIn('owner',display['memory']['text'])
        self.assertIsNone(display['memory']['card_id'])
        self.client.post(route+'1',json={'item':None})
        self.assertEqual(self.client.get('/api/state').json()['displays'],[])
