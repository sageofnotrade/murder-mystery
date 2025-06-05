<template>
  <div class="suspect-profile">
    <h3>{{ suspect.name }}</h3>
    <p><strong>Alibi:</strong> {{ suspect.alibi }}</p>
    <p><strong>Motive:</strong> {{ suspect.motive }}</p>
    <p><strong>Description:</strong> {{ suspect.description }}</p>
    <SuspectTraits :traits="suspect.traits" />
  </div>
</template>

<script setup>
import SuspectTraits from './SuspectTraitList.vue';

defineProps({
  suspect: Object
});
</script>

<style scoped>
.suspect-profile {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
