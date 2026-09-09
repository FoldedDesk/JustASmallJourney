"""Rebuild offline content references from the server catalog, using a disposable DB."""
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def export(game):
    from equipment import CHARMS, TOOL_PERKS, CHARM_PERKS
    equipment = ['# 工具与信物说明（离线数值参考）','','工具与信物各可选带一件，均不消耗。六种信物可在小铺兑换；初始四叶草通过新手物品的唯一发放记录，向新老玩家各发一枚。拥有后不能再次付费兑换。', '',
        '原工具的特别风景或额外纪念品基础概率仍为 50%。以下效果叠加：duration 为时长乘数；note 为途中来信概率（取最高值）；special、extra、food_return 分别为特别风景、额外纪念品、带回一份同款食物的概率加值；clovers 为额外三叶草数量。rain_duration 仅雨天乘入时长，wind_special 仅有风时加到特别风景。', '',
        '概率加值最高 90%，时长最低为原来的 60% 且不少于一秒。来信基础概率 65%；三叶草直接进余额，食物返回原背包。食品先在出发时扣一份，归来才判断是否带回。奖励与旅行结算在同一事务内，只发一次。', '',
        '效果取出发时的天气，时长不依赖目的地。信物不直接修改目的地权重，不改变原特殊搭配条件；月光信物可独立触发特别风景，四叶草可独立带来额外纪念品。普通装备说明可在前端显示，但配方和概率不下发。装备效果快照保存在旅行中，旧进行中旅行没有快照时沿用旧规则。', '',
        '| 工具 | 新用途 | 数值 |','| --- | --- | --- |']
    for key,(perks,description) in TOOL_PERKS.items():
        equipment.append('| '+game.TOOLS[key]['name']+' | '+description+' | `'+str(perks)+'` |')
    equipment+=['','## 信物','','| 名称 | 用途 | 价格 | 数值 |','| --- | --- | --- | --- |']
    for key,item in CHARMS.items():
        equipment.append('| '+item['name']+' | '+item['description']+' | '+str(item['price'])+' | `'+str(CHARM_PERKS[key])+'` |')
    equipment+=['','例：雨披＋轻羽在雨天为原时长的 67.5%；针线盒＋晨露归来额外 4 三叶草；保温壶＋点心护符有 75% 概率带回同款食物。隐藏搭配仍优先决定明信片故事，因此特别风景判定不会覆盖已命中的搭配故事。']
    (ROOT/'docs'/'工具与信物说明.md').write_text('\n'.join(equipment)+'\n')
    from content import FOOD_DESTINATIONS, TOOL_DESTINATIONS, FOOD_BONUS, TOOL_BONUS, destination_weights
    docs = ROOT/'docs'
    recipes = ['# 特殊搭配攻略（仅供离线查阅）', '',
        '这份文档只供本地策划和开发使用，不随网页发布，不在前端公开触发条件。', '',
        '出发时先按行囊权重随机确定目的地，再匹配食物、地点和可选工具。带齐物品不保证抵达指定地点。更具体的工具搭配优先；结果随旅行保存，刷新或重启不会重抽。', '',
        '共 50 组搭配。搭配明信片替代该次普通风景；基础纪念品仍会获得，额外物品效果照常独立判定。同种纪念品同一次结算只计一次。部分搭配会带回已在别处发现的纪念品，独特之处在于共同构成的故事。', '',
        '| 编号 | 地点 | 食物 | 工具 | 明信片 | 搭配纪念品 |', '| --- | --- | --- | --- | --- | --- |']
    for n,c in enumerate(game.COMBINATIONS,1):
        recipes.append(f"| {n:02} | {game.PLACES[c['place']]['name']} | {game.FOODS[c['food']]['name']} | {game.TOOLS[c['tool']]['name'] if c['tool'] else '不限（可不带）'} | {c['title']} | {game.SOUVENIRS[c['reward']]['name']} |")
    recipes += ['', '## 搭配故事', '']
    for c in game.COMBINATIONS:
        recipes += ['### '+c['title'], '', c['message'], '']
    (docs/'特殊搭配攻略.md').write_text('\n'.join(recipes).rstrip()+'\n')
    probability=['# 目的地概率说明（离线参考）','','这是本游戏的暂定规则，不是《旅行青蛙》的官方概率；不会在前端展示或下发。', '',
        f'目前 {len(game.PLACES)} 个目的地，每个基础权重为 10。食物偏好的两个地点各加 {FOOD_BONUS}，工具偏好的两个地点各加 {TOOL_BONUS}；饭团无偏好。重叠相加，概率＝地点权重÷总权重，所有地点都能抵达。', '',
        '扩展地图后同步调整了倾向强度：食物加分＝地点数×3，工具加分＝地点数。无保底、无防重复，不接受客户端指定地点。信物现已开放，不直接改变目的地权重；具体作用见[工具与信物说明](工具与信物说明.md)。路线抽取一次后入库存档。', '',
        '## 大致概率', '', '| 行囊 | 示例地点 | 概率 |','| --- | --- | --- |']
    for food,tool,keys in [('rice_ball',None,['forest']),('cocoa',None,['snow','forest']),('lemon_soda','camera',['sea','desert','mountain','forest']),('rice_ball','camera',['sea','forest'])]:
        weights=destination_weights(food,tool)
        for key in keys:
            probability.append(f"| {game.FOODS[food]['name']}＋{game.TOOLS[tool]['name'] if tool else '无工具'} | {game.PLACES[key]['name']} | {weights[key]/sum(weights.values()):.2%} |")
    for title,mapping,catalog in [('食物倾向',FOOD_DESTINATIONS,game.FOODS),('工具倾向',TOOL_DESTINATIONS,game.TOOLS)]:
        probability += ['', '## '+title, '', '| 物品 | 更容易到达 |','| --- | --- |']
        for key,bias in mapping.items():
            probability.append('| '+catalog[key]['name']+' | '+('、'.join(game.PLACES[p]['name'] for p in bias) or '无倾向')+' |')
    probability += ['', '## 旅行保密与偶遇', '', '旅行期间自己、好友状态和出发动态不公开目的地；世界偶遇动态等双方归来后才公开。归来的玩家可以从自己的共同明信片知道相遇地点。特殊搭配见[离线攻略](特殊搭配攻略.md)。', '', '规则位于 `content.py`，扩展内容位于 `expansion.py`。']
    (docs/'目的地概率说明.md').write_text('\n'.join(probability)+'\n')
    overview=['# 内容目录（扩充版）', '',
        '总量：60 种食物、50 个目的地、100 种纪念品、20 种工具。每地普通／特别风景各一款，共 100 款风景明信片；另有 50 款隐藏搭配故事，以及随朋友相遇生成的同行明信片。', '',
        '沿用 Emoji 与 CSS 美术：新地点共用十类地貌背景，每地有独立名字、故事和三个互动点；这不是 50 张独立手绘背景。新场景互动随已获得的明信片提供，未获得的故事和搭配不会下发。', '',
        '食物均可兑换，单次消耗一份。工具与六种信物兑换后永久可用，四件原工具与四叶草信物为新手物品。工具除原效果外还有时长、途中信、三叶草与食物返回等新用途，详见[工具与信物说明](工具与信物说明.md)。草圃和每日补给规则不变。', '',
        '## 地点与明信片', '', '| 地点 | 普通风景 | 特别风景 | 基础纪念品 | 额外纪念品 |', '| --- | --- | --- | --- | --- |']
    for p in game.PLACES.values():
        overview.append(f"| {p['name']} | {p['standard_title']} | {p['special_title']} | {game.SOUVENIRS[p['gift_key']]['name']} | {game.SOUVENIRS[p['extra_gift_key']]['name']} |")
    for title,catalog in [('食物',game.FOODS),('工具',game.TOOLS),('纪念品',game.SOUVENIRS)]:
        overview+=['','## '+title,'','| 名称 | 说明 |'+(' 价格（☘） |' if title!='纪念品' else ''),'| --- | --- |'+(' --- |' if title!='纪念品' else '')]
        for item in catalog.values():
            overview.append('| '+item['icon']+' '+item['name']+' | '+item['description']+' |'+(' '+str(item['price'])+' |' if title!='纪念品' else ''))
    overview+=['','## 维护与验证','','运行 `rtk proxy .venv/bin/python scripts/export_content_docs.py` 可同步三份离线目录。运行测试可验证数量、引用、全部普通／特别风景、额外纪念品、50 组搭配及工具兑换幂等。旧物品 ID 与已保存的明信片内容不变。']
    (docs/'内容目录.md').write_text('\n'.join(overview)+'\n')

if __name__=='__main__':
    with tempfile.TemporaryDirectory() as temp:
        os.environ['JOURNEY_DB']=str(Path(temp)/'docs.sqlite3')
        import app
        export(app)
    print('已同步内容目录、特殊搭配攻略、目的地概率及工具信物说明。')
