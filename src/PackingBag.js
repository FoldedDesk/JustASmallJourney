import './packing.css';

export default {
  props: { inventory: Object, food: String, tool: String, charm: String, busy: Boolean, traveling: Boolean, journey: Object },
  emits: ['food', 'tool', 'charm', 'depart', 'shop', 'daily'],
  data: () => ({ category: 'foods', query: '', feedback: '点下方物品装入行囊，点已装好的位置可以取下。' }),
  watch: {category(){this.query='';}},
  computed: {
    packedFood() { return this.traveling ? this.journey?.food : this.inventory.foods.find(i=>i.key===this.food && i.quantity>0); },
    packedTool() { return this.traveling ? this.journey?.tool : this.inventory.tools.find(i=>i.key===this.tool && i.quantity>0); },
    packedCharm() { return this.traveling ? this.journey?.charm : this.inventory.charms.find(i=>i.key===this.charm && i.quantity>0); },
    items() { return this.inventory[this.category].filter(i=>i.quantity>0&&i.name.includes(this.query.trim())); },
  },
  methods: {
    choose(item) {
      const type=this.category==='foods'?'food':this.category==='tools'?'tool':'charm';
      const remove=this[type]===item.key;
      this.$emit(type,remove?'':item.key);
      this.feedback=remove?'把'+item.name+'放回了架子。':'装好了'+item.name+'，'+(type==='food'?'路上饿了就吃一点。':'路上也许用得上。');
    },
    remove(type) {
      if(this.busy || this.traveling)return;
      const item=type==='food'?this.packedFood:type==='tool'?this.packedTool:this.packedCharm;
      this.category=type==='food'?'foods':type==='tool'?'tools':'charms';
      if(item){this.$emit(type,'');this.feedback='把'+item.name+'放回了架子。';}
    },
  },
  template: `<section class="packing-table" aria-label="整理旅行行囊">
    <p class="packing-intro">带一点食物，挑一件工具和一枚信物。去哪里，就交给它自己决定吧。</p>
    <div class="open-satchel"><div class="satchel-label">🎒 这次带上 <small>食物必带 · 工具／信物选带</small></div><div class="satchel-slots">
      <button class="satchel-slot" :class="{filled:packedFood}" :disabled="busy||traveling" @click="remove('food')" :aria-label="packedFood?'取下'+packedFood.name:'选择旅行食物'"><span :key="food">{{packedFood?.icon || '＋'}}</span><strong>{{packedFood?.name || '放一份食物'}}</strong><small>{{packedFood?'1 份 · 点一下取下':'必带'}}</small></button>
      <button class="satchel-slot" :class="{filled:packedTool}" :disabled="busy||traveling" @click="remove('tool')" :aria-label="packedTool?'取下'+packedTool.name:'选择旅行工具'"><span :key="tool">{{packedTool?.icon || '＋'}}</span><strong>{{packedTool?.name || '放一件工具'}}</strong><small>{{packedTool?'可重复使用 · 取下':'选带'}}</small></button>
      <button class="satchel-slot" :class="{filled:packedCharm}" :disabled="busy||traveling" @click="remove('charm')" :aria-label="packedCharm?'取下'+packedCharm.name:'选择旅行信物'"><span :key="charm">{{packedCharm?.icon || '✧'}}</span><strong>{{packedCharm?.name || '放一枚信物'}}</strong><small>{{packedCharm?'可重复使用 · 取下':'选带'}}</small></button>
    </div></div>
    <p class="packing-feedback" role="status">{{feedback}}</p>
    <p v-if="packedTool" class="packing-feedback">{{packedTool.icon}} {{packedTool.description}}</p><p v-if="packedCharm" class="packing-feedback">{{packedCharm.icon}} {{packedCharm.description}}</p>
    <div class="bag-switcher"><button :aria-pressed="category==='foods'" @click="category='foods'">食物</button><button :aria-pressed="category==='tools'" @click="category='tools'">工具</button><button :aria-pressed="category==='charms'" @click="category='charms'">信物</button></div>
    <label class="content-search">找找背包里的物品<input type="search" v-model="query" placeholder="输入物品名称"></label>
    <div class="packing-items"><button v-for="item in items" :key="item.key" :aria-pressed="(category==='foods'?food:category==='tools'?tool:charm)===item.key" :disabled="busy||traveling" @click="choose(item)"><span>{{item.icon}}</span><strong>{{item.name}}</strong><small>{{(category==='foods'?food:category==='tools'?tool:charm)===item.key?'✓ 已装入':category==='foods'?'库存 '+item.quantity:'可重复使用'}}</small></button></div>
    <p v-if="!items.length" class="packing-empty">{{query?'没有找到，试试别的名字。':category==='foods'?'还没有旅行点心，领一份饭团或去小铺挑一点吧。':'暂时没有这类物品，带好食物也可以出发。'}}</p>
    <div class="packing-supply"><button v-if="inventory.daily.available" class="text-button" :disabled="busy" @click="$emit('daily')">🍙 领取今日饭团</button><button class="text-button" :disabled="busy" @click="$emit('shop')">去小铺补充 →</button></div>
    <div class="packing-footer"><p>{{traveling?'它已经在路上了，等回家再收拾行囊吧。':packedFood?'行囊准备好了，远方会是什么样呢？':'先装一份食物，再出发。'}}</p><button class="primary" :disabled="busy||traveling||!packedFood" @click="$emit('depart')">{{busy?'正在收好行囊…':traveling?'旅途中':'合上行囊，出发 ↗'}}</button></div>
  </section>`,
};
