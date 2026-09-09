import { createApp } from 'vue/dist/vue.esm-bundler.js';
import './style.css';
import './content.css';
import JourneyScene from './JourneyScene.js';
import GardenShop from './GardenShop.js';
import BackpackDialog from './BackpackDialog.js';
import JourneyDiary from './JourneyDiary.js';
import IndoorScene from './IndoorScene.js';
import PackingBag from './PackingBag.js';
import './home-layout.css';
import './storybook.css';
import TravelArt from './TravelArt.js';
import './travel-art.css';

createApp({
  components: { TravelArt, JourneyScene, GardenShop, BackpackDialog, JourneyDiary, IndoorScene, PackingBag },
  data: () => ({ shopOpen: false, shopFromPacking: false, room: false, bagQuery: '', souvenirQuery: '', cardQuery: '', cardPlace: '', cardPage: 1, leavingUntil: 0, arrivalReveal: null, bagCategory: 'foods', packingOpen: false, backpackOpen: false, shopRequests: {}, notice: '', username: '', password: '', authMode: 'login', claimLegacy: false, tick: 0, state: null, page: 'home', kind: 'frog', name: '', food: 'rice_ball', tool: '', charm: '', giftTo: '', giftItem: '', busy: false, error: '', selected: null, now: Date.now()/1000, offset: 0, timer: null, polling: false, refreshTask: null,
    animals: {frog:'🐸',cat:'🐱',fox:'🦊',rabbit:'🐰',squirrel:'🐿️'}, labels:{frog:'青蛙',cat:'小猫',fox:'狐狸',rabbit:'兔子',squirrel:'松鼠'},
  }),
  computed: {
    bagItems(){return this.inventory[this.bagCategory].filter(i=>i.name.includes(this.bagQuery.trim()));},
    souvenirItems(){return this.inventory.souvenirs.filter(i=>i.name.includes(this.souvenirQuery.trim()));},
    matchingCards(){const q=this.cardQuery.trim();return this.cards.filter(c=>(!this.cardPlace||c.place===this.cardPlace)&&(!q||(c.title+' '+c.message+' '+this.places[c.place].name).includes(q)));},
    cardPages(){return Math.max(1,Math.ceil(this.matchingCards.length/12));},
    visibleCards(){return this.matchingCards.slice((this.cardPage-1)*12,this.cardPage*12);},
    visitedPlaces(){return [...new Set(this.cards.map(c=>c.place))];},
    places(){return this.state?.catalog?.places || {};},
    garden(){return this.state?.garden;},
    gardenReady(){return this.garden?.plots.filter(p=>p.ready_at!==null&&p.ready_at<=this.now).length || 0;},
    arrival(){return this.state?.arrival;},
    animal(){ return this.state?.animal; },
    trip(){return this.state?.travel;},
    cards(){return this.state?.postcards || [];},
    unread(){return this.cards.filter(c=>!c.opened);},
    inventory(){return this.state?.inventory || {foods:[],tools:[],charms:[],souvenirs:[],daily:{available:false,item:{}}};},
    gifts(){return this.state?.gifts || [];},
    giftableSouvenirs(){return this.inventory.souvenirs.filter(item=>item.quantity>0);},
    selectedFood(){return this.inventory.foods.find(item=>item.key===this.food && item.quantity>0);},
    foodCount(){return this.inventory.foods.reduce((sum,item)=>sum+item.quantity,0);},
    canDepart(){return !this.busy && !this.trip && !!this.selectedFood && this.selectedFood.quantity>0;},
    canGift(){return !this.busy && !!this.giftTo && !!this.giftItem && this.giftableSouvenirs.some(item=>item.key===this.giftItem);},
    remaining(){return Math.max(0, Math.ceil((this.trip?.ends_at || 0)-this.now));},
    progress(){return this.trip ? Math.min(100,Math.max(0,(this.now-this.trip.started_at)/(this.trip.ends_at-this.trip.started_at)*100)):0;}
  },
  watch: { bagCategory(){this.bagQuery='';},cardQuery(){this.cardPage=1;},cardPlace(){this.cardPage=1;},cardPages(n){this.cardPage=Math.min(this.cardPage,n);}, 'state.user'(user){if(!user){this.shopOpen=false;this.shopFromPacking=false;this.room=false;this.backpackOpen=false;this.packingOpen=false;this.arrivalReveal=null;}} },
  methods: {
    openPacking(){this.packingOpen=true;},
    openShop(){this.shopFromPacking=this.packingOpen;this.packingOpen=false;this.notice='';this.$nextTick(()=>this.shopOpen=true);},
    closeShop(){this.shopOpen=false;if(this.shopFromPacking)this.$nextTick(()=>this.packingOpen=true);this.shopFromPacking=false;},
    setRoom(value){this.room=value;this.$nextTick(()=>{if(value)this.$refs.indoors?.focusEntry();else this.$refs.yard?.$el.querySelector('.yard-door')?.focus({preventScroll:true});});},
    navigate(page){if(page==='shop'){this.openShop();}else if(page==='indoors'){this.setRoom(true);}else if(page==='backpack')this.backpackOpen=true;else if(page==='prepare')this.openPacking();else this.page=page;},
    async api(path, body){
      const response = await fetch('/api'+path, body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      if(response.status===401 && path!=='/login'){this.selected=null;this.state=null; await this.refresh();}
      if(!response.ok){const e=await response.json().catch(()=>({}));throw new Error(typeof e.detail==='string'?e.detail:'操作没有完成，请稍后重试。');}
      return response.json();
    },
    async refresh(){
      if(this.refreshTask)return this.refreshTask;
      this.polling=true;
      this.refreshTask=(async()=>{
        try{this.state=await this.api('/state');this.offset=this.state.server_time-Date.now()/1000;this.now=this.state.server_time;this.error='';this.syncPacking();}
        catch(e){this.error='暂时连接不上小屋，请检查服务是否启动，再点击重试。';}
      })();
      try{await this.refreshTask;}finally{this.polling=false;this.refreshTask=null;}
    },
    async act(path,body,after){
      if(this.busy)return;
      this.busy=true;this.error='';
      try{if(this.refreshTask)await this.refreshTask;const result=await this.api(path,body);await this.refresh();after?.(result);}
      catch(e){this.error=e.message;}finally{this.busy=false;}
    },
    authenticate(){this.act('/'+(this.authMode==='login'?'login':'register'),{username:this.username,password:this.password,claim_legacy:this.claimLegacy},()=>{this.password='';this.page='home';});},
    logout(){this.act('/logout',{},()=>{this.selected=null;this.password='';this.page='home';});},
    clock(t){return new Date(t*1000).toLocaleString('zh-CN',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'});},
    adopt(){this.act('/animal',{kind:this.kind,name:this.name});},
    syncPacking(){const foods=this.state?.inventory?.foods || [];if(this.food&&!foods.some(item=>item.key===this.food&&item.quantity>0))this.food='';const tools=this.state?.inventory?.tools || [];if(this.tool&&!tools.find(item=>item.key===this.tool&&item.quantity>0))this.tool='';if(this.charm&&!this.inventory.charms.some(i=>i.key===this.charm&&i.quantity>0))this.charm='';const friends=this.state?.friends || [];if(this.giftTo&&!friends.find(friend=>friend.username===this.giftTo))this.giftTo='';if(!this.giftTo&&friends.length)this.giftTo=friends[0].username;const gift=this.giftableSouvenirs.find(item=>item.key===this.giftItem) || this.giftableSouvenirs[0];this.giftItem=gift?.key || '';},
    depart(){if(!this.canDepart)return;this.act('/travel',{food:this.food,tool:this.tool||null,charm:this.charm||null},()=>{this.packingOpen=false;this.page='home';this.room=false;this.leavingUntil=this.now+2.5;});},
    claimDaily(){this.act('/inventory/daily',{},()=>{if(this.backpackOpen)this.$nextTick(()=>this.$refs.bagFoodTab?.focus({preventScroll:true}));});},
    plant(plot){this.act('/garden/'+plot+'/plant',{},()=>{this.$refs.yard?.react('garden','种好了！三叶草会慢慢长大，离线也没关系。');});},
    harvest(plot){this.act('/garden/'+plot+'/harvest',{},()=>{this.$refs.yard?.react('garden','收获了 '+this.garden.harvest_amount+' 三叶草，点小摊换份点心吧。');});},
    buy(item){const request_id=this.shopRequests[item] ||= crypto.randomUUID();this.act('/shop/buy',{item,request_id},()=>{delete this.shopRequests[item];this.notice='兑换成功，物品已经放进背包。';});},
    unpack(){if(this.arrival)this.act('/trips/'+this.arrival.id+'/unpack',{},result=>{this.arrivalReveal=result;});},
    openDiaryCard(id){const card=this.cards.find(c=>c.id===id);if(card)this.open(card);},
    exploreArrival(card){this.arrivalReveal=null;this.$nextTick(()=>this.open(card));},
    sendGift(){this.act('/gifts',{to_username:this.giftTo,item:this.giftItem});},
    open(card){this.selected=card;if(!card.opened)this.act('/postcards/'+card.id+'/open',{});},
    date(t){return new Date(t*1000).toLocaleDateString('zh-CN',{year:'numeric',month:'long',day:'numeric'});},
    rewardText(card){return card.rewards?.length?card.rewards.map(item=>item.icon+' '+item.name).join('、'):card.gift;},
    escape(e){if(e.key==='Escape')this.selected=null;}
  },
  async mounted(){await this.refresh();this.timer=setInterval(()=>{this.now=Date.now()/1000+this.offset;this.tick++;if(!this.busy&&((this.trip&&this.remaining===0)||(this.state?.user&&this.tick%10===0)))this.refresh();},1000);document.addEventListener('keydown',this.escape);},
  beforeUnmount(){clearInterval(this.timer);document.removeEventListener('keydown',this.escape);},
  template: `
    <div class="shell">
      <header><a class="brand" href="#" @click.prevent="page='home'"><span class="brand-mark">✳</span><span>小小远行<small>JustASmallJourney</small></span></a><span class="header-note">把日子过慢一点，把世界看多一点。</span><span class="account" v-if="state?.user">{{state.user.username}} <button class="text-button" @click="logout" :disabled="busy">退出</button></span><span class="edition" v-else>草叶与远行 · 07</span></header>
      <div v-if="error" class="error" role="alert">{{error}} <button @click="refresh" :disabled="polling">重试</button></div>
      <div v-if="notice && state?.user" class="supply-hint" role="status">{{notice}} <button class="text-button" @click="notice=''">收起</button></div>
      <main v-if="!state" class="loading">正在打开你的小屋…</main>
      <main v-else-if="!state.user" class="welcome auth-screen">
        <span class="eyebrow">OUR LITTLE SHARED WORLD</span><h1>世界很大，<br>在这里遇见朋友。</h1><p>每个人一间小屋，每一次远行都有新的故事。<br>登录后，回到属于你的小世界。</p>
        <div class="auth-tabs"><button :class="{active:authMode==='login'}" @click="authMode='login';error=''">回到小屋</button><button :class="{active:authMode==='register'}" @click="authMode='register';error=''">初次入住</button></div>
        <form @submit.prevent="authenticate"><label for="username">用户名</label><input id="username" v-model="username" required maxlength="24" autocomplete="username" placeholder="朋友们怎么称呼你"><label for="password">密码</label><input id="password" type="password" v-model="password" required minlength="8" maxlength="128" :autocomplete="authMode==='login'?'current-password':'new-password'" placeholder="至少 8 位字符">
        <label v-if="authMode==='register'&&state.legacy_available" class="legacy-choice"><input type="checkbox" v-model="claimLegacy" required>将原来的小动物与旅行回忆保存到我的账号</label><button class="primary" :disabled="busy||!username.trim()||password.length<8">{{busy?'正在打开小屋…':authMode==='login'?'登录小屋 ↗':'创建我的账号 ↗'}}</button></form><p class="hint">这个小世界，最多容纳 15 位朋友。</p>
      </main>
      <main v-else-if="!animal" class="welcome">
        <span class="eyebrow">一段小小的故事，从这里开始</span><h1>谁会陪你，<br>走过这些好天气？</h1><p>选一只小动物，为它起个名字。<br>以后，它会把远方的风景带回给你。</p>
        <form @submit.prevent="adopt"><div class="animal-options"><button v-for="(emoji,key) in animals" :key="key" type="button" :class="{chosen:kind===key}" @click="kind=key" :aria-pressed="kind===key"><span>{{emoji}}</span>{{labels[key]}}</button></div><label for="animal-name">它的名字</label><input id="animal-name" v-model="name" maxlength="16" required placeholder="例如：小满" autocomplete="off"><button class="primary" :disabled="busy||!name.trim()">{{busy?'正在布置小屋…':'一起住进小屋 ↗'}}</button></form>
      </main>
      <template v-else>
        <nav aria-label="主要页面"><button :class="{active:page==='home'}" @click="page='home'">⌂ 我的小屋</button><button :class="{active:page==='collection'}" @click="page='collection'">▤ 收藏 <span>{{cards.length}}</span></button><button :class="{active:page==='world'}" @click="page='world'">♧ 朋友世界</button><button :class="{active:page==='diary'}" @click="page='diary'">📖 日记</button></nav>
        <section v-if="state.weather" class="weather-strip" aria-label="小世界今日天气"><span class="weather-icon">{{state.weather.icon}}</span><div><strong>小世界今日 · {{state.weather.name}} · {{state.weather.season.name}}</strong><p>{{state.weather.note}} {{state.weather.season.note}}</p><small>大家共享的天气，每天更新 · {{state.weather.date}}</small><small v-if="trip?.weather">这次出发：{{trip.weather.icon}} {{trip.weather.name}} · {{trip.weather.date}}</small></div></section>
        <main v-if="page==='home'">
          <div class="page-heading"><div><span class="eyebrow">HOME, SWEET HOME</span><h1>{{trip?'它去看看世界了。':'平凡的一天，也有小小期待。'}}</h1><p>{{trip?'你可以先去忙，远方的故事会等你回来。':'收好行囊，让下一段故事慢慢发生。'}}</p></div><span class="status"><i :class="{away:trip}"></i>{{animal.name}} · {{trip?'旅行中':'在家'}}</span></div>

          <section v-if="arrival" class="return-banner"><span>🧳</span><div><h2>行李里，装着远方的小惊喜。</h2><p>{{trip?'上次归来的行李还等你打开。':animal.name+'已经回家了，来听听这次的故事吧。'}}</p></div><button class="primary" @click="unpack" :disabled="busy">打开归来的行李 ↗</button></section>
          <div class="home-grid"><div><indoor-scene v-if="room" ref="indoors" :animal="animals[animal.kind]" :name="animal.name" :now="now" :away="!!trip" :arrival="!!arrival" :weather="state.weather" :displays="state.displays || []" :items="inventory.souvenirs" :busy="busy" @exit="setRoom(false)" @navigate="navigate" @unpack="unpack" @save="({slot,item})=>act('/home/display/'+slot,{item})" @open="openDiaryCard" /><journey-scene v-else ref="yard" :garden="garden" :busy="busy" @plant="plant" @harvest="harvest" :departing="now < leavingUntil" :now="now" :animal="animals[animal.kind]" :name="animal.name" :away="!!trip" :weather="state.weather" :unread="unread.length" :arrival="!!arrival" @unpack="unpack" @navigate="navigate" @mail="unread.length?open(unread[0]):page='collection'" /></div>
          </div><section v-if="trip || unread.length" class="home-updates" aria-label="旅行与来信"><div v-if="trip" class="home-trip-summary"><strong>{{animal.name}}正在旅行</strong><span class="countdown">{{remaining>0?trip.duration_label+' · 预计 '+remaining+' 秒后回家':'正在整理旅行回忆…'}}</span><div class="progress"><div :style="{width:progress+'%'}"></div></div><p v-if="trip.note" class="trail-note" role="status">✉ {{trip.note.message}}</p></div><button v-if="unread.length" class="home-mail-summary" @click="open(unread[0])">✉ {{unread.length}} 张新明信片 · 拆开看看 →</button></section>
          <section class="recent"><div class="section-heading"><h2>留住一些好时光 <span>RECENT MEMORIES</span></h2><button class="text-button" @click="page='collection'">全部明信片 ↗</button></div><div v-if="!cards.length" class="empty-memory">✧ 第一张明信片，会是什么风景呢？ <span>等它旅行回来，这里就有故事了。</span></div><div v-else class="card-grid"><button v-for="card in cards.slice(0,3)" class="postcard" @click="open(card)"><div class="mini-scene" :class="card.scene?.theme || card.place"><travel-art :theme="card.scene?.theme || card.place" :variant="card.place" /><b v-if="card.participants.length" class="companions"><span v-for="(p,i) in card.participants" :key="i">{{animals[p.kind]}}</span></b><b v-else>{{animals[card.animal]}}</b><i v-if="!card.opened">NEW</i></div><div class="card-meta"><strong>{{card.encounter_id?'同行 · ':''}}{{places[card.place].name}}</strong><span>{{date(card.created_at)}}</span></div></button></div></section>
        </main>
<main v-else-if="page==='diary'"><journey-diary :entries="state.diary || []" :places="places" @open="openDiaryCard" /></main>

        <main v-else-if="page==='world'"><div class="page-heading"><div><span class="eyebrow">SOMEWHERE, TOGETHER</span><h1>原来，你也在这里。</h1><p>同一地点，重叠的旅程，就能留下共同回忆。世界每 10 秒更新一次。</p></div></div><div class="world-grid"><section class="panel"><h2>朋友的小动物</h2><p v-if="!state.friends.length">还没有其他小动物入住。朋友注册并领养动物后，就会出现在这里。</p><div class="friend" v-for="friend in state.friends" :key="friend.username"><span class="friend-emoji">{{animals[friend.kind]}}</span><div><strong>{{friend.name}}</strong><small>{{friend.username}}的小动物</small></div><span class="friend-status">{{friend.traveling?'正在旅行，归期将近':'在小屋休息'}}</span></div></section><section class="panel"><h2>这个世界的足迹</h2><p v-if="!state.events.length">第一段故事，等着大家写下。</p><article class="world-event" v-for="event in state.events" :key="event.id"><time>{{clock(event.created_at)}}</time><p>{{event.message}}</p></article></section></div><section class="gift-panel panel"><div><span class="eyebrow">LEAVE A LITTLE GIFT</span><h2>给朋友的小动物留个纪念品。</h2><p v-if="!state.friends.length">朋友入住并领养动物后，就可以在这里送礼。</p><p v-else-if="!giftableSouvenirs.length">还没有可送出的纪念品。等下一次旅行回来，也许就有了。</p><template v-else><label for="gift-friend">送给</label><select id="gift-friend" v-model="giftTo"><option v-for="friend in state.friends" :value="friend.username">{{friend.username}} 的 {{friend.name}}</option></select><div class="gift-options"><button v-for="item in giftableSouvenirs" :key="item.key" :class="{chosen:giftItem===item.key}" @click="giftItem=item.key"><span>{{item.icon}}</span><strong>{{item.name}}</strong><small>拥有 {{item.quantity}}</small></button></div></template></div><button class="primary" :disabled="!canGift" @click="sendGift">{{busy?'正在送出…':'送出小礼物 ↗'}}</button></section><section class="gift-log" v-if="gifts.length"><div class="section-heading"><h2>最近赠礼 <span>GIFT LOG</span></h2></div><article v-for="gift in gifts" :key="gift.id"><time>{{clock(gift.created_at)}}</time><p><b>{{gift.item.icon}} {{gift.item.name}}</b> {{gift.direction==='sent'?'送给了 '+gift.to_username:'来自 '+gift.from_username}}</p></article></section></main>
        <main v-else><div class="page-heading"><div><span class="eyebrow">POSTCARDS & MEMORIES</span><h1>把远方，收进日常。</h1><p>共 {{cards.length}} 张明信片，每一张都是走过的时光。</p></div></div><details class="souvenir-disclosure"><summary>礼物图鉴 <span>{{inventory.souvenirs.filter(i=>i.first_obtained_at).length}} / {{inventory.souvenirs.length}} 已发现</span></summary><section class="souvenir-book"><div class="section-heading"><h2>礼物图鉴 <span>SOUVENIRS</span></h2></div><label class="content-search">搜索纪念品<input type="search" v-model="souvenirQuery" placeholder="输入纪念品名称"></label><p v-if="!souvenirItems.length">没有找到对应纪念品。</p><div class="souvenir-grid"><article v-for="item in souvenirItems" :key="item.key" :class="{locked:!item.first_obtained_at}"><span>{{item.first_obtained_at?item.icon:'?'}}</span><strong>{{item.name}}</strong><small>{{item.first_obtained_at?'第一次获得：'+date(item.first_obtained_at):'尚未获得'}}</small><b>× {{item.quantity}}</b></article></div></section></details><div v-if="cards.length" class="collection-filters"><label class="content-search">找一段回忆<input type="search" v-model="cardQuery" placeholder="搜索地点、标题或文字"></label><label>去过的地方<select v-model="cardPlace"><option value="">全部地点</option><option v-for="key in visitedPlaces" :key="key" :value="key">{{places[key].name}}</option></select></label><span class="collection-counter">{{new Set(cards.map(c=>c.template_key || c.id)).size}} 种回忆 · 去过 {{visitedPlaces.length}} / {{Object.keys(places).length}} 个地方</span></div><p v-if="cards.length&&!matchingCards.length">没有找到这段回忆，换个名字试试。</p><div v-if="cards.length" class="card-grid"><button v-for="card in visibleCards" class="postcard" @click="open(card)"><div class="mini-scene" :class="card.scene?.theme || card.place"><travel-art :theme="card.scene?.theme || card.place" :variant="card.place" /><b v-if="card.participants.length" class="companions"><span v-for="(p,i) in card.participants" :key="i">{{animals[p.kind]}}</span></b><b v-else>{{animals[card.animal]}}</b><i v-if="!card.opened">NEW</i></div><div class="card-meta"><strong>{{card.encounter_id?'同行 · ':''}}{{places[card.place].name}}</strong><span>{{date(card.created_at)}}</span></div><span v-if="card.title" class="card-theme">{{card.title}}</span><p class="card-quote">“{{card.message}}”</p><p class="card-gifts">{{rewardText(card)}}</p></button></div><section v-else class="collection-empty"><span>✉</span><h2>信箱里，装着对远方的期待。</h2><p>完成第一次旅行，就能收到属于你的明信片。</p><button class="primary" @click="openPacking">去看看世界 ↗</button></section><div v-if="cardPages>1" class="content-pagination"><button :disabled="cardPage===1" @click="cardPage--">上一页</button><span>{{cardPage}} / {{cardPages}}</span><button :disabled="cardPage===cardPages" @click="cardPage++">下一页</button></div></main>
      </template>
        <backpack-dialog v-if="backpackOpen && animal" @close="backpackOpen=false">
          <div v-if="error" class="error" role="alert">{{error}}</div>
          <div class="bag-switcher" role="group" aria-label="背包分类"><button ref="bagFoodTab" :aria-pressed="bagCategory==='foods'" @click="bagCategory='foods'">🍙 食物 <span>{{foodCount}}</span></button><button :aria-pressed="bagCategory==='tools'" @click="bagCategory='tools'">🧭 工具 <span>{{inventory.tools.filter(i=>i.quantity>0).length}}</span></button><button :aria-pressed="bagCategory==='charms'" @click="bagCategory='charms'">🍀 信物 <span>{{inventory.charms.filter(i=>i.quantity>0).length}}</span></button></div>
          <p class="bag-description">{{bagCategory==='foods'?'出发时消耗一份，记得给下一次旅行留点口粮。':'旅行时可以带上一件，使用后会留在背包里。'}}</p>
          <section v-if="bagCategory==='foods' && inventory.daily.available" class="bag-daily" aria-label="每日饭团补给"><span aria-hidden="true">🍙</span><div><strong>今日免费饭团</strong><small>给下一段旅程加一份口粮</small></div><button class="primary" :disabled="busy" @click="claimDaily">领取饭团</button></section>
<label class="content-search">搜索背包<input type="search" v-model="bagQuery" placeholder="输入物品名称"></label>          <div class="bag-item-grid" :aria-label="bagCategory==='foods'?'食物库存':bagCategory==='tools'?'工具库存':'信物库存'"><article v-for="item in bagItems" :key="item.key" :class="['bag-item',{empty:item.quantity<=0}]"><span class="bag-item-icon">{{item.icon}}</span><div><strong>{{item.name}}</strong><p>{{item.description}}</p></div><b>{{bagCategory==='foods'?'× '+item.quantity:item.quantity>0?'已拥有':'未获得'}}</b></article></div><p v-if="!bagItems.length">没有找到对应物品。</p>
          <p class="bag-footnote">赠礼在「朋友世界」，礼物图鉴在「收藏」。</p>
        </backpack-dialog>
        <backpack-dialog v-if="packingOpen && animal" title="准备行囊" eyebrow="PACK A LITTLE HAPPINESS" title-id="packing-title" close-label="关闭行囊" @close="packingOpen=false"><div v-if="error" class="error" role="alert">{{error}}</div><packing-bag :inventory="inventory" :food="food" :tool="tool" :charm="charm" :busy="busy" :traveling="!!trip" :journey="trip" @food="food=$event" @tool="tool=$event" @charm="charm=$event" @depart="depart" @daily="claimDaily" @shop="openShop" /></backpack-dialog>
<backpack-dialog v-if="shopOpen && animal" title="院子里的旅行小铺" eyebrow="A LITTLE CORNER SHOP" title-id="shop-title" close-label="关闭旅行小铺" @close="closeShop"><div v-if="error" class="error" role="alert">{{error}}</div><p v-if="notice" role="status">{{notice}}</p><garden-shop :garden="garden" :foods="inventory.foods" :tools="inventory.tools" :charms="inventory.charms" :now="now" :busy="busy" @buy="buy" /><button v-if="shopFromPacking" class="primary shop-return" @click="closeShop">继续整理行囊 →</button></backpack-dialog>
        <backpack-dialog v-if="arrivalReveal && animal" eyebrow="WELCOME HOME" title="远行归来" title-id="arrival-title" close-label="关闭归来行李" @close="arrivalReveal=null"><p class="arrival-intro">{{animal.name}}把行李放下来，原来这次去了{{places[arrivalReveal.place].name}}。收获已放进背包，故事也保存好了。</p><article v-for="card in arrivalReveal.postcards" :key="card.id" class="arrival-card"><span>{{places[card.place].icon}} {{animals[card.animal]}}</span><h3>{{card.title || '一封远方的来信'}}</h3><p>“{{card.message}}”</p><ul v-if="card.equipment_log?.length" class="equipment-log"><li v-for="line in card.equipment_log" :key="line">{{line}}</li></ul><div class="arrival-rewards"><span v-for="item in card.rewards" :key="item.key">{{item.icon}} {{item.name}}</span></div><button class="text-button" @click="exploreArrival(card)">走进这张明信片的风景 →</button></article></backpack-dialog>
      <footer><span>✳ 小小远行</span><span>不赶路，只收集沿途的小幸福。</span><span>一个慢慢长大的小世界</span></footer>
      <div v-if="selected" class="modal-backdrop" @click.self="selected=null"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="postcard-title"><button class="close" @click="selected=null" aria-label="关闭明信片" autofocus>×</button><div class="mini-scene large" :class="selected.scene?.theme || selected.place"><travel-art :theme="selected.scene?.theme || selected.place" :variant="selected.place" /><b v-if="selected.participants.length" class="companions"><span v-for="(p,i) in selected.participants" :key="i">{{animals[p.kind]}}</span></b><b v-else>{{animals[selected.animal]}}</b><div class="stamp">小小远行<br>POSTCARD</div></div><div class="letter"><span class="eyebrow">A LITTLE NOTE FOR YOU</span><div v-if="selected.encounter_id" class="encounter-label">两只小动物，一段共同回忆</div><h2 id="postcard-title">{{selected.title || ('来自'+places[selected.place].name+'的问候')}}</h2><p>“{{selected.message}}”</p><div class="souvenir"><span>顺手带回：</span><b v-for="item in selected.rewards" :key="item.key">{{item.icon}} {{item.name}}</b><b v-if="!selected.rewards?.length">{{selected.gift}}</b></div><p v-if="selected.weather" class="weather-memory">{{selected.weather.icon}} 出发那天 · {{selected.weather.name}} · {{selected.weather.season.name}} · {{selected.weather.date}}</p><ul v-if="selected.equipment_log?.length" class="equipment-log"><li v-for="line in selected.equipment_log" :key="line">{{line}}</li></ul><div class="signature">{{selected.name}} · {{date(selected.created_at)}}</div><small>已自动保存到你的明信片收藏</small></div><journey-scene :key="selected.id" :scene="selected.place" :scene-data="selected.scene" :weather="selected.weather" memory /></section></div>
    </div>`
}).mount('#app');
