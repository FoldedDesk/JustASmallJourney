import './garden.css';

export default {
  props: ['garden', 'foods', 'now', 'busy'],
  emits: ['plant', 'harvest', 'buy'],
  data: () => ({ filter: '', affordable: false }),
  computed: { visibleFoods() { return this.foods.filter(f => f.name.includes(this.filter.trim()) && (!this.affordable || f.price <= this.garden.clovers)); } },
  methods: {
    ready(plot) { return plot.ready_at !== null && plot.ready_at <= this.now; },
    countdown(plot) { const seconds = Math.max(0, Math.ceil(plot.ready_at - this.now)); return Math.floor(seconds / 60) + '分' + seconds % 60 + '秒'; },
  },
  template: `<div v-if="garden" class="garden-shop">
    <div class="page-heading"><div><span class="eyebrow">GROW A LITTLE JOURNEY</span><h1>把下一次远行，种出来。</h1><p>免费播种，离线也会生长。成熟的三叶草，能换一份路上的好心情。</p></div><span class="clover-wallet" aria-label="三叶草余额">☘ {{garden.clovers}} 三叶草</span></div>
    <section class="clover-garden" aria-label="三叶草草圃"><div class="section-heading"><h2>小院草圃</h2><span>每块约 {{Math.ceil(garden.grow_seconds/60)}} 分钟 · 收获 {{garden.harvest_amount}} 三叶草</span></div>
      <div class="plot-grid"><article v-for="plot in garden.plots" :key="plot.plot" :class="['clover-plot', {ripe:ready(plot)}]"><span class="plot-number">第 {{plot.plot}} 块地</span><div class="plot-art" aria-hidden="true">{{plot.ready_at===null?'· · ·':ready(plot)?'☘ ☘ ☘':'🌱 🌱'}}</div><strong>{{plot.ready_at===null?'一块松软的空地':ready(plot)?'三叶草长好了':'正在慢慢长大'}}</strong><small>{{plot.ready_at===null?'种子免费，随时可以播种':ready(plot)?'不会枯萎，等你回来收获':countdown(plot)+' 后成熟'}}</small><button class="primary" :disabled="busy || (plot.ready_at!==null&&!ready(plot))" @click="plot.ready_at===null?$emit('plant',plot.plot):$emit('harvest',plot.plot)">{{plot.ready_at===null?'播种三叶草':ready(plot)?'收获 +'+garden.harvest_amount:'等待生长'}}</button></article></div>
      <p>成熟后不会继续累积；收获后再播种。第一次布置草圃送 12 三叶草，先去挑一点喜欢的食物吧。</p>
    </section>
    <section class="food-shop" aria-label="三叶草食物小铺"><div class="section-heading"><div><h2>转角食物小铺</h2><p>每次兑换 1 份，直接放进背包。所有食物都能用三叶草兑换。</p></div><label class="shop-filter"><input type="checkbox" v-model="affordable">只看换得起的</label></div><label class="shop-search">找一种食物<input v-model="filter" placeholder="例如：热可可" type="search"></label>
      <div class="shop-grid"><article v-for="food in visibleFoods" :key="food.key" class="food-product"><span class="food-icon">{{food.icon}}</span><div><h3>{{food.name}}</h3><p>{{food.description}}</p><small>背包里有 {{food.quantity}} 份</small></div><button class="primary" :disabled="busy || garden.clovers<food.price" @click="$emit('buy',food.key)" :aria-label="'兑换'+food.name+'，需要'+food.price+'三叶草'">☘ {{food.price}} · 兑换</button></article></div><p v-if="!visibleFoods.length">暂时没有符合条件的食物，换个名字搜搜，或先去收获三叶草。</p>
    </section>
  </div>`,
};
