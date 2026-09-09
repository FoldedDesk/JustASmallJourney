import './garden.css';

export default {
  props: ['garden', 'foods', 'tools', 'charms', 'now', 'busy'],
  emits: ['buy'],
  data: () => ({ filter: '', affordable: false, category: 'foods', page: 1 }),
  computed: {
    matches() { return (this.category==='foods'?this.foods:this.category==='tools'?this.tools:this.charms).filter(f => f.name.includes(this.filter.trim()) && (!this.affordable || (f.price <= this.garden.clovers && !(this.category!=='foods'&&f.quantity>0)))); },
    pages() { return Math.max(1,Math.ceil(this.matches.length/12)); },
    visibleFoods() { return this.matches.slice((this.page-1)*12,this.page*12); },
  },
  watch: { filter(){this.page=1;},category(){this.page=1;this.filter='';},affordable(){this.page=1;},pages(n){this.page=Math.min(this.page,n);} },
  methods: {
    ready(plot) { return plot.ready_at !== null && plot.ready_at <= this.now; },
    countdown(plot) { const seconds = Math.max(0, Math.ceil(plot.ready_at - this.now)); return Math.floor(seconds / 60) + '分' + seconds % 60 + '秒'; },
  },
  template: `<div v-if="garden" class="garden-shop">
    <div class="shop-wallet"><strong>☘ {{garden.clovers}} 三叶草</strong><small>在院子里种植、收获，再来换点旅行用品。</small></div>




    <section class="food-shop" aria-label="三叶草旅行小铺"><div class="section-heading"><div><h2>转角旅行小铺</h2><p>食物每次兑换 1 份；工具和信物只需兑换一次，之后一直可用。</p></div><label class="shop-filter"><input type="checkbox" v-model="affordable">只看换得起的</label></div><div class="bag-switcher"><button :aria-pressed="category==='foods'" @click="category='foods'">食物 · {{foods.length}}</button><button :aria-pressed="category==='tools'" @click="category='tools'">工具 · {{tools.length}}</button><button :aria-pressed="category==='charms'" @click="category='charms'">信物 · {{charms.length}}</button></div><label class="shop-search">找一种旅行用品<input v-model="filter" :placeholder="category==='foods'?'例如：竹筒饭':category==='tools'?'例如：望远镜':'例如：月光'" type="search"></label>
      <div class="shop-grid"><article v-for="food in visibleFoods" :key="food.key" class="food-product"><span class="food-icon">{{food.icon}}</span><div><h3>{{food.name}}</h3><p>{{food.description}}</p><small>{{category==='foods'?'背包里有 '+food.quantity+' 份':food.quantity?'已拥有 · 可重复使用':'尚未拥有'}}</small></div><button class="primary" :disabled="busy || garden.clovers<food.price || (category!=='foods'&&food.quantity>0)" @click="$emit('buy',food.key)" :aria-label="'兑换'+food.name+'，需要'+food.price+'三叶草'">{{category!=='foods'&&food.quantity>0?'已拥有':'☘ '+food.price+' · 兑换'}}</button></article></div><p v-if="!visibleFoods.length">暂时没有符合条件的物品，换个名字搜搜，或先去收获三叶草。</p><div v-if="pages>1" class="content-pagination"><button :disabled="page===1" @click="page--">上一页</button><span>{{page}} / {{pages}} · {{matches.length}} 件</span><button :disabled="page===pages" @click="page++">下一页</button></div>
    </section>
  </div>`,
};
