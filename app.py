"""Private shared travel world. SQLite and server time are authoritative."""
import hashlib
import hmac
import json
import os
import random
import secrets
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from content import EXTRA_FOODS, EXTRA_PLACES, EXTRA_SOUVENIRS, PLACE_PRESENTATION, COMBINATIONS, match_combination
from content import choose_destination

ROOT = Path(__file__).parent
DB = Path(os.environ.get('JOURNEY_DB', ROOT / 'data/journey.sqlite3'))
DB.parent.mkdir(parents=True, exist_ok=True)
DURATION = max(1, int(os.environ.get('JOURNEY_DURATION_SECONDS', '60')))
GROW_SECONDS = max(1, int(os.environ.get('JOURNEY_GROW_SECONDS', '300')))
HARVEST_AMOUNT = 6
TRIP_LENGTHS = [('附近散步', 1), ('悠闲漫游', 2), ('小小远行', 3)]
TRAIL_NOTES = ['刚找到一处可以歇脚的地方，带来的点心很好吃。', '遇见一阵轻轻的风，想把这份好心情带回去。', '沿途有好多小细节，等回家再慢慢讲给你听。', '停下来整理了一下行囊，一切都好，不用担心。']
SESSION_SECONDS = 30 * 86400
TIMEZONE = ZoneInfo(os.environ.get('JOURNEY_TIMEZONE', 'Asia/Shanghai'))
ANIMALS = ['frog', 'cat', 'fox', 'rabbit', 'squirrel']
WEATHER = {
    'sunny': {'name': '晴朗', 'icon': '☀️', 'note': '适合慢慢散步，把阳光带回家。', 'memory': '阳光把一路的影子拉得很长。'},
    'cloudy': {'name': '多云', 'icon': '☁️', 'note': '云走得很慢，今天也不用着急。', 'memory': '看着云变成小动物的形状，忍不住多停了一会儿。'},
    'rainy': {'name': '小雨', 'icon': '🌧️', 'note': '听听雨声，也是一场小旅行。', 'memory': '在屋檐下听了一阵雨，等雨小了才继续走。'},
    'windy': {'name': '微风', 'icon': '🍃', 'note': '风会捎来远方的小消息。', 'memory': '风翻动了行囊边的小纸条，像在催我给你写信。'},
}
SEASONS = {
    'spring': {'name': '春天', 'note': '路边的新芽，正在悄悄长大。'},
    'summer': {'name': '夏天', 'note': '树荫和晚风，都值得多停留一会儿。'},
    'autumn': {'name': '秋天', 'note': '捡起一片落叶，把秋天夹进回忆。'},
    'winter': {'name': '冬天', 'note': '远行之后，记得回温暖的小屋。'},
}


def world_weather(now):
    """Fictional shared weather; stable for a local calendar day across restarts."""
    day = datetime.fromtimestamp(now, TIMEZONE)
    date = day.date().isoformat()
    key = list(WEATHER)[int(hashlib.sha256(date.encode()).hexdigest()[:8], 16) % len(WEATHER)]
    season = ('winter', 'spring', 'summer', 'autumn')[(day.month % 12) // 3]
    return {'date': date, 'key': key, **WEATHER[key], 'season': {'key': season, **SEASONS[season]}}


PLACES = {
    'forest': {
        'name': '微风森林',
        'gift': '一枚松果',
        'gift_key': 'pinecone',
        'extra_gift_key': 'pressed_leaf',
        'lines': ['树叶沙沙响，像是在说欢迎你。', '在树荫下吃完饭团，又听了一会儿风。', '沿着苔藓小路，发现了一片心形的叶子。'],
        'special_lines': ['相机刚好拍下风穿过树叶的那一刻，整片森林都亮了一下。', '在树根边发现一束小光，像森林悄悄寄来的签名。'],
    },
    'sea': {
        'name': '日落海岸',
        'gift': '一枚贝壳',
        'gift_key': 'shell',
        'extra_gift_key': 'sea_glass',
        'lines': ['把烦恼留给海风，把贝壳带回来给你。', '今天的浪花，一朵比一朵温柔。', '等到太阳落进海里，才舍得往回走。'],
        'special_lines': ['相机里留下了太阳落进海面的最后一秒，像一颗橘色糖。', '浪花打湿了脚印，也把今天照得很柔软。'],
    },
    'mountain': {
        'name': '星星山谷',
        'gift': '一颗小石子',
        'gift_key': 'pebble',
        'extra_gift_key': 'star_fragment',
        'lines': ['山里的风很轻，星星离我很近。', '在山坡上坐了一会儿，云慢慢走过。', '带回一颗小石子，也带回一点勇气。'],
        'special_lines': ['相机拍到第一颗星亮起来，山谷安静得像一封信。', '在月光下抬头的时候，好像听见山谷轻轻回应了一声。'],
    },
    'library': {
        'name': '晴窗图书馆',
        'gift': '一枚书签',
        'gift_key': 'bookmark',
        'extra_gift_key': 'margin_note',
        'lines': ['在靠窗的位置读了一下午，阳光慢慢挪到书脊上。', '翻到一页夹着花瓣的旧书，像遇见很久以前的天气。', '图书馆很安静，连脚步声都放轻了。'],
        'special_lines': ['速写本上留下了一排书架和一束阳光，像把下午折进纸里。', '相机拍到灰尘在光里游泳，安静得很好看。'],
    },
    'town': {
        'name': '铃铛小镇',
        'gift': '一张车票根',
        'gift_key': 'ticket_stub',
        'extra_gift_key': 'postmark',
        'lines': ['小镇的风铃叮当响，街角面包店刚好出炉。', '在石板路上慢慢走，口袋里装着一张小小票根。', '黄昏时路灯亮起来，小镇像刚睡醒一样温柔。'],
        'special_lines': ['相机拍下风铃摇晃的一瞬间，整条街都像在眨眼。', '速写本里多了一盏路灯，还有路过的人留下的影子。'],
    },
    'garden': {
        'name': '雨后花园',
        'gift': '一朵干花',
        'gift_key': 'pressed_flower',
        'extra_gift_key': 'dew_bead',
        'lines': ['雨刚停，花瓣上还挂着很小的光。', '沿着湿湿的小径走了一圈，鞋尖沾到一点青草香。', '花园里没有人催促，连云都慢慢散开。'],
        'special_lines': ['相机靠近花瓣时，露珠里倒映出一整个小小天空。', '速写本上画了一朵花，旁边写着“今天很适合想念”。'],
    },
}
FOODS = {
    'rice_ball': {'name': '饭团', 'icon': '🍙', 'description': '朴素可靠，适合每一次小远行。'},
    'apple': {'name': '苹果', 'icon': '🍎', 'description': '清甜轻便，路上可以慢慢吃。'},
    'sandwich': {'name': '三明治', 'icon': '🥪', 'description': '夹着蔬菜和一点好心情。'},
    'pudding': {'name': '布丁', 'icon': '🍮', 'description': '软软甜甜，适合带去看日落。'},
    'cookie': {'name': '曲奇', 'icon': '🍪', 'description': '咬一口会掉屑，也会开心。'},
    'hot_tea': {'name': '热茶', 'icon': '🍵', 'description': '慢慢喝，路也会显得不那么远。'},
}
TOOLS = {
    'camera': {'name': '相机', 'icon': '📷', 'description': '更容易拍到特别明信片。', 'effect': 'special'},
    'sketchbook': {'name': '速写本', 'icon': '📓', 'description': '更容易留下特别明信片。', 'effect': 'special'},
    'map': {'name': '地图', 'icon': '🗺️', 'description': '更容易发现额外纪念品。', 'effect': 'extra'},
    'compass': {'name': '指南针', 'icon': '🧭', 'description': '更容易找到额外纪念品。', 'effect': 'extra'},
}
SOUVENIRS = {
    'pinecone': {'name': '松果', 'icon': '🌰', 'description': '来自微风森林的小礼物。'},
    'pressed_leaf': {'name': '压花叶片', 'icon': '🍃', 'description': '地图上标出的小路尽头，夹着一片好看的叶子。'},
    'shell': {'name': '贝壳', 'icon': '🐚', 'description': '海浪慢慢磨亮的声音。'},
    'sea_glass': {'name': '海玻璃', 'icon': '💎', 'description': '被海水磨圆的一点亮光。'},
    'pebble': {'name': '小石子', 'icon': '🪨', 'description': '从星星山谷带回的一点勇气。'},
    'star_fragment': {'name': '星光碎片', 'icon': '✨', 'description': '山路旁偶然发现的亮晶晶。'},
    'bookmark': {'name': '书签', 'icon': '🔖', 'description': '晴窗图书馆夹在书页里的小小停顿。'},
    'margin_note': {'name': '页边小记', 'icon': '📝', 'description': '有人在书页旁留下的一句轻声话。'},
    'ticket_stub': {'name': '车票根', 'icon': '🎟️', 'description': '铃铛小镇车站边带回的纸片。'},
    'postmark': {'name': '小镇邮戳', 'icon': '📮', 'description': '盖着日期和风铃声的纪念。'},
    'pressed_flower': {'name': '干花', 'icon': '🌼', 'description': '雨后花园里晾干的一点香气。'},
    'dew_bead': {'name': '露珠珠子', 'icon': '🫧', 'description': '像把雨后的早晨收进掌心。'},
    'travel_badge': {'name': '同行纪念章', 'icon': '🏵️', 'description': '和朋友的小动物相遇时留下的共同回忆。'},
}
PLACES.update(EXTRA_PLACES)
for key, (icon, tag, description) in PLACE_PRESENTATION.items():
    PLACES[key].update(icon=icon, tag=tag, description=description)
FOODS.update(EXTRA_FOODS)
for key, food in FOODS.items():
    food.setdefault('price', 2 if key == 'rice_ball' else 3)
SOUVENIRS.update(EXTRA_SOUVENIRS)
ITEM_CATALOG = {
    **{key: {**value, 'category': 'food'} for key, value in FOODS.items()},
    **{key: {**value, 'category': 'tool'} for key, value in TOOLS.items()},
    **{key: {**value, 'category': 'souvenir'} for key, value in SOUVENIRS.items()},
}
STARTER_ITEMS = {'rice_ball': 3, 'apple': 1, 'sandwich': 1, 'pudding': 1, 'cookie': 1, 'hot_tea': 1, 'camera': 1, 'sketchbook': 1, 'map': 1, 'compass': 1}
GIFT_TO_ITEM = {
    '松果': 'pinecone',
    '一枚松果': 'pinecone',
    '贝壳': 'shell',
    '一枚贝壳': 'shell',
    '小石子': 'pebble',
    '一颗小石子': 'pebble',
    '书签': 'bookmark',
    '一枚书签': 'bookmark',
    '车票根': 'ticket_stub',
    '一张车票根': 'ticket_stub',
    '干花': 'pressed_flower',
    '一朵干花': 'pressed_flower',
    '一枚同行纪念章': 'travel_badge',
    '同行纪念章': 'travel_badge',
}


@contextmanager
def database():
    con = sqlite3.connect(DB, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    try:
        with con:
            yield con
    finally:
        con.close()

def ensure_column(con, table, column, definition):
    columns = {row['name'] for row in con.execute(f'PRAGMA table_info({table})')}
    if column not in columns:
        con.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')

with database() as con:
    # Keep the original prototype tables intact; copy the database before first upgrade.
    old = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animal'").fetchone()
    upgraded = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
    if old and not upgraded:
        backup = sqlite3.connect(str(DB) + '.v1-backup')
        try:
            con.backup(backup)
        finally:
            backup.close()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE COLLATE NOCASE, password_hash TEXT NOT NULL, created_at REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), expires_at REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS pets(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL UNIQUE REFERENCES users(id), kind TEXT NOT NULL, name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS trips(id INTEGER PRIMARY KEY, pet_id INTEGER NOT NULL REFERENCES pets(id), place TEXT NOT NULL, started_at REAL NOT NULL, ends_at REAL NOT NULL, settled INTEGER NOT NULL DEFAULT 0);
    CREATE UNIQUE INDEX IF NOT EXISTS one_trip_per_pet ON trips(pet_id) WHERE settled=0;
    CREATE TABLE IF NOT EXISTS encounters(id INTEGER PRIMARY KEY, trip_a INTEGER NOT NULL REFERENCES trips(id), trip_b INTEGER NOT NULL REFERENCES trips(id), place TEXT NOT NULL, participants TEXT NOT NULL, message TEXT NOT NULL, occurred_at REAL NOT NULL, UNIQUE(trip_a,trip_b));
    CREATE TABLE IF NOT EXISTS cards(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), trip_id INTEGER NOT NULL REFERENCES trips(id), encounter_id INTEGER REFERENCES encounters(id), place TEXT NOT NULL, animal TEXT NOT NULL, name TEXT NOT NULL, message TEXT NOT NULL, gift TEXT NOT NULL, created_at REAL NOT NULL, opened INTEGER NOT NULL DEFAULT 0, participants TEXT NOT NULL DEFAULT '[]');
    CREATE UNIQUE INDEX IF NOT EXISTS solo_card ON cards(trip_id) WHERE encounter_id IS NULL;
    CREATE UNIQUE INDEX IF NOT EXISTS shared_card ON cards(user_id,encounter_id) WHERE encounter_id IS NOT NULL;
    CREATE TABLE IF NOT EXISTS inventory(user_id INTEGER NOT NULL REFERENCES users(id), item_key TEXT NOT NULL, quantity INTEGER NOT NULL DEFAULT 0, first_obtained_at REAL NOT NULL, PRIMARY KEY(user_id,item_key));
    CREATE TABLE IF NOT EXISTS item_grants(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), item_key TEXT NOT NULL, quantity INTEGER NOT NULL, source_type TEXT NOT NULL, source_id TEXT NOT NULL, created_at REAL NOT NULL, UNIQUE(user_id,item_key,source_type,source_id));
    CREATE TABLE IF NOT EXISTS daily_claims(user_id INTEGER NOT NULL REFERENCES users(id), claim_date TEXT NOT NULL, created_at REAL NOT NULL, PRIMARY KEY(user_id,claim_date));
    CREATE TABLE IF NOT EXISTS gifts(id INTEGER PRIMARY KEY, from_user_id INTEGER NOT NULL REFERENCES users(id), to_user_id INTEGER NOT NULL REFERENCES users(id), item_key TEXT NOT NULL, message TEXT NOT NULL, created_at REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, message TEXT NOT NULL, created_at REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS auth_attempts(address TEXT PRIMARY KEY, count INTEGER NOT NULL, started_at REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS gardens(user_id INTEGER PRIMARY KEY REFERENCES users(id), clovers INTEGER NOT NULL DEFAULT 12 CHECK(clovers>=0));
    CREATE TABLE IF NOT EXISTS garden_plots(user_id INTEGER NOT NULL REFERENCES users(id), plot INTEGER NOT NULL CHECK(plot BETWEEN 1 AND 3), ready_at REAL, cycle INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(user_id,plot));
    CREATE TABLE IF NOT EXISTS shop_orders(user_id INTEGER NOT NULL REFERENCES users(id), request_id TEXT NOT NULL, item_key TEXT NOT NULL, price INTEGER NOT NULL, created_at REAL NOT NULL, PRIMARY KEY(user_id,request_id));
    """)
    ensure_column(con, 'trips', 'food_key', 'TEXT')
    ensure_column(con, 'trips', 'tool_key', 'TEXT')
    ensure_column(con, 'trips', 'weather', "TEXT NOT NULL DEFAULT '{}'")
    ensure_column(con, 'trips', 'combination', "TEXT NOT NULL DEFAULT '{}'")
    ensure_column(con, 'trips', 'duration_label', "TEXT NOT NULL DEFAULT '小小远行'")
    ensure_column(con, 'trips', 'trail_note', "TEXT NOT NULL DEFAULT ''")
    ensure_column(con, 'trips', 'note_at', 'REAL')
    # Existing journeys have already used the old return flow.
    ensure_column(con, 'trips', 'unpacked', 'INTEGER NOT NULL DEFAULT 1')
    ensure_column(con, 'cards', 'rewards', "TEXT NOT NULL DEFAULT '[]'")
    ensure_column(con, 'cards', 'variant', "TEXT NOT NULL DEFAULT 'standard'")
    ensure_column(con, 'cards', 'title', "TEXT NOT NULL DEFAULT ''")
    ensure_column(con, 'cards', 'template_key', "TEXT NOT NULL DEFAULT ''")
    ensure_column(con, 'cards', 'combination', "TEXT NOT NULL DEFAULT '{}'")
    ensure_column(con, 'events', 'encounter_id', 'INTEGER REFERENCES encounters(id)')
    if not con.execute("SELECT 1 FROM settings WHERE key='hidden_routes_v1'").fetchone():
        con.execute('UPDATE events SET encounter_id=(SELECT id FROM encounters WHERE encounters.message=events.message AND encounters.occurred_at=events.created_at LIMIT 1)')
        for event in con.execute("SELECT id,message FROM events WHERE message LIKE '%去了%'").fetchall():
            con.execute('UPDATE events SET message=? WHERE id=?', (event['message'].split('去了')[0] + '出发去旅行了。', event['id']))
        con.execute("INSERT INTO settings VALUES('hidden_routes_v1','done')")

app = FastAPI(title='JustASmallJourney')

@app.middleware('http')
async def same_origin(request: Request, call_next):
    if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
        origin = request.headers.get('origin')
        if request.headers.get('sec-fetch-site') == 'cross-site' or (origin and urlsplit(origin).netloc != request.headers.get('host')):
            return JSONResponse({'detail':'请从游戏页面进行操作。'}, status_code=403)
    response = await call_next(request)
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response

class Credentials(BaseModel):
    username: str = Field(min_length=1, max_length=24)
    password: str = Field(min_length=8, max_length=128)
    claim_legacy: bool = False

class AnimalInput(BaseModel):
    kind: str
    name: str = Field(min_length=1, max_length=16)

class TravelInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    food: str = 'rice_ball'
    tool: str | None = None

class GiftInput(BaseModel):
    to_username: str = Field(min_length=1, max_length=24)
    item: str

class ShopInput(BaseModel):
    item: str
    request_id: str = Field(min_length=16, max_length=80, pattern=r'^[a-zA-Z0-9-]+$')

def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 600000).hex()
    return salt + ':' + digest

def identity(con, request, required=True):
    token = hashlib.sha256(request.cookies.get('journey_session', '').encode()).hexdigest()
    user = con.execute('SELECT u.id,u.username FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token=? AND s.expires_at>?', (token,time.time())).fetchone()
    if required and not user:
        raise HTTPException(401, '请先登录你的小屋。')
    return user

def legacy_available(con):
    if con.execute('SELECT 1 FROM users LIMIT 1').fetchone():
        return False
    if not con.execute("SELECT 1 FROM sqlite_master WHERE name='animal' AND type='table'").fetchone():
        return False
    return bool(con.execute('SELECT 1 FROM animal').fetchone())

def local_day(now):
    return datetime.fromtimestamp(now, TIMEZONE).date().isoformat()

def item_snapshot(key, row=None):
    meta = ITEM_CATALOG.get(key, {'name': key, 'icon': '•', 'description': '', 'category': 'souvenir'})
    data = {'key': key, **meta}
    if row is not None:
        data['quantity'] = int(row['quantity'])
        data['first_obtained_at'] = row['first_obtained_at']
    return data

def decode_rewards(raw):
    try:
        rewards = json.loads(raw or '[]')
    except json.JSONDecodeError:
        return []
    if not isinstance(rewards, list):
        return []
    return [key for key in rewards if isinstance(key, str) and key in ITEM_CATALOG]

def describe_rewards(place_key, rewards):
    place = PLACES[place_key]
    names = []
    for key in rewards:
        names.append(place['gift'] if key == place['gift_key'] else ITEM_CATALOG[key]['name'])
    return '、'.join(names) if names else '一点旅行回忆'

def item_quantity(con, user_id, key):
    row = con.execute('SELECT quantity FROM inventory WHERE user_id=? AND item_key=?', (user_id, key)).fetchone()
    return int(row['quantity']) if row else 0

def grant_item(con, user_id, key, quantity, source_type, source_id, now=None):
    if key not in ITEM_CATALOG or quantity <= 0:
        return False
    now = now or time.time()
    inserted = con.execute(
        'INSERT OR IGNORE INTO item_grants(user_id,item_key,quantity,source_type,source_id,created_at) VALUES(?,?,?,?,?,?)',
        (user_id, key, quantity, source_type, str(source_id), now),
    ).rowcount
    if not inserted:
        return False
    con.execute(
        """INSERT INTO inventory(user_id,item_key,quantity,first_obtained_at) VALUES(?,?,?,?)
        ON CONFLICT(user_id,item_key) DO UPDATE SET quantity=inventory.quantity+excluded.quantity""",
        (user_id, key, quantity, now),
    )
    return True

def consume_item(con, user_id, key, quantity=1, message=None):
    item = ITEM_CATALOG[key]
    removed = con.execute(
        'UPDATE inventory SET quantity=quantity-? WHERE user_id=? AND item_key=? AND quantity>=?',
        (quantity, user_id, key, quantity),
    ).rowcount
    if not removed:
        raise HTTPException(409, message or item['name'] + '不够了，先去背包领取补给或换一种食物。')

def ensure_starter_items(con, user_id, pet_id, now=None):
    now = now or time.time()
    for key, quantity in STARTER_ITEMS.items():
        grant_item(con, user_id, key, quantity, 'starter', pet_id, now)
    con.execute('INSERT OR IGNORE INTO gardens(user_id) VALUES(?)', (user_id,))
    for plot in range(1, 4):
        con.execute('INSERT OR IGNORE INTO garden_plots(user_id,plot) VALUES(?,?)', (user_id, plot))

def garden_state(con, user_id, now):
    garden = con.execute('SELECT clovers FROM gardens WHERE user_id=?', (user_id,)).fetchone()
    if not garden:
        return None
    plots = [dict(row) for row in con.execute('SELECT plot,ready_at,cycle FROM garden_plots WHERE user_id=? ORDER BY plot', (user_id,))]
    for plot in plots:
        plot['status'] = 'empty' if plot['ready_at'] is None else 'ready' if plot['ready_at'] <= now else 'growing'
    return {'clovers': garden['clovers'], 'plots': plots, 'grow_seconds': GROW_SECONDS, 'harvest_amount': HARVEST_AMOUNT}

def rewards_from_gift(gift):
    gift = (gift or '').strip()
    if gift in GIFT_TO_ITEM:
        return [GIFT_TO_ITEM[gift]]
    return [key for label, key in GIFT_TO_ITEM.items() if label and label in gift]

def backfill_card_rewards(con, user_id, now=None):
    now = now or time.time()
    for card in con.execute('SELECT id,gift,rewards,created_at FROM cards WHERE user_id=?', (user_id,)).fetchall():
        rewards = decode_rewards(card['rewards'])
        if not rewards:
            rewards = rewards_from_gift(card['gift'])
            if rewards:
                con.execute('UPDATE cards SET rewards=? WHERE id=?', (json.dumps(rewards, ensure_ascii=False), card['id']))
        for key in rewards:
            grant_item(con, user_id, key, 1, 'card', card['id'], card['created_at'] or now)

def inventory_state(con, user_id, now):
    rows = {row['item_key']: row for row in con.execute('SELECT * FROM inventory WHERE user_id=?', (user_id,)).fetchall()}
    today = local_day(now)
    daily_claimed = con.execute('SELECT 1 FROM daily_claims WHERE user_id=? AND claim_date=?', (user_id, today)).fetchone()
    def build(keys):
        return [item_snapshot(key, rows.get(key, {'quantity': 0, 'first_obtained_at': None})) for key in keys]
    return {
        'foods': build(FOODS.keys()),
        'tools': build(TOOLS.keys()),
        'souvenirs': build(SOUVENIRS.keys()),
        'daily': {
            'date': today,
            'available': daily_claimed is None,
            'item': item_snapshot('rice_ball'),
        },
    }

def create_card(con, user_id, trip_id, encounter_id, place_key, animal, name, message, gift, created_at, participants='[]', rewards=None, variant='standard', combination=None):
    rewards = rewards or []
    if encounter_id is None:
        inserted = con.execute(
            'INSERT OR IGNORE INTO cards(user_id,trip_id,place,animal,name,message,gift,created_at,rewards,variant) VALUES(?,?,?,?,?,?,?,?,?,?)',
            (user_id, trip_id, place_key, animal, name, message, gift, created_at, json.dumps(rewards, ensure_ascii=False), variant),
        ).rowcount
        card = con.execute('SELECT id FROM cards WHERE trip_id=? AND encounter_id IS NULL', (trip_id,)).fetchone()
    else:
        inserted = con.execute(
            'INSERT OR IGNORE INTO cards(user_id,trip_id,encounter_id,place,animal,name,message,gift,created_at,participants,rewards,variant) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
            (user_id, trip_id, encounter_id, place_key, animal, name, message, gift, created_at, participants, json.dumps(rewards, ensure_ascii=False), variant),
        ).rowcount
        card = con.execute('SELECT id FROM cards WHERE user_id=? AND encounter_id=?', (user_id, encounter_id)).fetchone()
    if inserted and card:
        title = combination['title'] if combination else ('同行 · ' if encounter_id else '特别风景 · ' if variant == 'special' else '远方来信 · ') + PLACES[place_key]['name']
        template_key = 'combo:' + combination['key'] if combination else place_key + ':' + variant
        con.execute('UPDATE cards SET title=?,template_key=?,combination=? WHERE id=?', (title, template_key, json.dumps(combination or {}, ensure_ascii=False), card['id']))
        for key in rewards:
            grant_item(con, user_id, key, 1, 'card', card['id'], created_at)

def migrate_legacy(con, uid):
    animal = con.execute('SELECT * FROM animal').fetchone()
    pid = con.execute('INSERT INTO pets(user_id,kind,name) VALUES(?,?,?)', (uid,animal['kind'],animal['name'])).lastrowid
    ensure_starter_items(con, uid, pid)
    for trip in con.execute('SELECT * FROM travel').fetchall():
        tid = con.execute('INSERT INTO trips(pet_id,place,started_at,ends_at,settled) VALUES(?,?,?,?,?)',(pid,trip['place'],trip['started_at'],trip['ends_at'],trip['settled'])).lastrowid
        for card in con.execute('SELECT * FROM postcard WHERE travel_id=?',(trip['id'],)).fetchall():
            con.execute('INSERT INTO cards(user_id,trip_id,place,animal,name,message,gift,created_at,opened) VALUES(?,?,?,?,?,?,?,?,?)',(uid,tid,card['place'],card['animal'],card['name'],card['message'],card['gift'],card['created_at'],card['opened']))
    con.execute("INSERT OR REPLACE INTO settings VALUES('legacy_owner',?)",(str(uid),))

def rate_limit(request):
    address = request.client.host if request.client else 'unknown'
    now = time.time()
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        con.execute('DELETE FROM auth_attempts WHERE started_at<?',(now-900,))
        entry = con.execute('SELECT count FROM auth_attempts WHERE address=?',(address,)).fetchone()
        if entry and entry['count'] >= 30:
            raise HTTPException(429,'尝试次数较多，请 15 分钟后再试。')
        con.execute('INSERT INTO auth_attempts VALUES(?,1,?) ON CONFLICT(address) DO UPDATE SET count=count+1',(address,now))

def login_session(con, uid, response):
    token = secrets.token_urlsafe(32)
    con.execute('DELETE FROM sessions WHERE expires_at<=?',(time.time(),))
    con.execute('INSERT INTO sessions VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),uid,time.time()+SESSION_SECONDS))
    response.set_cookie('journey_session',token,max_age=SESSION_SECONDS,httponly=True,samesite='lax',secure=os.environ.get('JOURNEY_SECURE_COOKIE')=='1')

@app.post('/api/register', status_code=201)
def register(body: Credentials, request: Request, response: Response):
    rate_limit(request)
    username = body.username.strip()
    if not username or any(not (c.isalnum() or c in '_-') for c in username):
        raise HTTPException(422,'用户名请使用汉字、字母、数字、下划线或短横线。')
    hashed = password_hash(body.password)
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        if con.execute('SELECT COUNT(*) FROM users').fetchone()[0] >= 15:
            raise HTTPException(403,'这个小世界的 15 个位置已经住满了。')
        available = legacy_available(con)
        if available and not body.claim_legacy:
            raise HTTPException(409,'请先确认将旧小屋与旅行回忆保存到你的账号。')
        try:
            uid = con.execute('INSERT INTO users(username,password_hash,created_at) VALUES(?,?,?)',(username,hashed,time.time())).lastrowid
        except sqlite3.IntegrityError:
            raise HTTPException(409,'这个用户名已经有人使用了。')
        if available:
            migrate_legacy(con,uid)
        login_session(con,uid,response)
    return {'ok':True}

@app.post('/api/login')
def login(body: Credentials, request: Request, response: Response):
    rate_limit(request)
    with database() as con:
        user = con.execute('SELECT * FROM users WHERE username=?',(body.username.strip(),)).fetchone()
        stored = user['password_hash'] if user else '0'*32 + ':' + '0'*64
        if not hmac.compare_digest(password_hash(body.password,stored.split(':')[0]),stored):
            raise HTTPException(401,'用户名或密码不正确。')
        login_session(con,user['id'],response)
    return {'ok':True}

@app.post('/api/logout')
def logout(request: Request, response: Response):
    with database() as con:
        con.execute('DELETE FROM sessions WHERE token=?',(hashlib.sha256(request.cookies.get('journey_session','').encode()).hexdigest(),))
    response.delete_cookie('journey_session')
    return {'ok':True}

def settle(con, now):
    for trip in con.execute('SELECT t.*,p.user_id,p.kind,p.name FROM trips t JOIN pets p ON p.id=t.pet_id WHERE settled=0 AND ends_at<=?',(now,)).fetchall():
        place = PLACES[trip['place']]
        tool = TOOLS.get(trip['tool_key'] or '')
        variant = 'special' if tool and tool.get('effect') == 'special' and random.random() < 0.5 else 'standard'
        rewards = [place['gift_key']]
        if tool and tool.get('effect') == 'extra' and random.random() < 0.5:
            rewards.append(place['extra_gift_key'])
        lines = place['special_lines'] if variant == 'special' else place['lines']
        message = random.choice(lines)
        combination = json.loads(trip['combination']) or None
        if combination:
            rewards.append(combination['reward'])
            message = combination['message']
            variant = 'combination'
        weather = json.loads(trip['weather'])
        if weather:
            memory = weather['memory']
            if trip['place'] == 'library':
                memory = '窗外下着小雨，书页和雨声刚好作伴。' if weather['key'] == 'rainy' else '隔着窗看了一会儿天色，又轻轻翻过一页书。'
            message += memory
            if trip['food_key'] == 'hot_tea' and weather['key'] in ('rainy', 'windy'):
                message += '带来的热茶，刚好暖了暖手心。'
        create_card(
            con, trip['user_id'], trip['id'], None, trip['place'], trip['kind'], trip['name'],
            message, describe_rewards(trip['place'], rewards), trip['ends_at'], rewards=rewards, variant=variant, combination=combination,
        )
        for encounter in con.execute('SELECT * FROM encounters WHERE trip_a=? OR trip_b=?',(trip['id'],trip['id'])).fetchall():
            create_card(
                con, trip['user_id'], trip['id'], encounter['id'], trip['place'], trip['kind'], trip['name'],
                encounter['message'], '一枚同行纪念章', trip['ends_at'], encounter['participants'], ['travel_badge'], 'encounter',
            )
        con.execute('UPDATE trips SET settled=1 WHERE id=?',(trip['id'],))

def as_card(row):
    result=dict(row)
    result['weather']=json.loads(result.get('weather', '{}')) or None
    result.pop('combination', None)
    result['participants']=json.loads(result['participants'])
    result['rewards']=[item_snapshot(key) for key in decode_rewards(result['rewards'])]
    return result

def as_trip(row, now):
    result = dict(row)
    result.pop('place', None)
    result['weather'] = json.loads(result['weather']) or None
    result.pop('combination', None)
    result['food'] = item_snapshot(result['food_key']) if result.get('food_key') else None
    result['tool'] = item_snapshot(result['tool_key']) if result.get('tool_key') else None
    note = result.pop('trail_note', '')
    note_at = result.pop('note_at', None)
    result['note'] = {'message': note, 'created_at': note_at} if note and note_at is not None and now >= note_at else None
    return result

def journey_diary(con, user_id, now):
    rows = con.execute('SELECT t.*,p.name FROM trips t JOIN pets p ON p.id=t.pet_id WHERE p.user_id=? ORDER BY t.started_at DESC,t.id DESC', (user_id,)).fetchall()
    cards = con.execute('SELECT id,trip_id,encounter_id,message FROM cards WHERE user_id=? ORDER BY id', (user_id,)).fetchall()
    by_trip = {}
    for card in cards:
        by_trip.setdefault(card['trip_id'], []).append(dict(card))
    entries = []
    for row in rows:
        entry = as_trip(row, now)
        entry['place'] = row['place'] if row['settled'] else None
        entry['cards'] = by_trip.get(row['id'], [])
        entries.append(entry)
    return entries

def as_gift(row, user_id):
    result = dict(row)
    result['item'] = item_snapshot(result.pop('item_key'))
    result['direction'] = 'sent' if result['from_user_id'] == user_id else 'received'
    return result

@app.get('/api/state')
def state(request: Request):
    now=time.time()
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        user=identity(con,request,False)
        base={'user':dict(user) if user else None,'server_time':now,'duration':DURATION,'legacy_available':legacy_available(con),'weather':world_weather(now), 'catalog': {'places': {key: {field: place[field] for field in ('name', 'icon', 'tag', 'description')} for key, place in PLACES.items()}}, 'garden': None}
        if not user:
            return {**base,'animal':None,'travel':None,'postcards':[],'friends':[],'events':[],'gifts':[],'inventory':None,'diary':[],'arrival':None}
        settle(con,now)
        pet=con.execute('SELECT * FROM pets WHERE user_id=?',(user['id'],)).fetchone()
        if pet:
            ensure_starter_items(con, user['id'], pet['id'], now)
            base['garden'] = garden_state(con, user['id'], now)
        backfill_card_rewards(con, user['id'], now)
        trip=con.execute('SELECT * FROM trips WHERE pet_id=? AND settled=0',(pet['id'],)).fetchone() if pet else None
        cards=con.execute('SELECT c.*,t.weather FROM cards c JOIN trips t ON t.id=c.trip_id WHERE c.user_id=? ORDER BY c.created_at DESC,c.id DESC',(user['id'],)).fetchall()
        diary = journey_diary(con, user['id'], now)
        arrival = next((entry for entry in reversed(diary) if entry['settled'] and not entry['unpacked']), None)
        friends=con.execute('SELECT p.name,p.kind,u.username,(t.id IS NOT NULL) AS traveling,t.ends_at FROM pets p JOIN users u ON u.id=p.user_id LEFT JOIN trips t ON t.pet_id=p.id AND t.settled=0 WHERE p.user_id!=? ORDER BY p.id',(user['id'],)).fetchall()
        events=con.execute('SELECT e.id,e.message,e.created_at FROM events e WHERE e.encounter_id IS NULL OR EXISTS (SELECT 1 FROM encounters x JOIN trips a ON a.id=x.trip_a JOIN trips b ON b.id=x.trip_b WHERE x.id=e.encounter_id AND a.settled=1 AND b.settled=1) ORDER BY e.id DESC LIMIT 30').fetchall()
        gifts=con.execute(
            """SELECT g.*,fu.username AS from_username,tu.username AS to_username,fp.name AS from_pet,tp.name AS to_pet
            FROM gifts g
            JOIN users fu ON fu.id=g.from_user_id JOIN users tu ON tu.id=g.to_user_id
            LEFT JOIN pets fp ON fp.user_id=g.from_user_id LEFT JOIN pets tp ON tp.user_id=g.to_user_id
            WHERE g.from_user_id=? OR g.to_user_id=?
            ORDER BY g.id DESC LIMIT 30""",
            (user['id'], user['id']),
        ).fetchall()
        return {**base,'animal':dict(pet) if pet else None,'travel':as_trip(trip,now) if trip else None,'postcards':[as_card(c) for c in cards],'friends':[dict(f) for f in friends],'events':[dict(e) for e in events],'gifts':[as_gift(g,user['id']) for g in gifts],'inventory':inventory_state(con,user['id'],now) if pet else None,'diary':diary,'arrival':arrival}

@app.post('/api/animal',status_code=201)
def create_animal(body: AnimalInput,request: Request):
    name=body.name.strip()
    if body.kind not in ANIMALS or not name:
        raise HTTPException(422,'请选择动物，并填写名字。')
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        user=identity(con,request)
        if con.execute('SELECT 1 FROM pets WHERE user_id=?',(user['id'],)).fetchone():
            raise HTTPException(409,'小屋已经有主人了，请刷新页面。')
        pid = con.execute('INSERT INTO pets(user_id,kind,name) VALUES(?,?,?)',(user['id'],body.kind,name)).lastrowid
        ensure_starter_items(con, user['id'], pid)
    return {'ok':True}

@app.post('/api/travel',status_code=201)
def depart(body: TravelInput,request: Request):
    food_key = body.food.strip() if body.food else ''
    tool_key = body.tool.strip() if body.tool else None
    if food_key not in FOODS:
        raise HTTPException(422,'请选择一种可以带上路的食物。')
    if tool_key and tool_key not in TOOLS:
        raise HTTPException(422,'请选择背包里已有的旅行工具。')
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        user=identity(con,request)
        now=time.time()
        settle(con,now)
        pet=con.execute('SELECT * FROM pets WHERE user_id=?',(user['id'],)).fetchone()
        if not pet:
            raise HTTPException(409,'请先选择你的小动物。')
        ensure_starter_items(con, user['id'], pet['id'], now)
        if con.execute('SELECT 1 FROM trips WHERE pet_id=? AND settled=0',(pet['id'],)).fetchone():
            raise HTTPException(409,'小动物还在旅行中。')
        consume_item(con, user['id'], food_key)
        if tool_key and item_quantity(con, user['id'], tool_key) < 1:
            raise HTTPException(409,'背包里还没有' + TOOLS[tool_key]['name'] + '。')
        place_key = choose_destination(food_key, tool_key)
        duration_label, multiplier = random.choice(TRIP_LENGTHS)
        ends_at = now + DURATION * multiplier
        trail_note = random.choice(TRAIL_NOTES) if random.random() < .65 else ''
        peers=con.execute('SELECT t.id,p.kind,p.name,u.username FROM trips t JOIN pets p ON p.id=t.pet_id JOIN users u ON u.id=p.user_id WHERE t.place=? AND t.ends_at>? AND t.started_at<? AND t.pet_id!=?',(place_key,now,ends_at,pet['id'])).fetchall()
        combination = match_combination(place_key, food_key, tool_key)
        tid=con.execute('INSERT INTO trips(pet_id,place,started_at,ends_at,food_key,tool_key,weather,combination,duration_label,trail_note,note_at,unpacked) VALUES(?,?,?,?,?,?,?,?,?,?,?,0)',(pet['id'],place_key,now,ends_at,food_key,tool_key,json.dumps(world_weather(now), ensure_ascii=False),json.dumps(combination or {}, ensure_ascii=False),duration_label,trail_note,now+(ends_at-now)/2 if trail_note else None)).lastrowid
        con.execute('INSERT INTO events(message,created_at) VALUES(?,?)',(user['username']+'的'+pet['name']+'出发去旅行了。',now))
        for peer in peers:
            participants=json.dumps([{'name':peer['name'],'kind':peer['kind'],'username':peer['username']},{'name':pet['name'],'kind':pet['kind'],'username':user['username']}],ensure_ascii=False)
            message=peer['username']+'的'+peer['name']+'和'+user['username']+'的'+pet['name']+'在'+PLACES[place_key]['name']+'相遇，一起分享了'+FOODS[food_key]['name']+'。'
            encounter_id = con.execute('INSERT INTO encounters(trip_a,trip_b,place,participants,message,occurred_at) VALUES(?,?,?,?,?,?)',(peer['id'],tid,place_key,participants,message,now)).lastrowid
            con.execute('INSERT INTO events(message,created_at,encounter_id) VALUES(?,?,?)',(message,now,encounter_id))
    return {'ok':True}

@app.post('/api/trips/{trip_id}/unpack')
def unpack(trip_id: int, request: Request):
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        user = identity(con, request)
        settle(con, time.time())
        trip = con.execute('SELECT t.* FROM trips t JOIN pets p ON p.id=t.pet_id WHERE t.id=? AND p.user_id=?', (trip_id, user['id'])).fetchone()
        if not trip:
            raise HTTPException(404, '没有找到这次旅行。')
        if not trip['settled']:
            raise HTTPException(409, '小动物还没回来，行李也在路上。')
        con.execute('UPDATE trips SET unpacked=1 WHERE id=?', (trip_id,))
        con.execute('UPDATE cards SET opened=1 WHERE trip_id=? AND user_id=?', (trip_id,user['id']))
        cards = con.execute('SELECT c.*,t.weather FROM cards c JOIN trips t ON t.id=c.trip_id WHERE c.trip_id=? AND c.user_id=? ORDER BY c.id', (trip_id,user['id'])).fetchall()
        return {'place':trip['place'], 'postcards':[as_card(card) for card in cards]}

@app.post('/api/inventory/daily')
def claim_daily(request: Request):
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        user = identity(con, request)
        now = time.time()
        today = local_day(now)
        inserted = con.execute(
            'INSERT OR IGNORE INTO daily_claims(user_id,claim_date,created_at) VALUES(?,?,?)',
            (user['id'], today, now),
        ).rowcount
        if not inserted:
            raise HTTPException(409, '今天的饭团已经领过了，明天再来看看。')
        grant_item(con, user['id'], 'rice_ball', 1, 'daily', today, now)
    return {'ok': True}

def require_garden(con, request):
    user = identity(con, request)
    pet = con.execute('SELECT id FROM pets WHERE user_id=?', (user['id'],)).fetchone()
    if not pet:
        raise HTTPException(409, '先领养小动物，再一起照料草圃吧。')
    ensure_starter_items(con, user['id'], pet['id'])
    return user['id']

@app.post('/api/garden/{plot}/plant')
def plant(plot: int, request: Request):
    if plot not in range(1, 4):
        raise HTTPException(422, '请选择一块草圃。')
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        uid = require_garden(con, request)
        if not con.execute('UPDATE garden_plots SET ready_at=?,cycle=cycle+1 WHERE user_id=? AND plot=? AND ready_at IS NULL', (time.time() + GROW_SECONDS, uid, plot)).rowcount:
            raise HTTPException(409, '这块地已经种好了，等收获后再播种。')
    return {'ok': True}

@app.post('/api/garden/{plot}/harvest')
def harvest(plot: int, request: Request):
    if plot not in range(1, 4):
        raise HTTPException(422, '请选择一块草圃。')
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        uid = require_garden(con, request)
        if not con.execute('UPDATE garden_plots SET ready_at=NULL WHERE user_id=? AND plot=? AND ready_at<=?', (uid, plot, time.time())).rowcount:
            raise HTTPException(409, '这块地还没有成熟的三叶草。')
        con.execute('UPDATE gardens SET clovers=clovers+? WHERE user_id=?', (HARVEST_AMOUNT, uid))
    return {'ok': True, 'clovers': HARVEST_AMOUNT}

@app.post('/api/shop/buy')
def buy_food(body: ShopInput, request: Request):
    if body.item not in FOODS:
        raise HTTPException(422, '小铺里暂时没有这种食物。')
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        uid = require_garden(con, request)
        prior = con.execute('SELECT item_key FROM shop_orders WHERE user_id=? AND request_id=?', (uid, body.request_id)).fetchone()
        if prior:
            if prior['item_key'] != body.item:
                raise HTTPException(409, '这次兑换已经用于另一种食物，请刷新后重试。')
            return {'ok': True}
        price = FOODS[body.item]['price']
        if not con.execute('UPDATE gardens SET clovers=clovers-? WHERE user_id=? AND clovers>=?', (price, uid, price)).rowcount:
            raise HTTPException(409, '三叶草不够了，去草圃收获一些再来吧。')
        now = time.time()
        con.execute('INSERT INTO shop_orders VALUES(?,?,?,?,?)', (uid, body.request_id, body.item, price, now))
        grant_item(con, uid, body.item, 1, 'shop', body.request_id, now)
    return {'ok': True}

@app.post('/api/gifts', status_code=201)
def send_gift(body: GiftInput, request: Request):
    item_key = body.item.strip()
    to_username = body.to_username.strip()
    if item_key not in SOUVENIRS:
        raise HTTPException(422, '现在只能赠送旅行带回的纪念品。')
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        user = identity(con, request)
        sender_pet = con.execute('SELECT * FROM pets WHERE user_id=?', (user['id'],)).fetchone()
        if not sender_pet:
            raise HTTPException(409, '请先选择你的小动物。')
        receiver = con.execute(
            'SELECT u.id,u.username,p.name AS pet_name FROM users u LEFT JOIN pets p ON p.user_id=u.id WHERE u.username=?',
            (to_username,),
        ).fetchone()
        if not receiver:
            raise HTTPException(404, '没有找到这位朋友。')
        if receiver['id'] == user['id']:
            raise HTTPException(409, '礼物要留给朋友的小动物。')
        if not receiver['pet_name']:
            raise HTTPException(409, '这位朋友还没有小动物。')
        consume_item(con, user['id'], item_key, message='背包里还没有可送出的' + ITEM_CATALOG[item_key]['name'] + '。')
        now = time.time()
        item_name = ITEM_CATALOG[item_key]['name']
        message = user['username'] + '的' + sender_pet['name'] + '给' + receiver['username'] + '的' + receiver['pet_name'] + '留下了' + item_name + '。'
        gift_id = con.execute(
            'INSERT INTO gifts(from_user_id,to_user_id,item_key,message,created_at) VALUES(?,?,?,?,?)',
            (user['id'], receiver['id'], item_key, message, now),
        ).lastrowid
        grant_item(con, receiver['id'], item_key, 1, 'gift', gift_id, now)
        con.execute('INSERT INTO events(message,created_at) VALUES(?,?)', (message, now))
    return {'ok': True}

@app.post('/api/postcards/{card_id}/open')
def open_card(card_id:int,request:Request):
    with database() as con:
        user=identity(con,request)
        if not con.execute('UPDATE cards SET opened=1 WHERE id=? AND user_id=?',(card_id,user['id'])).rowcount:
            raise HTTPException(404,'没有找到这张明信片。')
    return {'ok':True}

if (ROOT/'dist').exists():
    app.mount('/',StaticFiles(directory=ROOT/'dist',html=True),name='frontend')
