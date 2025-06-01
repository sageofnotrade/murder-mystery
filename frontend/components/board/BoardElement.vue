<template>
  <div class="board-element">
    <slot />
    <div class="element-meta">{{ element?.type }} #{{ element?.id }}</div>
  </div>
</template>

<script setup>
defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.board-element {
  min-width: 100px;
  min-height: 60px;
  background: #fff;
  border: 1px solid #bbb;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  padding: 0.5rem;
  position: absolute;
}
.element-meta {
  font-size: 0.7em;
  color: #888;
  margin-top: 0.5em;
}
</style> 