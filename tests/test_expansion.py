import importlib
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient
import test_garden_content


class ExpansionTests(unittest.TestCase):
    setUp = test_garden_content.GardenContentTests.setUp
    tearDown = test_garden_content.GardenContentTests.tearDown
    state = test_garden_content.GardenContentTests.state

    def test_content_graph_and_all_normal_postcards_are_obtainable(self):
        game = self.game
        self.assertEqual((len(game.FOODS),len(game.PLACES),len(game.SOUVENIRS),len(game.TOOLS),len(game.COMBINATIONS)), (60,50,100,20,50))
        for catalog in (game.FOODS,game.PLACES,game.SOUVENIRS,game.TOOLS):
            self.assertEqual(len({v['name'] for v in catalog.values()}),len(catalog))
        reachable = {'travel_badge'}
        for place in game.PLACES.values():
            reachable.update([place['gift_key'],place['extra_gift_key']])
        reachable.update(c['reward'] for c in game.COMBINATIONS)
        self.assertEqual(reachable,set(game.SOUVENIRS))
        with game.database() as con:
            game.grant_item(con,1,'rice_ball',200,'test','world-tour')
        templates, titles = set(), set()
        for key, place in game.PLACES.items():
            for variant, tool, chance in [('standard',None,.99),('special','camera',0),('standard','map',0)]:
                with self.subTest(place=key,variant=variant,tool=tool):
                    with patch.object(game,'choose_destination',return_value=key):
                        self.assertEqual(self.client.post('/api/travel',json={'food':'rice_ball','tool':tool}).status_code,201)
                    self.assertNotIn('place',self.state()['travel'])
                    with game.database() as con:
                        con.execute('UPDATE trips SET ends_at=1 WHERE settled=0')
                    with patch.object(game.random,'random',return_value=chance):
                        card=self.state()['postcards'][0]
                    self.assertEqual(card['template_key'],key+':'+variant)
                    self.assertEqual(card['title'],place[variant+'_title'])
                    self.assertIn(place['gift_key'],[i['key'] for i in card['rewards']])
                    if tool=='map':
                        self.assertIn(place['extra_gift_key'],[i['key'] for i in card['rewards']])
                    if 'objects' in place:
                        self.assertEqual(len(card['scene']['objects']),3)
                        self.assertEqual(len({o[1] for o in card['scene']['objects']}),3)
                        self.assertIn(card['scene']['theme'],{'forest','sea','mountain','library','town','garden','lake','desert','snow','ruins'})
                    templates.add(card['template_key'])
                    titles.add(card['title'])
        self.assertEqual(len(templates),100)
        self.assertEqual(len(titles),100)
        importlib.reload(game)
        self.assertEqual(len(self.state()['postcards']),150)

    def test_all_tools_can_be_bought_once_and_retries_do_not_charge(self):
        with self.game.database() as con:
            con.execute('UPDATE gardens SET clovers=1000')
        for key, tool in self.game.TOOLS.items():
            before=self.state()
            owned=next(i['quantity'] for i in before['inventory']['tools'] if i['key']==key)
            body={'item':key,'request_id':'tool-purchase-'+key.replace('_','-')+'-001'}
            response=self.client.post('/api/shop/buy',json=body)
            self.assertEqual(response.status_code,409 if owned else 200)
            after=self.state()
            self.assertEqual(after['garden']['clovers'],before['garden']['clovers']-(0 if owned else tool['price']))
            if not owned:
                self.assertEqual(self.client.post('/api/shop/buy',json=body).status_code,200)
                self.assertEqual(self.state()['garden']['clovers'],after['garden']['clovers'])
                self.assertEqual(self.client.post('/api/shop/buy',json={**body,'request_id':body['request_id']+'-again'}).status_code,409)
        self.assertTrue(all(t['quantity']==1 for t in self.state()['inventory']['tools']))

    def test_concurrent_tool_orders_grant_only_one(self):
        with self.game.database() as con:
            con.execute('UPDATE gardens SET clovers=100')
        def purchase(index):
            with TestClient(self.game.app) as client:
                client.cookies.update(self.client.cookies)
                return client.post('/api/shop/buy',json={'item':'binoculars','request_id':'parallel-tool-order-'+str(index)}).status_code
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sorted(pool.map(purchase,range(4))),[200,409,409,409])
        state=self.state()
        self.assertEqual(state['garden']['clovers'],82)
        self.assertEqual(next(t['quantity'] for t in state['inventory']['tools'] if t['key']=='binoculars'),1)

    def test_private_recipes_are_not_in_public_catalog_or_pending_trip(self):
        import json
        public=json.dumps(self.state()['catalog'],ensure_ascii=False)
        for recipe in self.game.COMBINATIONS:
            self.assertNotIn(recipe['message'],public)
            self.assertNotIn(recipe['title'],public)
        self.assertNotIn('objects',public)
        self.assertNotIn('FOOD_BONUS',public)
