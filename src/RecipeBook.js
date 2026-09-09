export default {
  props: ['recipes', 'places', 'foods', 'tools', 'souvenirs', 'cards', 'compact'],
  emits: ['prepare', 'open'],
  methods: {
    food(key) { return this.foods.find(f => f.key === key) || {}; },
    tool(key) { return this.tools.find(t => t.key === key) || {}; },
    gift(key) { return this.souvenirs.find(s => s.key === key) || {}; },
    owned(recipe) { return this.cards.find(c => c.template_key === 'combo:' + recipe.key); },
  },
  template: `<section class="recipe-book" aria-label="搭配明信片手帐"><div class="section-heading"><div><h2>{{compact?'这里适合带什么？':'搭配明信片手帐'}}</h2><p>{{compact?'选中一条搭配，自动装配食物与工具。归来会带回主题明信片和专属纪念品。':'每个地点都有两段点心故事。集齐食物、地点与指定工具，就能把它带回来。'}}</p></div><span>{{recipes.filter(r=>owned(r)).length}} / {{recipes.length}}</span></div><div :class="['recipe-grid',{'recipe-compact':compact}]"><article v-for="recipe in recipes" :key="recipe.key" :class="['recipe-card',{'recipe-owned':owned(recipe)}]"><div :class="['recipe-art',recipe.place]"><span>{{places[recipe.place].icon}}</span><span>{{food(recipe.food).icon}}</span><b>{{owned(recipe)?'已收藏':recipe.tool?'特殊搭配':'食物搭配'}}</b></div><div class="recipe-copy"><h3>{{recipe.title}}</h3><p>{{places[recipe.place].name}} ＋ {{food(recipe.food).name}}{{recipe.tool?' ＋ '+tool(recipe.tool).name:' · 工具不限'}}</p><small>专属纪念品：{{gift(recipe.reward).icon}} {{gift(recipe.reward).name}}</small><div><button class="text-button" @click="$emit('prepare',recipe)">准备这套搭配 ↗</button><button v-if="owned(recipe)" class="text-button" @click="$emit('open',owned(recipe))">查看来信 →</button></div></div></article></div></section>`,
};
