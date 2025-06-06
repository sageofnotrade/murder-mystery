<template>
  <div class="suspect-element">
  <img
  :src="element?.imageUrl || defaultImage"
  alt="Suspect Image"
  class="suspect-photo"
/>
    <button class="delete-button" @click.stop="emit('delete', element.id)">×</button>
    <div class="element-header">{{ element?.name || 'Unnamed Suspect' }}</div>
    <div class="element-body">
      <p><strong>Motive:</strong> {{ element?.motive || 'N/A' }}</p>
      <p><strong>Alibi:</strong> {{ element?.alibi || 'N/A' }}</p>
    </div>
    <div class="element-footer">#{{ element?.id }}</div>
  </div>
</template>


<script setup>
import defaultImage from '../../../assets/suspect/suspect-default.jpg';
const emit = defineEmits(['delete']);

defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.suspect-element {
  bbackground: linear-gradient(to bottom, #ffe0e0, #fff1f1);
  border: 2px dashed #d33;
  box-shadow: 2px 4px 6px rgba(0, 0, 0, 0.08);
  font-family: 'Courier New', Courier, monospace;
  padding: 1em;
  padding-top: 2em;
  border-radius: 12px;
  position: absolute;
  width: 12em;
  height: 10em;
  min-width: 10em;
  min-height: 8em;
  max-width: 20em;
  max-height: 20em;
  resize: both;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0.3em;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.suspect-photo {
  width: 100%;
  height: 5em;
  object-fit: cover;
  border-radius: 6px;
  margin-bottom: 0.5em;
} 

.suspect-element:hover {
  transform: scale(1.02);
  box-shadow: 4px 6px 12px rgba(0, 0, 0, 0.12);
  z-index: 20;
}

.delete-button {
  position: absolute;
  top: 0.4em;
  right: 0.4em;
  background-color: #ffd4d4;
  border: none;
  border-radius: 50%;
  width: 1.4em;
  height: 1.4em;
  font-size: 0.8em;
  font-weight: bold;
  color: #a00;
  cursor: pointer;
  box-shadow: 0 1px 2px #aaa;
  z-index: 3;
}

.delete-button:hover {
  background-color: #fbb;
  color: #700;
}

.element-header {
  font-weight: bold;
  font-size: 0.95em;
  color: #b22222;
  border-bottom: 1px dashed #d33;
  padding-bottom: 0.2em;
  margin-bottom: 0.2em;
}

.element-body p {
  font-size: 0.85em;
  color: #4b1f1f;
  margin: 0.2em 0;
}

.element-footer {
  font-size: 0.8em;
  color: #888;
  margin-top: auto;
  text-align: right;
}

</style>
