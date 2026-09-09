import './yard-garden.css';
import PaintedObject from './PaintedObject.js';

export default {
  components: { PaintedObject },
  props: ['garden','now','busy'],
  emits: ['plant','harvest'],
  methods: {
    ready(plot){return plot.ready_at!==null && plot.ready_at<=this.now;},
    remaining(plot){const seconds=Math.max(0,Math.ceil(plot.ready_at-this.now));return Math.floor(seconds/60)+'分'+seconds%60+'秒';},
    label(plot){return '第'+plot.plot+'块草圃：'+(plot.ready_at===null?'免费播种':this.ready(plot)?'收获'+this.garden.harvest_amount+'枚三叶草':this.remaining(plot)+'后成熟');},
  },
  template: `<section v-if="garden" class="yard-crops" aria-label="院子里的三叶草草圃"><div class="crop-caption">小院草圃</div><div class="crop-beds"><button v-for="plot in garden.plots" :key="plot.plot" :class="{ripe:ready(plot),growing:plot.ready_at!==null&&!ready(plot)}" :aria-label="label(plot)" :disabled="busy || (plot.ready_at!==null&&!ready(plot))" @click="plot.ready_at===null?$emit('plant',plot.plot):$emit('harvest',plot.plot)"><span v-if="plot.ready_at===null" class="seed-dots" aria-hidden="true">· · ·</span><painted-object v-else kind="clover" /><small>{{plot.ready_at===null?'播种':ready(plot)?'收获 +'+garden.harvest_amount:remaining(plot)}}</small></button></div></section>`,
};
