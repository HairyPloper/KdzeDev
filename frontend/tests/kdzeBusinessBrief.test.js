import test from 'node:test'
import assert from 'node:assert/strict'

import {
  isKdzeBusinessWorkflow,
  needsKdzeBusinessBrief
} from '../src/utils/kdzeBusinessBrief.js'

test('recognizes the Kdze workflow by filename', () => {
  assert.equal(isKdzeBusinessWorkflow('Kdze_new_business_idea.yaml'), true)
  assert.equal(isKdzeBusinessWorkflow('yaml_instance/Kdze_new_business_idea.yaml'), true)
  assert.equal(isKdzeBusinessWorkflow('other.yaml'), false)
})

test('rejects command-only launch prompts for the Kdze workflow', () => {
  for (const prompt of ['start', 'Start!', 'run', 'go', 'begin workflow', 'launch it']) {
    assert.equal(needsKdzeBusinessBrief('Kdze_new_business_idea.yaml', prompt), true)
  }
})

test('allows a real brief, an attachment, and other workflows', () => {
  assert.equal(
    needsKdzeBusinessBrief('Kdze_new_business_idea.yaml', 'We are four friends with a €1,000 budget.'),
    false
  )
  assert.equal(needsKdzeBusinessBrief('Kdze_new_business_idea.yaml', 'start', 1), false)
  assert.equal(needsKdzeBusinessBrief('other.yaml', 'start'), false)
})
