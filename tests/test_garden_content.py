import importlib
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi.testclient import TestClient
from travel_helpers import travel


class GardenContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ['JOURNEY_DB'] = self.temp.name + '/garden.sqlite3'
        import app
        self.game = importlib.reload(app)
        self.route_patch = patch.object(self.game, 'choose_destination', return_value='forest')
        self.route_patch.start()
        self.addCleanup(self.route_patch.stop)
        self.client = TestClient(self.game.app)
        self.client.post('/api/register', json={'username': 'gardener', 'password': 'garden-test-123'})
        self.client.post('/api/animal', json={'kind': 'rabbit', 'name': '团团'})

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()
        os.environ.pop('JOURNEY_DB', None)

    def state(self):
        return self.client.get('/api/state').json()

    def quantity(self, state, key):
        return next(i['quantity'] for category in ('foods', 'souvenirs') for i in state['inventory'][category] if i['key'] == key)

    def parallel(self, path, bodies):
        def send(body):
            with TestClient(self.game.app) as client:
                client.cookies.update(self.client.cookies)
                return client.post(path, json=body).status_code
        with ThreadPoolExecutor(max_workers=4) as pool:
            return sorted(pool.map(send, bodies))

    def test_garden_offline_growth_single_harvest_and_restart(self):
        state = self.state()
        self.assertEqual(state['garden']['clovers'], 12)
        self.assertEqual(len(state['garden']['plots']), 3)
        self.assertEqual(self.parallel('/api/garden/1/plant', [{}, {}, {}, {}]), [200, 409, 409, 409])
        self.assertEqual(self.client.post('/api/garden/1/harvest').status_code, 409)
        with self.game.database() as con:
            con.execute('UPDATE garden_plots SET ready_at=1 WHERE plot=1')
        importlib.reload(self.game)
        self.assertEqual(self.state()['garden']['plots'][0]['status'], 'ready')
        self.assertEqual(self.parallel('/api/garden/1/harvest', [{}, {}, {}, {}]), [200, 409, 409, 409])
        self.assertEqual(self.state()['garden']['clovers'], 18)
        self.assertEqual(self.state()['garden']['plots'][0]['status'], 'empty')
        self.assertEqual(self.client.post('/api/garden/1/plant').status_code, 200)
        self.assertEqual(self.state()['garden']['plots'][0]['cycle'], 2)
        importlib.reload(self.game)
        self.assertEqual(self.state()['garden']['clovers'], 18)

    def test_shop_retry_and_atomic_spending(self):
        order = {'item': 'berry_pie', 'request_id': 'one-shop-order-0001'}
        self.assertEqual(self.parallel('/api/shop/buy', [order] * 4), [200] * 4)
        self.assertEqual(self.state()['garden']['clovers'], 6)
        self.assertEqual(self.quantity(self.state(), 'berry_pie'), 1)
        self.assertEqual(self.client.post('/api/shop/buy', json={**order, 'item': 'cocoa'}).status_code, 409)
        self.assertEqual(self.parallel('/api/shop/buy', [{'item': 'berry_pie', 'request_id': 'separate-order-00'+str(i)} for i in range(4)]), [200, 409, 409, 409])
        state = self.state()
        self.assertEqual(state['garden']['clovers'], 0)
        self.assertEqual(self.quantity(state, 'berry_pie'), 2)
        self.assertEqual(self.client.post('/api/shop/buy', json={'item': 'pinecone', 'request_id': 'invalid-product-000'}).status_code, 422)
        importlib.reload(self.game)
        self.assertEqual(self.client.post('/api/shop/buy', json=order).status_code, 200)
        self.assertEqual(self.quantity(self.state(), 'berry_pie'), 2)
        self.assertEqual(self.state()['garden']['clovers'], 0)

    def test_garden_auth_pet_requirement_and_isolation(self):
        with TestClient(self.game.app) as friend:
            self.assertEqual(friend.post('/api/garden/1/plant').status_code, 401)
            self.assertEqual(friend.post('/api/shop/buy', json={'item': 'cocoa', 'request_id': 'anonymous-order-001'}).status_code, 401)
            friend.post('/api/register', json={'username': 'friend', 'password': 'garden-test-456'})
            self.assertEqual(friend.post('/api/garden/1/plant').status_code, 409)
            self.assertEqual(friend.post('/api/shop/buy', json={'item': 'cocoa', 'request_id': 'no-pet-order-0001'}).status_code, 409)
            friend.post('/api/animal', json={'kind': 'cat', 'name': '小花'})
            self.client.post('/api/garden/1/plant')
            self.assertEqual(friend.post('/api/garden/1/harvest').status_code, 409)
            self.assertEqual(friend.get('/api/state').json()['garden']['clovers'], 12)
        self.assertEqual(self.client.post('/api/garden/4/plant').status_code, 422)
        self.assertEqual(self.client.post('/api/garden/0/harvest').status_code, 422)

    def test_all_combinations_deliver_distinct_collectible_cards_once(self):
        catalog = self.state()['catalog']
        self.assertEqual(len(catalog['places']), 50)
        self.assertEqual(len(self.game.FOODS), 60)
        self.assertEqual(len(self.game.SOUVENIRS), 100)
        self.assertNotIn('combinations', catalog)
        self.assertEqual(len(self.game.COMBINATIONS), 50)
        for recipe in self.game.COMBINATIONS:
            with self.subTest(recipe=recipe['key']):
                before = self.quantity(self.state(), recipe['reward'])
                with self.game.database() as con:
                    self.game.grant_item(con, 1, recipe['food'], 1, 'test', recipe['key'])
                    if recipe['tool']:
                        self.game.grant_item(con, 1, recipe['tool'], 1, 'test', recipe['key'])
                response = travel(self.client, {'place': recipe['place'], 'food': recipe['food'], 'tool': recipe['tool']})
                self.assertEqual(response.status_code, 201)
                self.assertNotIn('combination', self.state()['travel'])
                with self.game.database() as con:
                    con.execute('UPDATE trips SET ends_at=started_at-1 WHERE settled=0')
                with patch.object(self.game.random, 'random', return_value=.99):
                    state = self.state()
                card = state['postcards'][0]
                self.assertEqual(card['template_key'], 'combo:' + recipe['key'])
                self.assertEqual(card['title'], recipe['title'])
                self.assertEqual(card['variant'], 'combination')
                self.assertEqual({r['key'] for r in card['rewards']}, {self.game.PLACES[recipe['place']]['gift_key'], recipe['reward']})
                self.assertEqual(self.quantity(self.state(), recipe['reward']), before+1)
        importlib.reload(self.game)
        self.assertEqual(len(self.state()['postcards']), 50)
        self.assertEqual(len({c['template_key'] for c in self.state()['postcards']}), 50)

    def test_special_recipe_requires_tool_and_snapshot_survives_restart(self):
        self.assertIsNone(self.game.match_combination('sea', 'lemon_soda', 'map'))
        self.assertIsNone(self.game.match_combination('forest', 'lemon_soda', 'camera'))
        self.client.post('/api/shop/buy', json={'item': 'lemon_soda', 'request_id': 'soda-for-recipe-0001'})
        travel(self.client, {'place': 'sea', 'food': 'lemon_soda', 'tool': 'camera'})
        self.assertNotIn('combination', self.state()['travel'])
        with self.game.database() as con:
            snapshot = con.execute('SELECT combination FROM trips').fetchone()['combination']
            con.execute('UPDATE trips SET ends_at=1')
        importlib.reload(self.game)
        with patch.object(self.game, 'match_combination', return_value=None):
            card = self.state()['postcards'][0]
        self.assertNotIn('combination', card)
        with self.game.database() as con:
            self.assertEqual(con.execute('SELECT combination FROM cards').fetchone()['combination'], snapshot)
        self.assertEqual(self.quantity(self.state(), 'bubble_photo'), 1)

    def test_all_foods_can_be_replenished_in_shop(self):
        with self.game.database() as con:
            con.execute('UPDATE gardens SET clovers=1000')
        for key, food in self.game.FOODS.items():
            before = self.state()
            self.assertEqual(self.client.post('/api/shop/buy', json={'item': key, 'request_id': 'catalog-order-'+key.replace('_', '-')}).status_code, 200)
            after = self.state()
            self.assertEqual(after['garden']['clovers'], before['garden']['clovers'] - food['price'])
            self.assertEqual(self.quantity(after, key), self.quantity(before, key) + 1)

    def test_state_does_not_publish_undiscovered_recipes_or_story_catalog(self):
        state = self.state()
        self.assertEqual(set(state['catalog']), {'places'})
        for place in state['catalog']['places'].values():
            self.assertEqual(set(place), {'name', 'icon', 'tag', 'description'})
        with TestClient(self.game.app) as visitor:
            self.assertEqual(visitor.get('/api/state').json()['catalog'], state['catalog'])


if __name__ == '__main__':
    unittest.main()
