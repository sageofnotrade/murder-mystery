<template>
  <div class="note-element">
    <slot>Note</slot>
    <div class="element-meta">{{ element?.type }} #{{ element?.id }}</div>
  </div>
</template>

<script setup>
defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.note-element {
  min-width: 120px;
  min-height: 70px;
  background: #f3e5f5;
  border: 2px solid #8e24aa;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(142,36,170,0.08);
  padding: 0.5rem;
  position: absolute;
}
.element-meta {
  font-size: 0.7em;
  color: #8e24aa;
  margin-top: 0.5em;
}
</style> 