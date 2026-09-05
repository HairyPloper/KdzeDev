import test from 'node:test'
import assert from 'node:assert/strict'
import { buildChatExportHtml, openChatExport } from '../src/utils/chatExport.js'

test('exports full messages in order, ignoring cached or truncated rendered HTML', () => {
  const longText = 'First line\n\n' + 'Full paragraph.\n\n'.repeat(500) + 'LAST LINE MUST SURVIVE'
  const html = buildChatExportHtml({ messages: [
    { type: 'dialogue', name: 'User', text: 'Start', isRight: true },
    { type: 'dialogue', name: 'Šomi', text: longText, htmlContent: '<p>Truncated cache</p>' },
    { type: 'dialogue', name: 'Miki', text: '**Final recommendation**' }
  ] })
  assert.ok(html.indexOf('>User<') < html.indexOf('>Šomi<'))
  assert.ok(html.indexOf('>Šomi<') < html.indexOf('>Miki<'))
  assert.equal((html.match(/Full paragraph\./g) || []).length, 500)
  assert.ok(html.includes('LAST LINE MUST SURVIVE'))
  assert.ok(html.includes('<strong>Final recommendation</strong>'))
  assert.ok(!html.includes('Truncated cache'))
})

test('escapes untrusted titles, names, notifications and raw HTML', () => {
  const html = buildChatExportHtml({ workflow: '</title><script>alert(1)</script>', messages: [
    { type: 'warning', message: '<img src=x onerror=alert(1)>' },
    { type: 'dialogue', name: '<script>name</script>', text: '<script>body</script>\n[bad](javascript:alert(1))', avatar: 'javascript:alert(1)' }
  ] })
  assert.ok(!html.includes('<script>'))
  assert.ok(!html.includes('<img src=x'))
  assert.ok(!html.includes('href="javascript:'))
  assert.ok(!html.includes('src="javascript:'))
  assert.ok(html.includes('&lt;script&gt;body&lt;/script&gt;'))
})

test('includes loaded artifacts and marks unfinished messages and missing images', () => {
  const html = buildChatExportHtml({ baseUrl: 'http://localhost:5173/launch', messages: [
    { type: 'dialogue', name: 'Pepi', isArtifact: true, isImage: true, dataUri: 'data:image/png;base64,AAAA', fileName: 'design.png', avatar: '/sprites/a.png' },
    { type: 'dialogue', name: 'Koki', isArtifact: true, fileName: 'plan.txt' },
    { type: 'dialogue', name: 'Ceki', isLoading: true, loadingEntries: [{ label: 'Review', status: 'running' }] },
    { type: 'dialogue', name: 'Pepi', isArtifact: true, isImage: true, fileName: 'pending.png' },
    { type: 'error', message: 'Connection failed' }
  ] })
  assert.ok(html.includes('http://localhost:5173/sprites/a.png'))
  assert.ok(html.includes('data:image/png;base64,AAAA'))
  assert.ok(html.includes('Attachment: plan.txt'))
  assert.ok(html.includes('In progress when exported'))
  assert.ok(html.includes('image not loaded at export time'))
  assert.ok(html.includes('Connection failed'))
})

test('reports blocked popups without throwing', () => {
  globalThis.window = { location: { href: 'http://localhost:5173' }, open: () => null }
  try { assert.equal(openChatExport({ messages: [] }), false) }
  finally { delete globalThis.window }
})

test('opens a snapshot without automatically printing or mutating the chat', async () => {
  let html, click, prints = 0
  const button = { disabled: false, addEventListener: (event, callback) => { click = callback } }
  const view = { opener: {}, focus() {}, print() { prints++ }, document: {
    open() {}, write(value) { html = value }, close() {},
    getElementById() { return button }, images: [], fonts: { ready: Promise.resolve() }
  } }
  const messages = [{ type: 'dialogue', name: 'Viki', text: 'Full brief' }]
  globalThis.window = { location: { href: 'http://localhost:5173' }, open: () => view }
  try {
    assert.equal(openChatExport({ messages }), true)
    assert.equal(view.opener, null)
    assert.equal(prints, 0)
    messages[0].text = 'Updated after export'
    assert.ok(html.includes('Full brief'))
    assert.ok(!html.includes('Updated after export'))
    await click()
    assert.equal(prints, 1)
    assert.equal(button.disabled, false)
  } finally { delete globalThis.window }
})
