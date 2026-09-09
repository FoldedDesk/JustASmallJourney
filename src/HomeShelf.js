import BackpackDialog from './BackpackDialog.js';
import './home.css';

export default {
  components: { BackpackDialog },
  props: { displays: Array, items: Array, busy: Boolean },
  emits: ['save', 'open'],
  data: () => ({ slot: null, query: '' }),
  computed: {
    selected() { return this.displays.find(d => d.slot === this.slot); },
    available() { return this.items.filter(i => i.quantity > 0 && i.name.includes(this.query.trim())); },
  },
  methods: {
    date(t) { return new Date(t*1000).toLocaleDateString('zh-CN'); },
    openMemory() { const id=this.selected.memory.card_id; this.slot=null; this.$nextTick(()=>this.$emit('open',id)); },
  },
  template: `<section class="home-shelf" aria-label="小屋纪念品架"><div class="shelf-heading"><h3>留在小屋的风景</h3><small>点点摆设，翻一段回忆</small></div><div class="shelf-slots"><button v-for="n in 3" :key="n" @click="slot=n" :aria-label="'查看展示位'+n"><span>{{displays.find(d=>d.slot===n)?.item.icon || '＋'}}</span><small>{{displays.find(d=>d.slot===n)?.item.name || '摆一件纪念品'}}</small></button></div>
  <backpack-dialog v-if="slot" eyebrow="LITTLE MEMORIES" title="小屋的纪念品" title-id="shelf-title" close-label="关闭纪念品摆设" @close="slot=null"><div v-if="selected" class="shelf-memory"><span>{{selected.item.icon}}</span><h3>{{selected.item.name}}</h3><p>{{selected.memory?.text || '一件值得留在小屋的小收藏'}}</p><small v-if="selected.memory">{{date(selected.memory.created_at)}}</small><button v-if="selected.memory?.card_id" class="text-button" @click="openMemory">看看那次旅行的明信片 →</button></div><p class="hint">展示不消耗纪念品。送出最后一件时会自动收起，收藏记录仍然保留。</p><label class="content-search">搜索可摆放的纪念品<input v-model="query" type="search" placeholder="输入纪念品名称"></label><div class="shelf-choices"><button v-for="item in available" :key="item.key" :disabled="busy" :aria-pressed="selected?.item.key===item.key" @click="$emit('save',{slot,item:item.key})"><span>{{item.icon}}</span>{{item.name}}<small>{{displays.some(d=>d.item.key===item.key)?'已摆放 · 可移到这里':'摆在这里'}}</small></button></div><p v-if="!available.length">{{query?'没有找到，试试别的名字。':'架子还空着，等下一次旅行带点小东西回来吧。'}}</p><button v-if="selected" class="text-button" :disabled="busy" @click="$emit('save',{slot,item:null})">收起这件摆设</button></backpack-dialog></section>`,
};
