<template>
  <div class="suspect-traits">
    <h4>Traits</h4>
    <ul>
      <li v-for="(trait, index) in traits" :key="index">{{ trait }}</li>
    </ul>
  </div>
</template>

<script setup>
defineProps({
  traits: {
    type: Array,
    default: () => [],
  }
});
</script>

<style scoped>
.suspect-traits {
  margin-top: 1rem;
}
.suspect-traits h4 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
}
.suspect-traits ul {
  list-style-type: disc;
  margin-left: 1.5rem;
}
</style>
