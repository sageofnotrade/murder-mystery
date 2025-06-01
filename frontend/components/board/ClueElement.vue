<template>
  <div class="clue-element">
    <slot>Clue</slot>
    <div class="element-meta">{{ element?.type }} #{{ element?.id }}</div>
  </div>
</template>

<script setup>
defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.clue-element {
  min-width: 120px;
  min-height: 70px;
  background: #e0f7fa;
  border: 2px solid #0097a7;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0,150,136,0.08);
  padding: 0.5rem;
  position: absolute;
}
.element-meta {
  font-size: 0.7em;
  color: #0097a7;
  margin-top: 0.5em;
}
</style> 