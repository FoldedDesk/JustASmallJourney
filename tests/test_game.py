import importlib
import os
import sqlite3
import tempfile
from pathlib import Path
import unittest
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi.testclient import TestClient


class GameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ['JOURNEY_DB'] = self.temp.name + '/game.sqlite3'
        import app
        self.game = importlib.reload(app)
        self.client = TestClient(self.game.app)
        self.client.post('/api/register',json={'username':'owner','password':'test-pass-123'})

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()
        os.environ.pop('JOURNEY_DB', None)

    def adopt(self):
        self.assertEqual(self.client.post('/api/animal', json={'kind':'frog','name':'小满'}).status_code,201)

    def finish(self):
        with closing(sqlite3.connect(self.game.DB)) as con:
            with con:
                con.execute('UPDATE trips SET ends_at=started_at-1')

    def item(self, state, category, key):
        return next(item for item in state['inventory'][category] if item['key'] == key)

    def test_validation_and_busy_trip(self):
        self.assertEqual(self.client.post('/api/travel',json={'place':'forest'}).status_code,409)
        for body in [{'kind':'dragon','name':'小满'},{'kind':'frog','name':'   '}]:
            self.assertEqual(self.client.post('/api/animal',json=body).status_code,422)
        self.adopt()
        self.assertEqual(self.client.post('/api/animal',json={'kind':'cat','name':'新名字'}).status_code,409)
        self.assertEqual(self.client.post('/api/travel',json={'place':'unknown'}).status_code,422)
        self.assertEqual(self.client.post('/api/travel',json={'place':'forest'}).status_code,201)
        self.assertEqual(self.client.post('/api/travel',json={'place':'sea'}).status_code,409)
        self.assertEqual(len(self.client.get('/api/state').json()['postcards']),0)

    def test_offline_restart_settles_once_and_keeps_opened_state(self):
        self.adopt()
        self.client.post('/api/travel',json={'place':'sea'})
        self.finish()
        importlib.reload(self.game)
        with TestClient(self.game.app) as client:
            client.cookies.update(self.client.cookies)
            state=client.get('/api/state').json()
            self.assertIsNone(state['travel'])
            self.assertEqual(state['animal']['name'],'小满')
            self.assertEqual(len(state['postcards']),1)
            card=state['postcards'][0]
            self.assertEqual(card['place'],'sea')
            self.assertEqual(card['gift'],'一枚贝壳')
            self.assertFalse(card['opened'])
            self.assertEqual(client.post(f"/api/postcards/{card['id']}/open").status_code,200)
            self.assertEqual(len(client.get('/api/state').json()['postcards']),1)
            self.assertTrue(client.get('/api/state').json()['postcards'][0]['opened'])
            self.assertEqual(client.post('/api/travel',json={'place':'mountain'}).status_code,201)

    def test_backpack_starter_daily_claim_and_food_consumption(self):
        self.adopt()
        state = self.client.get('/api/state').json()
        self.assertEqual(self.item(state, 'foods', 'rice_ball')['quantity'], 3)
        self.assertEqual(self.item(state, 'foods', 'apple')['quantity'], 1)
        self.assertEqual(self.item(state, 'tools', 'camera')['quantity'], 1)
        self.assertEqual(self.item(state, 'tools', 'map')['quantity'], 1)
        self.assertTrue(state['inventory']['daily']['available'])
        self.assertEqual(self.client.post('/api/inventory/daily').status_code, 200)
        self.assertEqual(self.client.post('/api/inventory/daily').status_code, 409)
        state = self.client.get('/api/state').json()
        self.assertEqual(self.item(state, 'foods', 'rice_ball')['quantity'], 4)
        self.assertFalse(state['inventory']['daily']['available'])
        self.assertEqual(self.client.post('/api/travel', json={'place': 'forest', 'food': 'apple', 'tool': 'camera'}).status_code, 201)
        state = self.client.get('/api/state').json()
        self.assertEqual(state['travel']['food']['key'], 'apple')
        self.assertEqual(state['travel']['tool']['key'], 'camera')
        self.assertEqual(self.item(state, 'foods', 'apple')['quantity'], 0)
        self.assertEqual(self.item(state, 'tools', 'camera')['quantity'], 1)
        self.finish()
        state = self.client.get('/api/state').json()
        self.assertEqual(self.item(state, 'souvenirs', 'pinecone')['quantity'], 1)
        self.assertEqual(self.item(self.client.get('/api/state').json(), 'souvenirs', 'pinecone')['quantity'], 1)

    def test_map_can_add_extra_souvenir_once(self):
        self.adopt()
        self.assertEqual(self.client.post('/api/travel', json={'place': 'mountain', 'food': 'rice_ball', 'tool': 'map'}).status_code, 201)
        self.finish()
        with patch.object(self.game.random, 'random', return_value=0.0):
            state = self.client.get('/api/state').json()
        rewards = {item['key'] for item in state['postcards'][0]['rewards']}
        self.assertEqual(rewards, {'pebble', 'star_fragment'})
        self.assertEqual(self.item(state, 'souvenirs', 'pebble')['quantity'], 1)
        self.assertEqual(self.item(state, 'souvenirs', 'star_fragment')['quantity'], 1)
        self.assertEqual(self.item(self.client.get('/api/state').json(), 'souvenirs', 'star_fragment')['quantity'], 1)

    def test_insufficient_food_blocks_departure(self):
        self.adopt()
        self.assertEqual(self.client.post('/api/travel', json={'place': 'sea', 'food': 'apple'}).status_code, 201)
        self.finish()
        self.client.get('/api/state')
        self.assertEqual(self.client.post('/api/travel', json={'place': 'forest', 'food': 'apple'}).status_code, 409)
        state = self.client.get('/api/state').json()
        self.assertIsNone(state['travel'])
        self.assertEqual(self.item(state, 'foods', 'apple')['quantity'], 0)

    def test_expanded_content_catalog_and_new_places(self):
        self.adopt()
        state = self.client.get('/api/state').json()
        for key in ['sandwich', 'pudding', 'cookie', 'hot_tea']:
            self.assertEqual(self.item(state, 'foods', key)['quantity'], 1)
        for key in ['sketchbook', 'compass']:
            self.assertEqual(self.item(state, 'tools', key)['quantity'], 1)
        self.assertEqual(self.client.post('/api/travel', json={'place': 'library', 'food': 'sandwich', 'tool': 'compass'}).status_code, 201)
        self.finish()
        with patch.object(self.game.random, 'random', return_value=0.0):
            state = self.client.get('/api/state').json()
        card = state['postcards'][0]
        self.assertEqual(card['place'], 'library')
        self.assertEqual({item['key'] for item in card['rewards']}, {'bookmark', 'margin_note'})
        self.assertEqual(self.item(state, 'souvenirs', 'margin_note')['quantity'], 1)
        self.assertEqual(self.client.post('/api/travel', json={'place': 'garden', 'food': 'cookie', 'tool': 'sketchbook'}).status_code, 201)
        self.finish()
        with patch.object(self.game.random, 'random', return_value=0.0):
            state = self.client.get('/api/state').json()
        self.assertEqual(state['postcards'][0]['place'], 'garden')
        self.assertEqual(state['postcards'][0]['variant'], 'special')
        self.assertEqual(self.client.post('/api/travel', json={'place': 'town', 'food': 'hot_tea'}).status_code, 201)

    def test_gift_souvenir_between_friends(self):
        self.adopt()
        friend = self.second_player()
        with self.game.database() as con:
            self.game.grant_item(con, 1, 'pinecone', 1, 'test', 'giftable')
        self.assertEqual(self.client.post('/api/gifts', json={'to_username': 'friend', 'item': 'pinecone'}).status_code, 201)
        owner_state = self.client.get('/api/state').json()
        friend_state = friend.get('/api/state').json()
        self.assertEqual(self.item(owner_state, 'souvenirs', 'pinecone')['quantity'], 0)
        self.assertEqual(self.item(friend_state, 'souvenirs', 'pinecone')['quantity'], 1)
        self.assertEqual(owner_state['gifts'][0]['direction'], 'sent')
        self.assertEqual(owner_state['gifts'][0]['to_username'], 'friend')
        self.assertEqual(friend_state['gifts'][0]['direction'], 'received')
        self.assertEqual(friend_state['gifts'][0]['from_username'], 'owner')
        self.assertIn('松果', friend_state['events'][0]['message'])
        self.assertEqual(self.client.post('/api/gifts', json={'to_username': 'friend', 'item': 'pinecone'}).status_code, 409)
        self.assertEqual(self.item(friend.get('/api/state').json(), 'souvenirs', 'pinecone')['quantity'], 1)

    def test_gift_validation(self):
        self.adopt()
        self.assertEqual(self.client.post('/api/gifts', json={'to_username': 'owner', 'item': 'pinecone'}).status_code, 409)
        friend = self.second_player()
        self.assertEqual(self.client.post('/api/gifts', json={'to_username': 'friend', 'item': 'rice_ball'}).status_code, 422)
        self.assertEqual(self.client.post('/api/gifts', json={'to_username': 'missing', 'item': 'pinecone'}).status_code, 404)
        self.assertEqual(self.client.post('/api/gifts', json={'to_username': 'friend', 'item': 'pinecone'}).status_code, 409)

    def test_concurrent_departures_and_settlement(self):
        self.adopt()
        def depart(_):
            with TestClient(self.game.app) as c:
                c.cookies.update(self.client.cookies)
                return c.post('/api/travel',json={'place':'forest'}).status_code
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sorted(pool.map(depart,range(4))),[201,409,409,409])
        self.finish()
        def read(_):
            with TestClient(self.game.app) as c:
                c.cookies.update(self.client.cookies)
                return len(c.get('/api/state').json()['postcards'])
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(list(pool.map(read,range(4))),[1,1,1,1])


    def second_player(self):
        client=TestClient(self.game.app)
        self.addCleanup(client.close)
        self.assertEqual(client.post('/api/register',json={'username':'friend','password':'test-pass-456'}).status_code,201)
        self.assertEqual(client.post('/api/animal',json={'kind':'cat','name':'团子'}).status_code,201)
        return client

    def test_auth_isolation_logout_and_origin(self):
        self.adopt()
        friend=self.second_player()
        self.client.post('/api/travel',json={'place':'forest'})
        self.finish()
        card=self.client.get('/api/state').json()['postcards'][0]
        self.assertEqual(friend.get('/api/state').json()['postcards'],[])
        self.assertEqual(friend.post(f"/api/postcards/{card['id']}/open").status_code,404)
        self.assertEqual(friend.get('/api/state').json()['animal']['name'],'团子')
        self.assertEqual(friend.post('/api/travel',json={'place':'sea'},headers={'origin':'https://evil.example'}).status_code,403)
        cookies=dict(friend.cookies)
        friend.post('/api/logout')
        self.assertIsNone(friend.get('/api/state').json()['user'])
        friend.cookies.update(cookies)
        self.assertEqual(friend.post('/api/travel',json={'place':'sea'}).status_code,401)
        friend.cookies.clear()
        self.assertEqual(friend.post('/api/login',json={'username':'friend','password':'incorrect-password'}).status_code,401)
        self.assertEqual(friend.post('/api/login',json={'username':'friend','password':'test-pass-456'}).status_code,200)
        self.assertEqual(friend.get('/api/state').json()['animal']['name'],'团子')

    def test_shared_encounter_survives_restart_and_is_not_duplicated(self):
        self.adopt()
        friend=self.second_player()
        self.client.post('/api/travel',json={'place':'forest'})
        friend.post('/api/travel',json={'place':'forest'})
        self.assertEqual(friend.get('/api/state').json()['postcards'],[])
        self.finish()
        importlib.reload(self.game)
        a=self.client.get('/api/state').json()['postcards']
        b=friend.get('/api/state').json()['postcards']
        self.assertEqual(len(a),2)
        self.assertEqual(len(b),2)
        ac=next(c for c in a if c['encounter_id'])
        bc=next(c for c in b if c['encounter_id'])
        self.assertEqual(ac['encounter_id'],bc['encounter_id'])
        self.assertEqual(ac['message'],bc['message'])
        self.assertEqual(len(ac['participants']),2)
        self.client.post(f"/api/postcards/{ac['id']}/open")
        self.assertFalse(next(c for c in friend.get('/api/state').json()['postcards'] if c['encounter_id'])['opened'])
        self.assertEqual(len(self.client.get('/api/state').json()['postcards']),2)
        self.assertEqual(len(friend.get('/api/state').json()['events']),3)

    def test_no_encounter_for_different_places_or_nonoverlapping_trips(self):
        self.adopt()
        friend=self.second_player()
        self.client.post('/api/travel',json={'place':'forest'})
        friend.post('/api/travel',json={'place':'sea'})
        self.finish()
        self.client.get('/api/state')
        friend.post('/api/travel',json={'place':'forest'})
        self.finish()
        self.assertEqual(len(self.client.get('/api/state').json()['postcards']),1)
        self.assertEqual(len(friend.get('/api/state').json()['postcards']),2)
        with self.game.database() as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM encounters').fetchone()[0],0)

    def test_shared_cards_arrive_at_each_owners_return_time(self):
        self.adopt()
        friend=self.second_player()
        self.client.post('/api/travel',json={'place':'sea'})
        friend.post('/api/travel',json={'place':'sea'})
        with self.game.database() as con:
            con.execute('UPDATE trips SET ends_at=1 WHERE pet_id=(SELECT id FROM pets WHERE user_id=1)')
        self.assertEqual(len(self.client.get('/api/state').json()['postcards']),2)
        state=friend.get('/api/state').json()
        self.assertIsNotNone(state['travel'])
        self.assertEqual(state['postcards'],[])
        self.finish()
        self.assertEqual(len(friend.get('/api/state').json()['postcards']),2)

    def test_expired_session_and_case_insensitive_duplicate(self):
        response=self.client.post('/api/register',json={'username':'OWNER','password':'test-pass-123'})
        self.assertEqual(response.status_code,409)
        with self.game.database() as con:
            con.execute('UPDATE sessions SET expires_at=0')
        self.assertIsNone(self.client.get('/api/state').json()['user'])
        self.assertEqual(self.client.post('/api/animal',json={'kind':'frog','name':'小满'}).status_code,401)

    def test_legacy_copy_and_explicit_claim(self):
        legacy=Path(self.temp.name)/'legacy.sqlite3'
        with closing(sqlite3.connect(legacy)) as con:
            con.executescript("""
            CREATE TABLE animal(id INTEGER PRIMARY KEY, kind TEXT, name TEXT);
            INSERT INTO animal VALUES(1,'frog','旧小满');
            CREATE TABLE travel(id INTEGER PRIMARY KEY, place TEXT, started_at REAL, ends_at REAL, settled INTEGER);
            INSERT INTO travel VALUES(1,'forest',1,2,1);
            CREATE TABLE postcard(id INTEGER PRIMARY KEY,travel_id INTEGER,place TEXT,animal TEXT,name TEXT,message TEXT,gift TEXT,created_at REAL,opened INTEGER);
            INSERT INTO postcard VALUES(1,1,'forest','frog','旧小满','旧回忆','松果',2,1);
            """)
        os.environ['JOURNEY_DB']=str(legacy)
        importlib.reload(self.game)
        with TestClient(self.game.app) as client:
            self.assertTrue(client.get('/api/state').json()['legacy_available'])
            body={'username':'legacy','password':'legacy-pass-123'}
            self.assertEqual(client.post('/api/register',json=body).status_code,409)
            body['claim_legacy']=True
            self.assertEqual(client.post('/api/register',json=body).status_code,201)
            state=client.get('/api/state').json()
            self.assertEqual(state['animal']['name'],'旧小满')
            self.assertEqual(state['postcards'][0]['message'],'旧回忆')
            self.assertTrue(state['postcards'][0]['opened'])
            self.assertEqual(self.item(state, 'souvenirs', 'pinecone')['quantity'], 1)
            self.assertEqual(self.item(client.get('/api/state').json(), 'souvenirs', 'pinecone')['quantity'], 1)
        self.assertTrue(Path(str(legacy)+'.v1-backup').exists())


if __name__ == '__main__':
    unittest.main()
