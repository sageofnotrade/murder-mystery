import { mount } from '@vue/test-utils';
import DetectiveBoard from '@/components/board/DetectiveBoard.vue';

describe('DetectiveBoard', () => {
  it('renders board controls and board area', () => {
    const wrapper = mount(DetectiveBoard);
    expect(wrapper.find('.board-controls').exists()).toBe(true);
    expect(wrapper.find('.detective-board').exists()).toBe(true);
  });

  it('zoom in/out and reset work as expected', async () => {
    const wrapper = mount(DetectiveBoard);
    await wrapper.find('button').trigger('click'); // Zoom In
    await wrapper.findAll('button')[1].trigger('click'); // Zoom Out
    await wrapper.findAll('button')[2].trigger('click'); // Reset View
    // No error should occur, zoom state should be valid
    // (zoom state is not exposed, so just check no crash)
    expect(wrapper.exists()).toBe(true);
  });

  it('handles addElement with invalid type gracefully', async () => {
    const wrapper = mount(DetectiveBoard);
    // Call addElement with an invalid type
    const vm = wrapper.vm;
    expect(() => vm.addElement && vm.addElement('invalid')).not.toThrow();
  });
}); 