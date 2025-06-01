<template>
  <div class="suspect-element">
    <slot>Suspect</slot>
    <div class="element-meta">{{ element?.type }} #{{ element?.id }}</div>
  </div>
</template>

<script setup>
defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.suspect-element {
  min-width: 120px;
  min-height: 70px;
  background: #ffe0e0;
  border: 2px solid #d33;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(200,0,0,0.08);
  padding: 0.5rem;
  position: absolute;
}
.element-meta {
  font-size: 0.7em;
  color: #a00;
  margin-top: 0.5em;
}
</style> 