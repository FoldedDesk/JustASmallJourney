import importlib
import json
import unittest
from unittest.mock import patch
import test_garden_content
from equipment import CHARMS, TOOL_PERKS, plan_equipment


class EquipmentTests(unittest.TestCase):
    setUp = test_garden_content.GardenContentTests.setUp
    tearDown = test_garden_content.GardenContentTests.tearDown
    state = test_garden_content.GardenContentTests.state

    def finish(self):
        with self.game.database() as con:
            con.execute('UPDATE trips SET ends_at=1 WHERE settled=0')
        return self.state()

    def test_each_tool_has_perks_and_stacking_is_bounded(self):
        self.assertEqual(set(TOOL_PERKS),set(self.game.TOOLS))
        for tool in self.game.TOOLS:
            for charm in [None,*CHARMS]:
                for weather in ['sunny','rainy','windy']:
                    p=plan_equipment(tool,self.game.TOOLS[tool],charm,{'key':weather})
                    self.assertTrue(.6<=p['duration']<=1)
                    for k in ['special','extra','food_return']:
                        self.assertTrue(0<=p[k]<=.9)
        rainy=plan_equipment('raincoat',self.game.TOOLS['raincoat'],'swift_feather',{'key':'rainy'})
        self.assertAlmostEqual(rainy['duration'],.675)
        self.assertEqual(plan_equipment('kite',self.game.TOOLS['kite'],None,{'key':'windy'})['special'],.75)

    def test_charms_purchase_once_and_starter_upgrade(self):
        self.assertEqual(next(i['quantity'] for i in self.state()['inventory']['charms'] if i['key']=='four_leaf'),1)
        importlib.reload(self.game)
        self.assertEqual(next(i['quantity'] for i in self.state()['inventory']['charms'] if i['key']=='four_leaf'),1)
        with self.game.database() as con: con.execute('UPDATE gardens SET clovers=500')
        for key in CHARMS:
            body={'item':key,'request_id':'charm-purchase-'+key.replace('_','-')}
            before=self.state()['garden']['clovers']
            status=self.client.post('/api/shop/buy',json=body).status_code
            self.assertEqual(status,409 if key=='four_leaf' else 200)
            if status==200:
                self.assertEqual(self.client.post('/api/shop/buy',json=body).status_code,200)
                self.assertEqual(self.state()['garden']['clovers'],before-CHARMS[key]['price'])
            self.assertEqual(self.client.post('/api/shop/buy',json={**body,'request_id':body['request_id']+'-new'}).status_code,409)
        self.assertTrue(all(c['quantity']==1 for c in self.state()['inventory']['charms']))

    def test_unowned_and_wrong_category_roll_back_food(self):
        before=self.state()['inventory']
        self.assertEqual(self.client.post('/api/travel',json={'charm':'moon_charm'}).status_code,409)
        self.assertEqual(self.client.post('/api/travel',json={'charm':'camera'}).status_code,422)
        self.assertEqual(self.state()['inventory'],before)

    def test_note_and_speed_are_saved_without_disclosing_destination(self):
        with self.game.database() as con:
            self.game.grant_item(con,1,'letter_knot',1,'test','note')
        with patch.object(self.game.random,'choice',side_effect=[('附近散步',1),'问候']),patch.object(self.game.random,'random',return_value=.99):
            self.assertEqual(self.client.post('/api/travel',json={'tool':'compass','charm':'letter_knot'}).status_code,201)
        trip=self.state()['travel']
        self.assertAlmostEqual(trip['ends_at']-trip['started_at'],self.game.DURATION*.85,places=4)
        self.assertNotIn('equipment',trip)
        self.assertNotIn('place',trip)
        self.assertEqual(trip['charm']['key'],'letter_knot')
        self.assertIsNone(trip['note'])
        importlib.reload(self.game)
        with patch.object(self.game.time,'time',return_value=(trip['ends_at']+trip['started_at'])/2):
            self.assertEqual(self.state()['travel']['note']['message'],'问候')

    def test_return_rewards_once_and_use_departure_snapshot(self):
        with self.game.database() as con:
            self.game.grant_item(con,1,'sewing_kit',1,'test','kit')
            self.game.grant_item(con,1,'dew_charm',1,'test','dew')
        before=self.state()
        self.client.post('/api/travel',json={'tool':'sewing_kit','charm':'dew_charm'})
        with self.game.database() as con:
            snapshot=json.loads(con.execute('SELECT equipment FROM trips').fetchone()[0])
            self.assertEqual(snapshot['clovers'],4)
        importlib.reload(self.game)
        with patch.object(self.game,'plan_equipment',return_value={}),patch.object(self.game.random,'random',return_value=0):
            state=self.finish()
        self.assertEqual(state['garden']['clovers'],before['garden']['clovers']+4)
        self.assertEqual(state['inventory']['foods'][0]['quantity'],before['inventory']['foods'][0]['quantity'])
        self.assertTrue(any('4 枚三叶草' in l for l in state['postcards'][0]['equipment_log']))
        self.assertTrue(any('带回一份' in l for l in state['postcards'][0]['equipment_log']))
        for _ in range(3):
            self.client.post('/api/trips/'+str(state['arrival']['id'])+'/unpack')
            again=self.state()
            self.assertEqual(again['garden'],state['garden'])
            self.assertEqual(again['inventory'],state['inventory'])

    def test_moon_works_without_tool_and_old_trips_get_no_new_perks(self):
        with self.game.database() as con: self.game.grant_item(con,1,'moon_charm',1,'test','moon')
        self.client.post('/api/travel',json={'charm':'moon_charm'})
        with patch.object(self.game.random,'random',return_value=.1):
            state=self.finish()
        self.assertEqual(state['postcards'][0]['variant'],'special')
        self.client.post('/api/travel',json={'tool':'sketchbook'})
        before=self.state()['garden']['clovers']
        with self.game.database() as con: con.execute("UPDATE trips SET equipment='{}' WHERE settled=0")
        state=self.finish()
        self.assertEqual(state['garden']['clovers'],before)
        self.assertEqual(state['postcards'][0]['equipment_log'],[])
