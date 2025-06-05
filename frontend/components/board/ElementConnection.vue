<template>
  <g v-if="source && target">
    <path
      :d="bezierPath"
      :stroke="threadColor"
      :stroke-width="threadWidth"
      fill="none"
      :class="connectionClass"
      :style="glowStyle"
      :filter="glowFilter"
      stroke-linecap="round"
      stroke-dasharray="0.5,0.5,2,0.5,1,0.5,2,0.5,1,0.5,2,0.5,1,0.5'"
      :marker-end="'url(#arrowhead-thread)'"
    />
    <!-- Connection label -->
    <text
      v-if="connection.label"
      :x="midpoint.x"
      :y="midpoint.y - 12"
      text-anchor="middle"
      font-size="15"
      font-family="monospace"
      :fill="threadColor"
      class="connection-label"
      @click.stop="onLabelClick"
      style="cursor:pointer; user-select:none;"
    >
      {{ connection.label }}
    </text>
    
    <!-- 🆕 Add this right below the label -->
    <g
      v-if="midpoint"
      @click.stop="emit('delete', connection.id)"
      style="cursor: pointer;"
    >
      <circle
        :cx="midpoint.x"
        :cy="midpoint.y"
        r="12"
        fill="#fff"
        stroke="#d33"
        stroke-width="2"
      />
      <text
        :x="midpoint.x"
        :y="midpoint.y + 4"
        text-anchor="middle"
        font-size="14"
        fill="#d33"
        style="pointer-events: none;"
      >
        ×
      </text>
    </g>
    
    <defs>
      <filter :id="glowFilterId" x="-30%" y="-30%" width="160%" height="160%">
        <feDropShadow dx="0" dy="0" stdDeviation="6" :flood-color="threadColor" flood-opacity="0.7" />
      </filter>
      <marker id="arrowhead-thread" markerWidth="12" markerHeight="8" refX="12" refY="4" orient="auto">
        <polygon points="0 0, 12 4, 0 8" :fill="threadColor" />
      </marker>
    </defs>
  </g>
</template>

<script setup>
import { computed, ref, watchEffect } from 'vue';
const emit = defineEmits(['edit-label', 'delete']); // add 'delete'
const props = defineProps({
  connection: { type: Object, required: true },
  elements: { type: Array, required: true },
  selectedElementId: { type: [String, Number, null], default: null },
});
const width = 120; // element width (should match element style)
const height = 70; // element height (should match element style)
const source = computed(() =>
  props.elements.find(e => e.id === props.connection.sourceId)
);
const target = computed(() =>
  props.elements.find(e => e.id === props.connection.targetId)
);

// Color and thickness by type
const typeStyles = {
  thread:   { color: '#b33', width: 4 },
  logic:    { color: '#3366cc', width: 4 },
  alibi:    { color: '#33a853', width: 4 },
  evidence: { color: '#fbbc05', width: 5 },
};
const threadColor = typeStyles[props.connection.type]?.color || '#b33';
const threadWidth = typeStyles[props.connection.type]?.width || 4;

// Calculate a smooth Bezier path between source and target
const bezierPath = computed(() => {
  if (!source.value || !target.value) return '';
  const x1 = source.value.position.x + width / 2;
  const y1 = source.value.position.y + height / 2;
  const x2 = target.value.position.x + width / 2;
  const y2 = target.value.position.y + height / 2;

  const dx = x2 - x1;
  const dy = y2 - y1;
  const curve = 0.3 * Math.sqrt(dx * dx + dy * dy);
  const wave = Math.sin(Date.now() / 800 + (x1 + y1) / 100) * 10;

  const cx1 = x1 + dx * 0.25 + (dy > 0 ? curve : -curve) * 0.2 + (!isGlowing.value ? wave : 0);
  const cy1 = y1 + dy * 0.25 + (dx > 0 ? curve : -curve) * 0.1 + (!isGlowing.value ? wave : 0);
  const cx2 = x1 + dx * 0.75 - (dy > 0 ? curve : -curve) * 0.2 - (!isGlowing.value ? wave : 0);
  const cy2 = y1 + dy * 0.75 - (dx > 0 ? curve : -curve) * 0.1 - (!isGlowing.value ? wave : 0);

  return `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`;
});

const midpoint = computed(() => {
  if (!source.value || !target.value) return { x: 0, y: 0 };
  return {
    x: (source.value.position.x + target.value.position.x) / 2 + width / 2,
    y: (source.value.position.y + target.value.position.y) / 2 + height / 2,
  };
});

// Animation: glow if attached to selected element, else idle wave
const isGlowing = computed(() =>
  props.selectedElementId &&
  (props.connection.sourceId === props.selectedElementId || props.connection.targetId === props.selectedElementId)
);
const glowFilterId = `thread-glow-${props.connection.id}`;
const glowFilter = computed(() => (isGlowing.value ? `url(#${glowFilterId})` : undefined));
const glowStyle = computed(() => (isGlowing.value ? { filter: `url(#${glowFilterId})`, animation: 'glowPulse 1.2s infinite alternate' } : {}));
const connectionClass = computed(() => (isGlowing.value ? 'glow-thread' : 'wavy-thread'));

function onLabelClick() {
  emit('edit-label', props.connection);
}

// Animate idle wave by updating the path every frame
if (!import.meta.env.SSR) {
  if (!isGlowing.value) {
    setInterval(() => { /* triggers reactivity for path */ }, 60);
  }
}
</script>

<style scoped>
.connection-label {
  font-weight: bold;
  text-shadow: 0 2px 8px #fff, 0 0 2px #0002;
  pointer-events: auto;
}
@keyframes glowPulse {
  0% { filter: brightness(1) drop-shadow(0 0 8px currentColor); }
  100% { filter: brightness(1.3) drop-shadow(0 0 18px currentColor); }
}
.wavy-thread {
  animation: wavyThreadAnim 2.5s linear infinite;
}
@keyframes wavyThreadAnim {
  0% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: 24; }
}
.element-connection {
  position: absolute;
  pointer-events: none;
}
</style> 