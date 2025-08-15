import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RuleCreator from '@/components/game/RuleCreator.vue'

describe('RuleCreator', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render rule creation form', () => {
    const wrapper = mount(RuleCreator)
    expect(wrapper.find('input[placeholder*="规则名称"]').exists()).toBe(true)
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('should emit create event with rule data', async () => {
    const wrapper = mount(RuleCreator)
    
    // 填写表单
    await wrapper.find('input').setValue('测试规则')
    await wrapper.find('textarea').setValue('测试描述')
    
    // 提交表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 检查事件
    expect(wrapper.emitted()).toHaveProperty('create')
  })
})
