<template>
  <div class="suspect-element">
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
const emit = defineEmits(['delete']);

defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.suspect-element {
  background: linear-gradient(to bottom, #ffe0e0, #fff1f1);
  border: 2px dashed #d33;
  box-shadow: 3px 5px 10px rgba(0, 0, 0, 0.1);
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
  transition: transform 0.2s ease-in-out;
}

.suspect-element:hover {
  transform: scale(1.02);
  z-index: 20;
}

.delete-button {
  position: absolute;
  top: 0.4em;
  right: 0.4em;
  background-color: #f88;
  border: none;
  border-radius: 50%;
  width: 1.4em;
  height: 1.4em;
  font-size: 0.8em;
  font-weight: bold;
  color: white;
  cursor: pointer;
  box-shadow: 0 1px 2px #aaa;
  z-index: 3;
}

.delete-button:hover {
  background-color: #d33;
}

.element-header {
  font-weight: bold;
  font-size: 1em;
  color: #b22222;
  border-bottom: 1px dashed #d33;
  padding-bottom: 0.3em;
  margin-bottom: 0.3em;
}

.element-body p {
  font-size: 0.9em;
  color: #4b1f1f;
  margin: 0;
}

.element-footer {
  font-size: 0.8em;
  color: #888;
  margin-top: auto;
  text-align: right;
}

.suspect-element:hover,
.clue-element:hover,
.note-element:hover,
.location-element:hover {
  transform: scale(1.02);
  z-index: 20;
  transition: transform 0.2s ease-in-out;
}
</style>
