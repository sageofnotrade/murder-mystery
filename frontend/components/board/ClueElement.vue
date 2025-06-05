<template>
  <div class="clue-element">
    <button class="delete-button" @click.stop="emit('delete', element.id)">×</button>
    <img
      :src="defaultImage"
      alt="Clue image"
      class="element-photo"
    />
    <div class="element-header">Clue</div>
    <div class="element-body">
      <p>{{ element?.description || 'clue' }}</p>
    </div>
    <div class="element-footer">clue #{{ element?.id }}</div>
  </div>
</template>

<script setup>
import defaultImage from '../../../assets/clue/clue-default.jpg';
const emit = defineEmits(['delete'])

defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.clue-element {
  background-color: #e0f0ff;
  border: 2px dashed #339;
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

.clue-element:hover {
  transform: scale(1.02);
  z-index: 20;
}

.delete-button {
  position: absolute;
  top: 4px;
  right: 6px;
  border: none;
  background: rgb(204, 228, 251); /* original light blue bg */
  color: #004080; /* original dark blue X */
  font-weight: bold;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  line-height: 16px;
  font-size: 14px;
  cursor: pointer;
  z-index: 3;
}

.delete-button:hover {
  background-color: #339;
  color: white;
}

.element-header {
  font-weight: bold;
  font-size: 1em;
  color: #004080;
  border-bottom: 1px dashed #339;
  padding-bottom: 0.3em;
  margin-bottom: 0.3em;
}

.element-body p {
  font-size: 0.9em;
  color: #1c3b4b;
  margin: 0;
}

.element-footer {
  font-size: 0.8em;
  color: #888;
  margin-top: auto;
  text-align: right;
}

.element-photo {
  width: 100%;
  height: 5em; /* or 4em if 5em still pushes it */
  object-fit: cover;
  border-radius: 6px;
  margin-bottom: 0.5em;
  display: block;
}
</style>
