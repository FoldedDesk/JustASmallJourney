import './diary.css';

export default {
  props: ['entries', 'places'],
  emits: ['open'],
  computed: {
    days() {
      const groups = new Map();
      for (const entry of this.entries) {
        const day = new Date(entry.started_at*1000).toLocaleDateString('zh-CN');
        if (!groups.has(day)) groups.set(day, []);
        groups.get(day).push(entry);
      }
      return [...groups].map(([date, entries])=>({date, entries}));
    },
  },
  methods: { time(t) { return new Date(t*1000).toLocaleString('zh-CN',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'}); } },
  template: `<section class="journey-diary" aria-label="旅行日记"><div class="page-heading"><div><span class="eyebrow">DAYS WORTH KEEPING</span><h1>把走过的日子，慢慢记下来。</h1><p>出发、途中捎信、归来，还有和朋友相遇的那一天。</p></div></div><p v-if="!entries.length" class="empty-memory">日记的第一页，等下一次出发来写。</p><section v-for="day in days" :key="day.date" class="diary-day"><h2>{{day.date}}</h2><article v-for="entry in day.entries" :key="entry.id" class="diary-entry"><header><strong>{{entry.name}} · {{entry.duration_label}}</strong><span>{{entry.settled?'已经归来':'旅行中'}}</span></header><ol><li><time>{{time(entry.started_at)}} · 出发</time><p>{{entry.food?entry.food.icon+' 带上'+entry.food.name:'整理好了行囊'}}{{entry.tool?'，还有'+entry.tool.name:'，轻装上路'}}。</p></li><li v-if="entry.note"><time>{{time(entry.note.created_at)}} · 途中捎信</time><p>“{{entry.note.message}}”</p></li><li v-if="entry.settled"><time>{{time(entry.ends_at)}} · 回到小屋</time><p>去了{{places[entry.place].name}}，带回 {{entry.cards.length}} 张明信片。</p><div class="diary-memories"><button v-for="card in entry.cards" :key="card.id" class="text-button" @click="$emit('open',card.id)">{{card.encounter_id?'和朋友的共同回忆':'打开这次旅行的来信'}} →</button></div><p v-for="card in entry.cards.filter(c=>c.encounter_id)" :key="'encounter'+card.id" class="diary-encounter">{{card.message}}</p></li><li v-else><p>它还在路上，故事等回来再讲。</p></li></ol></article></section></section>`,
};
