"""Private equipment rules, snapshotted at departure."""
TOOL_PERKS = {
    'camera': ({'note': .85}, '更常寄来途中见闻。'),
    'sketchbook': ({'clovers': 1}, '会把路边拾到的一枚三叶草夹回来。'),
    'map': ({'duration': .9}, '认路更顺，旅程稍短。'),
    'compass': ({'duration': .85}, '少走弯路，更早回家。'),
    'binoculars': ({'note': 1}, '总会捎来一句途中观察。'),
    'watercolors': ({'special': .15}, '更擅长记录特别风景。'),
    'notebook': ({'note': 1}, '每次都会写一则途中笔记。'),
    'music_box': ({'food_return': .3}, '休息更从容，有时会把备用的一份食物带回来。'),
    'lantern_tool': ({'clovers': 2}, '照亮脚边，带回两枚三叶草。'),
    'walking_stick': ({'duration': .8}, '脚步更稳，较早回家。'),
    'thermos': ({'food_return': .4}, '补给安排得更好，有机会带回一份同款食物。'),
    'raincoat': ({'rain_duration': .75}, '雨天不必久等，归程更快。'),
    'picnic_mat': ({'food_return': .25, 'note': .85}, '午餐更从容，常写来信，偶尔带回备用点心。'),
    'field_guide': ({'clovers': 3}, '认出路旁的三叶草，带回三枚。'),
    'shell_pouch': ({'extra': .2}, '额外纪念品更不容易错过。'),
    'stamp_book': ({'special': .15}, '沿途收集印记，更容易留下特别风景。'),
    'kite': ({'wind_special': .25}, '有风时更容易记录特别风景。'),
    'magnifier': ({'extra': .2}, '放大细节，更容易发现额外纪念品。'),
    'sewing_kit': ({'clovers': 2, 'food_return': .2}, '修好行囊带回两枚三叶草，偶尔保住备用食物。'),
    'folding_cup': ({'note': 1}, '歇脚时总会写一句话带回给你。'),
}
CHARMS = {
    'four_leaf': {'name':'四叶草信物','icon':'🍀','price':18,'description':'让额外纪念品更容易出现。每次旅行都可以带上。'},
    'swift_feather': {'name':'轻羽信物','icon':'🪶','price':24,'description':'让旅途轻快一点，稍早回到小屋。'},
    'letter_knot': {'name':'思念绳结','icon':'🪢','price':20,'description':'每段旅行都会捎来一句问候。'},
    'picnic_pouch': {'name':'点心护符','icon':'🥠','price':24,'description':'有机会把一份同款食物带回家。'},
    'dew_charm': {'name':'晨露小坠','icon':'💧','price':22,'description':'每次归来多带两枚三叶草。'},
    'moon_charm': {'name':'月光信物','icon':'🌙','price':26,'description':'即使不带相机，也有机会留下特别风景。'},
}
CHARM_PERKS = {
    'four_leaf': {'extra':.15}, 'swift_feather': {'duration':.9},
    'letter_knot': {'note':1}, 'picnic_pouch': {'food_return':.35},
    'dew_charm': {'clovers':2}, 'moon_charm': {'special':.2},
}

def plan_equipment(tool_key, tool, charm_key, weather):
    result={'duration':1,'note':.65,'special':.5 if tool and tool['effect']=='special' else 0,
            'extra':.5 if tool and tool['effect']=='extra' else 0,'clovers':0,'food_return':0}
    for perks in [TOOL_PERKS.get(tool_key, ({},''))[0],CHARM_PERKS.get(charm_key,{})]:
        result['duration'] *= perks.get('duration',1)
        if weather['key']=='rainy': result['duration'] *= perks.get('rain_duration',1)
        result['note']=max(result['note'],perks.get('note',0))
        for key in ('special','extra','clovers','food_return'):
            result[key]+=perks.get(key,0)
        if weather['key']=='windy': result['special']+=perks.get('wind_special',0)
    for key in ('special','extra','food_return'): result[key]=min(.9,result[key])
    result['duration']=max(.6,result['duration'])
    result['names']=[v for v in [tool['name'] if tool else None,CHARMS[charm_key]['name'] if charm_key else None] if v]
    return result
