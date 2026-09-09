import './backpack.css';

export default {
  props: { eyebrow: { default: 'YOUR LITTLE BACKPACK' }, title: { default: '我的背包' }, titleId: { default: 'backpack-title' }, closeLabel: { default: '关闭背包' } },
  emits: ['close'],
  mounted() {
    this.returnFocus = document.activeElement;
    this.previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    this.$refs.dialog.showModal();
  },
  beforeUnmount() {
    this.$refs.dialog.close();
    document.body.style.overflow = this.previousOverflow;
    if (this.returnFocus?.isConnected) this.returnFocus.focus({preventScroll:true});
  },
  methods: {
    backdrop(event) {
      if (event.target !== this.$refs.dialog) return;
      const box = this.$refs.dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) this.$emit('close');
    },
  },
  template: `<dialog ref="dialog" class="backpack-dialog" :aria-labelledby="titleId" @cancel.prevent="$emit('close')" @click="backdrop"><header class="backpack-header"><div><span class="eyebrow">{{eyebrow}}</span><h2 :id="titleId">{{title}}</h2></div><button class="backpack-close" @click="$emit('close')" :aria-label="closeLabel" autofocus>×</button></header><div class="backpack-content"><slot /></div></dialog>`,
};
