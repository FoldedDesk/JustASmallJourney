import './scene.css';
import TravelArt from './TravelArt.js';
import PaintedObject from './PaintedObject.js';
import YardGarden from './YardGarden.js';

const destinations = {
  lake: { title: '荷风湖畔', objects: [['🪷', '荷叶', '一滴水沿着荷叶滚了一圈，又回到中央。', 22, 60], ['🛶', '木舟', '小舟轻轻碰到桥边，像在邀请你坐一会儿。', 70, 48], ['🦆', '湖鸭', '小鸭排成一列，把水面写成弯弯的句子。', 64, 77]] },
  desert: { title: '风信沙丘', objects: [['🌴', '绿洲树荫', '走进树荫，热风也慢慢安静下来。', 24, 55], ['🏺', '旧水罐', '罐口刻着一行字：给下一个旅人留一口清凉。', 74, 73], ['🐪', '骆驼', '骆驼慢慢眨了眨眼，铃铛轻轻响了一声。', 58, 57]] },
  snow: { title: '白绒雪原', objects: [['🌲', '雪松', '松枝抖落一小团雪，像轻声说了句早安。', 23, 56], ['⛄', '雪人', '有人给雪人围了围巾，口袋里还放着一颗松果。', 73, 65], ['🛖', '驿站', '门口的牌子写着：冷了就进来坐坐。', 49, 72]] },
  ruins: { title: '苔痕古城', objects: [['🏛️', '古石柱', '细细的藤蔓沿着石纹，往天空的方向生长。', 24, 50], ['🏺', '陶罐', '罐身的花纹，像很久以前的人画下的梦。', 74, 72], ['🌿', '石缝新芽', '旧石墙上的新芽，正在写今天的故事。', 51, 77]] },
  forest: { title: '微风森林', objects: [['🌳', '老树', '树洞里藏着一封没有署名的信：愿你今天也开心。', 22, 46], ['🍄', '蘑菇', '小蘑菇排成一圈，像在等谁来参加茶会。', 70, 69], ['🌿', '蕨叶', '拨开蕨叶，一条软软的苔藓小路出现了。', 44, 77]] },
  sea: { title: '日落海岸', objects: [['🐚', '贝壳', '把贝壳靠近耳边，听见一小片海。', 23, 75], ['⛵', '帆船', '远处的帆船轻轻摇晃，正把今天送往远方。', 73, 45], ['🦀', '小螃蟹', '它横着走了两步，又害羞地躲进沙里。', 61, 77]] },
  mountain: { title: '星星山谷', objects: [['🔭', '望远镜', '从这里望出去，山的另一边还是温柔的山。', 23, 70], ['🪨', '石头', '石头被风磨得圆圆的，适合坐下来歇脚。', 70, 76], ['✨', '星光', '发现一颗还没睡醒的星星，正在悄悄眨眼。', 66, 28]] },
  library: { title: '晴窗图书馆', objects: [['📚', '书架', '书脊上写着《如何把平凡的一天过成冒险》。', 22, 50], ['📖', '翻开的书', '这一页夹着一片花瓣，还有一句“下次见”。', 55, 74], ['🪴', '窗边绿植', '绿叶朝着窗外，和你一起发了一会儿呆。', 79, 54]] },
  town: { title: '铃铛小镇', objects: [['🥖', '面包店', '刚出炉的香气飘过来，连脚步都慢了下来。', 22, 63], ['🔔', '风铃', '叮——小镇用一声清脆的问候欢迎你。', 68, 37], ['📮', '街角邮筒', '邮筒上写着：想念一个人的时候，就写封信吧。', 78, 73]] },
  garden: { title: '雨后花园', objects: [['🌷', '郁金香', '花瓣慢慢舒展开，像一个小小的早安。', 22, 65], ['🦋', '蝴蝶', '蝴蝶绕了一个圈，停在刚刚开放的花上。', 68, 40], ['⛲', '小喷泉', '水珠跳起来，又轻轻落回自己的小池塘。', 70, 75]] },
};

export default {
  components: { TravelArt, PaintedObject, YardGarden },
  props: { garden: Object, busy: Boolean, sceneData: Object, departing: Boolean, now: { default: 0 }, arrival: Boolean, memory: Boolean, scene: { default: 'home' }, animal: { default: '🐸' }, name: { default: '小动物' }, away: Boolean, weather: Object, unread: { default: 0 } },
  emits: ['navigate', 'mail', 'unpack', 'plant', 'harvest'],
  data: () => ({ lamp: false, watered: false, message: '', active: '', discovered: [], pulse: 0 }),
  computed: {
    activity() {
      const activities = [ ['📖','正在读书','把书翻过一页，指给你看一幅远方的插画。'], ['💤','正在打盹','迷迷糊糊地睁开眼，又安心地缩成一团。'], ['🫖','正在喝茶','捧着暖暖的杯子，给你留了身旁的位置。'], ['🎒','正在整理行李','把背包拍平，想了想，又把地图展开了。'] ];
      const seed = [...this.name].reduce((sum,c)=>sum+c.codePointAt(0),0);
      return activities[(Math.floor(this.now/300)+seed)%activities.length];
    },
    destination() { return this.sceneData?.objects ? this.sceneData : destinations[this.scene]; },
    theme() { return this.sceneData?.theme || this.scene; },
    weatherKey() { return this.weather?.key || 'sunny'; },
    objects() { return this.destination?.objects || []; },
  },
  watch: { scene() { this.message = ''; this.active = ''; this.discovered = []; } },
  methods: {
    react(key, message) { this.active = key; this.message = message; this.pulse++; },
    explore(object) {
      if (!this.discovered.includes(object[1])) this.discovered.push(object[1]);
      this.react(object[1], object[2]);
    },
    pet() { this.react('pet', this.name+this.activity[2]); },
    water() { this.watered = !this.watered; this.react('flowers', this.watered ? '给花浇了一点水，花朵精神起来了。' : '坐在花旁边，陪它安静地待一会儿。'); },
    light() { this.lamp = !this.lamp; this.react('lamp', this.lamp ? '暖暖的灯亮了，给小屋留一点安心。' : '关上灯，让小屋休息一会儿。'); },
  },
  template: `
    <section class="journey-scene-wrap" :aria-label="scene==='home'?'可交互的小屋':destination.title+'场景预览'">
      <div :class="['interactive-scene', 'land-'+theme, 'sky-'+weatherKey, {'lamp-on':lamp}]">
        <div class="scene-title"><span>{{scene==='home'?name+'的小院':destination.title}}</span><small>{{scene==='home'?'门前有花，路上有风':memory?'旅途回忆 · 再看看这些小细节':'风景预览 · 点亮三处小发现'}}</small></div>
        <div class="scenery" aria-hidden="true">
          <travel-art v-if="scene!==\'home\'" :theme="theme" :variant="scene" />
          <div class="scene-orb"></div><div class="scene-cloud cloud-one"></div><div class="scene-cloud cloud-two"></div>
          <svg class="landscape" viewBox="0 0 800 400" preserveAspectRatio="none"><path class="ridge-back" d="M0 280 Q150 110 340 260 Q540 120 800 250 V400 H0Z"/><path class="ridge-front" d="M0 330 Q230 250 450 320 Q640 240 800 310 V400 H0Z"/><path class="scene-trail" d="M430 270 Q360 330 480 400 H370 Q310 325 410 270Z"/></svg>
          <div v-if="theme==='sea'" class="scene-waves"></div>
          <div v-if="theme==='library'" class="reading-window">✚</div>
          <template v-if="scene==='home'"><span class="yard-tree tree-left"><painted-object kind="tree" /></span><span class="yard-tree tree-right"><painted-object kind="tree" /></span><div class="little-house"></div></template>
          <template v-if="theme==='town'"><span class="town-houses">🏠 🏡</span></template>
          <div v-if="weatherKey==='rainy' && theme!=='library'" class="scene-rain"><i v-for="n in 14" :key="n" :style="{left:(n*7)+'%',animationDelay:-(n%5)*.3+'s'}"></i></div>
        </div>
        <template v-if="scene==='home'">
          <yard-garden :garden="garden" :now="now" :busy="busy" @plant="$emit('plant',$event)" @harvest="$emit('harvest',$event)" /><button class="scene-object yard-stall" @click="$emit('navigate','shop')" aria-label="打开院子里的旅行小铺" aria-haspopup="dialog"><span class="stall-awning" aria-hidden="true"></span><span class="stall-counter" aria-hidden="true"><painted-object kind="bag" /><painted-object kind="clover" /></span><small>旅行小铺 · ☘ {{garden?.clovers || 0}}</small></button>
          <button class="scene-object yard-door" @click="$emit('navigate','indoors')" aria-label="打开小屋门进入室内"><span class="door-knob-dot" aria-hidden="true"></span><small>进屋坐坐</small></button>
          <button class="scene-object lamp-switch" @click="light" :aria-pressed="lamp" aria-label="小屋灯光"><span class="window-glow" aria-hidden="true"></span><small>{{lamp?'关灯':'开灯'}}</small></button>
          <button v-if="!away" class="scene-object yard-pet" @click="arrival?$emit('unpack'):pet()" :class="{'object-active':active==='pet'}" :aria-label="arrival?'听听'+name+'的旅行故事':'看看'+name+'：'+activity[1]"><span :key="pulse">{{animal}}</span><i v-if="!arrival" class="pet-activity" aria-hidden="true">{{activity[0]}}</i><small>{{arrival?'听它讲故事':activity[1]}}</small></button>
          <template v-else-if="departing"><span class="scene-departing" aria-hidden="true">{{animal}}<small>🎒</small></span><span class="departure-goodbye" role="status">行囊收好啦，我出门了！</span></template>
          <span v-else class="yard-away">出门散步了，晚点回来</span>
          <button class="scene-object yard-flowers" @click="water" :aria-pressed="watered" aria-label="照料花朵"><painted-object kind="flowers" /><small>{{watered?'陪花坐坐':'浇浇水'}}</small></button>
          <button class="scene-object yard-mail" @click="$emit('mail')" aria-label="打开邮箱"><painted-object kind="mail" /><b v-if="unread">{{unread}}</b><small>{{unread?'有新来信':'邮箱'}}</small></button>
<button v-if="arrival && !away" class="scene-object yard-bag" @click="$emit('unpack')" aria-label="打开归来的行李"><painted-object kind="suitcase" /><small>拆行李</small></button>
          <button v-else class="scene-object yard-bag" @click="$emit('navigate','backpack')" aria-label="查看背包"><painted-object kind="bag" /><small>背包</small></button>
          <button class="scene-object yard-sign" @click="$emit('navigate','prepare')" aria-label="路牌：去远行"><painted-object kind="sign" /><small>去远行 ↗</small></button>
        </template>
        <template v-else>
          <button v-for="object in objects" :key="object[1]" class="scene-object explore-object" :class="{'object-active':active===object[1]}" :style="{left:object[3]+'%',top:object[4]+'%'}" @click="explore(object)" :aria-label="'探索'+object[1]" :aria-pressed="discovered.includes(object[1])"><span>{{object[0]}}</span><small>{{object[1]}} {{discovered.includes(object[1])?'✓':'·'}}</small></button>
          <span class="preview-visitor" aria-hidden="true">👣</span>
        </template>
        <span class="scene-corner-note">{{weather?.icon || '☀️'}} {{weather?.name || '晴朗'}}<template v-if="destination"> · 已发现 {{discovered.length}} / 3</template></span>
      </div>
      <div class="scene-response" role="status" aria-live="polite"><span aria-hidden="true">✧</span><p>{{message || (scene==='home'?'点点小动物、花朵和小屋，也可以从邮箱与路牌开始。':'点点风景里的小物件，看看这里藏着什么故事。')}}</p></div>

    </section>`,
};
