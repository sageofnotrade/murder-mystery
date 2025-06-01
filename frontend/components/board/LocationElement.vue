<template>
  <div class="location-element">
    <slot>Location</slot>
    <div class="element-meta">{{ element?.type }} #{{ element?.id }}</div>
  </div>
</template>

<script setup>
defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.location-element {
  min-width: 120px;
  min-height: 70px;
  background: #fffde7;
  border: 2px solid #fbc02d;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(251,192,45,0.08);
  padding: 0.5rem;
  position: absolute;
}
.element-meta {
  font-size: 0.7em;
  color: #bfa100;
  margin-top: 0.5em;
}
</style> 