import HomeShelf from './HomeShelf.js';
import './indoor.css';
import PaintedObject from './PaintedObject.js';

export default {
  components: { PaintedObject, HomeShelf },
  props: { animal: String, name: String, now: Number, away: Boolean, arrival: Boolean, weather: Object, displays: Array, items: Array, busy: Boolean },
  emits: ['navigate','unpack','save','open','exit'],
  data: () => ({ lamp: true, curtains: false, chosen: null, message: '', pulse: 0 }),
  computed: {
    period(){return Math.floor(this.now/300);},
    activity(){
      const seed=[...this.name].reduce((sum,c)=>sum+c.codePointAt(0),0);
      return this.chosen ?? (this.period+seed)%4;
    },
    activityName(){return ['在书桌旁读书','窝在床上打盹','坐在地毯上喝茶','在门边整理行李'][this.activity];},
  },
  watch: { period(){this.chosen=null;},away(){this.message='';this.chosen=null;} },
  methods: {
    focusEntry(){this.$refs.title.focus({preventScroll:true});},
    settleAt(activity){
      if(this.away){this.message=['把书签夹好，等它回来接着读。','把枕头拍松，给远行的小动物留好床铺。','茶杯摆好了，等它回来再添热茶。'][activity];return;}
      this.chosen=activity;this.pulse++;
      this.message=this.name+['走到书桌旁，翻开了上次没读完的那一页。','爬上软软的床，蜷起来伸了个懒腰。','捧起小杯子，给你留了地毯上的另一半位置。'][activity];
    },
    pet(){if(this.arrival){this.$emit('unpack');return;}this.pulse++;this.message=this.name+['抬起头，把书里的小插画指给你看。','迷迷糊糊地睁开眼，又安心地闭上了。','轻轻推过来一只空杯子，像在邀请你一起坐。','拍了拍行囊，好像已经期待下一次远行。'][this.activity];},
    light(){this.lamp=!this.lamp;this.message=this.lamp?'台灯亮了，小屋多了一圈暖光。':'把灯关小，留一点窗外的光。';},
    window(){this.curtains=!this.curtains;this.message=this.curtains?'拉上窗帘，把安静留在屋里。':'拉开窗帘，看看今天的'+(this.weather?.name || '好天气')+'。';},
  },
  template: `<section class="indoor-wrap" aria-label="可交互的室内小屋">
    <div class="indoor-heading"><div><small>HOME, SWEET HOME</small><h2 ref="title" tabindex="-1">{{name}}的小屋</h2></div><button class="text-button" @click="$emit('exit')">回到院子 ↗</button></div>
    <div class="indoor-stage" :class="[{'room-lamp-on':lamp,'curtains-closed':curtains},'room-weather-'+(weather?.key || 'sunny')]">
      <div class="room-wall" aria-hidden="true"></div><div class="room-floor" aria-hidden="true"></div><div class="room-rug" aria-hidden="true"></div><div class="room-chair" aria-hidden="true"><i></i></div><div class="room-plant" aria-hidden="true"><painted-object kind="flowers" /></div>
      <button class="room-window room-target" @click="window" :aria-pressed="curtains" :aria-label="curtains?'拉开窗帘':'拉上窗帘'"><span class="window-sky" aria-hidden="true">{{weather?.icon || '☀️'}}</span><span class="curtain curtain-left"></span><span class="curtain curtain-right"></span><small>{{curtains?'拉开窗帘':'看看窗外'}}</small></button>
      <div class="room-shelf"><home-shelf :displays="displays" :items="items" :busy="busy" @save="$emit('save',$event)" @open="$emit('open',$event)" /></div>
      <button class="room-door room-target" @click="$emit('exit')" aria-label="开门回到院子"><span aria-hidden="true">✧</span><small>去院子</small></button>
      <button class="room-desk room-target" @click="settleAt(0)" aria-label="在书桌读书"><span class="desk-books" aria-hidden="true"><painted-object kind="books" /></span><span class="desk-top"></span><span class="desk-drawer"></span><span class="desk-leg leg-left"></span><span class="desk-leg leg-right"></span><small>读一会儿书</small></button>
      <button class="room-bed room-target" @click="settleAt(1)" aria-label="在床上休息"><span class="bed-pillow"></span><span class="bed-quilt"></span><small>窝一会儿</small></button>
      <button class="room-tea room-target" @click="settleAt(2)" aria-label="在地毯上喝茶"><painted-object kind="tea" /><small>坐下喝茶</small></button>
      <button class="room-lamp room-target" @click="light" :aria-pressed="lamp" aria-label="室内台灯"><painted-object kind="lamp" /><small>{{lamp?'关灯':'开灯'}}</small></button>
      <button v-if="!away" class="room-pet room-target" :class="'pet-position-'+activity" @click="pet" :aria-label="arrival?'听听'+name+'的旅行故事':name+activityName"><span :key="pulse" :class="{'pet-napping':activity===1}">{{animal}}</span><i v-if="activity===1" aria-hidden="true">z Z</i><small>{{arrival?'听它讲故事':activityName}}</small></button>
      <span v-else class="room-away">{{name}}出门了<br>小屋替你等它回来</span>
      <button class="room-bag room-target" @click="$emit('navigate','backpack')" aria-label="打开室内背包"><painted-object kind="bag" /><small>整理背包</small></button>
      <button v-if="arrival" class="room-luggage room-target" @click="$emit('unpack')" :disabled="busy" aria-label="打开室内归来行李"><painted-object kind="suitcase" /><small>归来的行李</small></button>
    </div>
    <div class="scene-response" role="status" aria-live="polite"><span aria-hidden="true">✧</span><p>{{message || (away?'它出门了，帮它整理一下小屋吧。':'点点书桌、床铺或茶杯，陪它慢慢过一会儿。墙上的架子可以摆旅行纪念品。')}}</p></div>
  </section>`,
};
