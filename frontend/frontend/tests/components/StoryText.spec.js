// frontend/tests/components/StoryText.spec.js
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import StoryText from '@/components/narrative/StoryText.vue';

describe('StoryText.vue', () => {
  it('renders story text correctly', () => {
    const text = 'This is a test narrative text.';
    const wrapper = mount(StoryText, {
      props: {
        text,
        character: null,
        animate: false,
      },
    });

    expect(wrapper.text()).toContain(text);
  });

  it('shows character name if provided', () => {
    const wrapper = mount(StoryText, {
      props: {
        text: 'Hi there.',
        character: { name: 'Narrator' },
        animate: false,
      },
    });

    expect(wrapper.html()).toContain('Narrator');
  });
});
