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
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent
DB = Path(os.environ.get('JOURNEY_DB', ROOT / 'data/journey.sqlite3'))
DB.parent.mkdir(parents=True, exist_ok=True)
DURATION = max(1, int(os.environ.get('JOURNEY_DURATION_SECONDS', '60')))
SESSION_SECONDS = 30 * 86400
ANIMALS = ['frog', 'cat', 'fox', 'rabbit', 'squirrel']
PLACES = {
    'forest': {'name': '微风森林', 'gift': '一枚松果', 'lines': ['树叶沙沙响，像是在说欢迎你。', '在树荫下吃完饭团，又听了一会儿风。', '沿着苔藓小路，发现了一片心形的叶子。']},
    'sea': {'name': '日落海岸', 'gift': '一枚贝壳', 'lines': ['把烦恼留给海风，把贝壳带回来给你。', '今天的浪花，一朵比一朵温柔。', '等到太阳落进海里，才舍得往回走。']},
    'mountain': {'name': '星星山谷', 'gift': '一颗小石子', 'lines': ['山里的风很轻，星星离我很近。', '在山坡上坐了一会儿，云慢慢走过。', '带回一颗小石子，也带回一点勇气。']},
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
    CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, message TEXT NOT NULL, created_at REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS auth_attempts(address TEXT PRIMARY KEY, count INTEGER NOT NULL, started_at REAL NOT NULL);
    """)

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
    place: str

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

def migrate_legacy(con, uid):
    animal = con.execute('SELECT * FROM animal').fetchone()
    pid = con.execute('INSERT INTO pets(user_id,kind,name) VALUES(?,?,?)', (uid,animal['kind'],animal['name'])).lastrowid
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
        con.execute('INSERT OR IGNORE INTO cards(user_id,trip_id,place,animal,name,message,gift,created_at) VALUES(?,?,?,?,?,?,?,?)',(trip['user_id'],trip['id'],trip['place'],trip['kind'],trip['name'],random.choice(place['lines']),place['gift'],trip['ends_at']))
        for encounter in con.execute('SELECT * FROM encounters WHERE trip_a=? OR trip_b=?',(trip['id'],trip['id'])).fetchall():
            con.execute('INSERT OR IGNORE INTO cards(user_id,trip_id,encounter_id,place,animal,name,message,gift,created_at,participants) VALUES(?,?,?,?,?,?,?,?,?,?)',(trip['user_id'],trip['id'],encounter['id'],trip['place'],trip['kind'],trip['name'],encounter['message'],'一枚同行纪念章',trip['ends_at'],encounter['participants']))
        con.execute('UPDATE trips SET settled=1 WHERE id=?',(trip['id'],))

def as_card(row):
    result=dict(row)
    result['participants']=json.loads(result['participants'])
    return result

@app.get('/api/state')
def state(request: Request):
    now=time.time()
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        user=identity(con,request,False)
        base={'user':dict(user) if user else None,'server_time':now,'duration':DURATION,'legacy_available':legacy_available(con)}
        if not user:
            return {**base,'animal':None,'travel':None,'postcards':[],'friends':[],'events':[]}
        settle(con,now)
        pet=con.execute('SELECT * FROM pets WHERE user_id=?',(user['id'],)).fetchone()
        trip=con.execute('SELECT * FROM trips WHERE pet_id=? AND settled=0',(pet['id'],)).fetchone() if pet else None
        cards=con.execute('SELECT * FROM cards WHERE user_id=? ORDER BY created_at DESC,id DESC',(user['id'],)).fetchall()
        friends=con.execute('SELECT p.name,p.kind,u.username,t.place,t.ends_at FROM pets p JOIN users u ON u.id=p.user_id LEFT JOIN trips t ON t.pet_id=p.id AND t.settled=0 WHERE p.user_id!=? ORDER BY p.id',(user['id'],)).fetchall()
        events=con.execute('SELECT * FROM events ORDER BY id DESC LIMIT 30').fetchall()
        return {**base,'animal':dict(pet) if pet else None,'travel':dict(trip) if trip else None,'postcards':[as_card(c) for c in cards],'friends':[dict(f) for f in friends],'events':[dict(e) for e in events]}

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
        con.execute('INSERT INTO pets(user_id,kind,name) VALUES(?,?,?)',(user['id'],body.kind,name))
    return {'ok':True}

@app.post('/api/travel',status_code=201)
def depart(body: TravelInput,request: Request):
    if body.place not in PLACES:
        raise HTTPException(422,'这个目的地还没有开放。')
    with database() as con:
        con.execute('BEGIN IMMEDIATE')
        user=identity(con,request)
        now=time.time()
        settle(con,now)
        pet=con.execute('SELECT * FROM pets WHERE user_id=?',(user['id'],)).fetchone()
        if not pet:
            raise HTTPException(409,'请先选择你的小动物。')
        if con.execute('SELECT 1 FROM trips WHERE pet_id=? AND settled=0',(pet['id'],)).fetchone():
            raise HTTPException(409,'小动物还在旅行中。')
        peers=con.execute('SELECT t.id,p.kind,p.name,u.username FROM trips t JOIN pets p ON p.id=t.pet_id JOIN users u ON u.id=p.user_id WHERE t.place=? AND t.ends_at>? AND t.started_at<? AND t.pet_id!=?',(body.place,now,now+DURATION,pet['id'])).fetchall()
        tid=con.execute('INSERT INTO trips(pet_id,place,started_at,ends_at) VALUES(?,?,?,?)',(pet['id'],body.place,now,now+DURATION)).lastrowid
        con.execute('INSERT INTO events(message,created_at) VALUES(?,?)',(user['username']+'的'+pet['name']+'去了'+PLACES[body.place]['name']+'。',now))
        for peer in peers:
            participants=json.dumps([{'name':peer['name'],'kind':peer['kind'],'username':peer['username']},{'name':pet['name'],'kind':pet['kind'],'username':user['username']}],ensure_ascii=False)
            message=peer['username']+'的'+peer['name']+'和'+user['username']+'的'+pet['name']+'在'+PLACES[body.place]['name']+'相遇，一起分享了饭团。'
            con.execute('INSERT INTO encounters(trip_a,trip_b,place,participants,message,occurred_at) VALUES(?,?,?,?,?,?)',(peer['id'],tid,body.place,participants,message,now))
            con.execute('INSERT INTO events(message,created_at) VALUES(?,?)',(message,now))
    return {'ok':True}

@app.post('/api/postcards/{card_id}/open')
def open_card(card_id:int,request:Request):
    with database() as con:
        user=identity(con,request)
        if not con.execute('UPDATE cards SET opened=1 WHERE id=? AND user_id=?',(card_id,user['id'])).rowcount:
            raise HTTPException(404,'没有找到这张明信片。')
    return {'ok':True}

if (ROOT/'dist').exists():
    app.mount('/',StaticFiles(directory=ROOT/'dist',html=True),name='frontend')
