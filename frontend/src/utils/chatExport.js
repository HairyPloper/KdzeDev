import MarkdownIt from 'markdown-it'

const markdown = new MarkdownIt({ html: false, linkify: true, typographer: true })
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]))

function imageUrl(value, baseUrl) {
  if (!value) return ''
  if (/^data:image\/(png|jpeg|gif|webp);base64,[a-z0-9+/=\s]+$/i.test(value)) return value
  try {
    const url = new URL(value, baseUrl)
    const base = new URL(baseUrl)
    return ['http:', 'https:'].includes(url.protocol) && url.origin === base.origin ? url.href : ''
  } catch { return '' }
}

// Build from full message data, never the collapsed/scrolled UI DOM.
export function buildChatExportHtml({ messages, workflow = '', sessionId = '', status = '',
  exportedAt = new Date().toLocaleString(), baseUrl = 'http://localhost/' }) {
  const transcript = messages.map(message => {
    const timestamp = message.timestamp ? new Date(message.timestamp).toLocaleString() : ''
    if (message.type !== 'dialogue') {
      return `<aside class="notice ${['warning', 'error'].includes(message.type) ? message.type : ''}">
        <p>${escapeHtml(message.message)}</p><time>${escapeHtml(timestamp)}</time></aside>`
    }
    const avatar = imageUrl(message.avatar, baseUrl)
    const artifact = message.isImage ? imageUrl(message.dataUri, baseUrl) : ''
    const activity = (message.loadingEntries || []).map(entry =>
      `<li>${escapeHtml(entry.label)} — ${escapeHtml(entry.status)}</li>`).join('')
    return `<article class="dialogue ${message.isRight ? 'user' : ''}">
      ${avatar ? `<img class="avatar" src="${escapeHtml(avatar)}" alt="">` : ''}
      <div class="bubble"><header><strong>${escapeHtml(message.name)}</strong><time>${escapeHtml(timestamp)}</time></header>
      <div class="message-text">${markdown.render(String(message.text || ''))}</div>
      ${activity ? `<ul class="activity">${activity}</ul>` : ''}
      ${artifact ? `<img class="artifact" src="${escapeHtml(artifact)}" alt="${escapeHtml(message.fileName || 'Image artifact')}">` : ''}
      ${message.isArtifact ? `<p class="file">Attachment: ${escapeHtml(message.fileName || 'File')}${!artifact && message.isImage ? ' (image not loaded at export time)' : ''}</p>` : ''}
      ${message.error ? `<p class="error">${escapeHtml(message.error)}</p>` : ''}
      ${message.isLoading ? '<p class="activity">In progress when exported</p>' : ''}
      ${message.duration ? `<p class="activity">Duration: ${escapeHtml(message.duration)}</p>` : ''}
      </div></article>`
  }).join('\n')

  return `<!doctype html><html lang="en"><head><meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(workflow || 'KdzeDev')} — Chat</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #172122; color: #edf5f3; font: 15px/1.6 system-ui, sans-serif; }
    .toolbar { position: sticky; top: 0; z-index: 1; padding: 14px 24px; background: #213335; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
    button { border: 0; border-radius: 8px; padding: 10px 18px; background: #9ee9ef; color: #10292b; font: inherit; font-weight: 600; cursor: pointer; }
    button:disabled { opacity: .6; cursor: wait; }
    .toolbar span { font-size: 13px; }
    main { max-width: 1000px; padding: 28px; margin: auto; }
    h1 { font-size: 26px; overflow-wrap: anywhere; margin-bottom: 8px; }
    .metadata { color: #b7cdca; margin-bottom: 30px; overflow-wrap: anywhere; }
    .dialogue { display: flex; align-items: flex-start; gap: 14px; margin: 24px 0; }
    .avatar { width: 42px; height: 56px; object-fit: contain; image-rendering: pixelated; }
    .bubble { background: #263335; border: 1px solid #49625f; border-radius: 12px; padding: 18px 22px; min-width: 0; flex: 1; }
    .user .bubble { background: #233f3a; border-color: #67a295; }
    header { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: baseline; margin-bottom: 12px; }
    header strong { color: #a8eef0; font-size: 17px; }
    time, .activity, .file { font-size: 12px; color: #b7cdca; }
    p { margin: 0 0 12px; }
    .message-text { overflow: visible; overflow-wrap: anywhere; }
    .message-text > :last-child { margin-bottom: 0; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #182224; padding: 14px; border-radius: 6px; }
    code { font-size: 12px; }
    table { width: 100%; table-layout: fixed; border-collapse: collapse; margin: 14px 0; }
    th, td { border: 1px solid #5b7370; padding: 7px; overflow-wrap: anywhere; }
    blockquote { margin-left: 0; padding-left: 16px; border-left: 3px solid #87c7bf; }
    a { color: #a8eef0; overflow-wrap: anywhere; }
    img { max-width: 100%; height: auto; }
    .artifact { display: block; margin: 12px 0; }
    .notice { border-left: 3px solid #547a72; padding: 8px 14px; margin: 16px 0; overflow-wrap: anywhere; }
    .notice p { white-space: pre-wrap; margin: 0; }
    .warning { border-color: #d8ba62; } .error { color: #ffc1bd; border-color: #e9968f; }
    @page { size: A4; margin: 14mm; }
    @media print {
      body { background: white; color: #182a2c; font-size: 10pt; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .toolbar { display: none !important; }
      main { max-width: none; padding: 0; }
      .dialogue { display: block; position: relative; margin: 16px 0; }
      .avatar { float: left; width: 28px; height: 38px; margin: 12px 10px 0 0; }
      .bubble, .user .bubble { margin-left: 38px; background: #f3f7f6; color: #182a2c; border-color: #c2d4d0; border-radius: 6px; box-decoration-break: clone; -webkit-box-decoration-break: clone; }
      header { break-after: avoid; }
      header strong, a { color: #165c57; }
      time, .metadata, .activity, .file { color: #475e5c; }
      pre { background: #e7eeec; }
      .error { color: #9a2929; }
      tr, img { break-inside: avoid; }
      .artifact, .message-text img { max-height: 245mm; object-fit: contain; }
      p { orphans: 3; widows: 3; }
      th, td { border-color: #a8bdb9; }
    }
  </style></head><body>
    <nav class="toolbar"><button id="print-chat" type="button">Print / Save as PDF</button>
      <span>All messages expanded. Choose “Save as PDF” in the print dialog.</span></nav>
    <main><h1>${escapeHtml(workflow || 'KdzeDev chat')}</h1>
      <div class="metadata">Session: ${escapeHtml(sessionId || 'Not assigned')}<br>
      Status: ${escapeHtml(status)} · Exported: ${escapeHtml(exportedAt)}<br>
      ${messages.length} messages · Snapshot of the chat at export time</div>
      ${transcript || '<p>No messages to export.</p>'}
    </main></body></html>`
}

export function openChatExport(options) {
  const html = buildChatExportHtml({ ...options, baseUrl: window.location.href })
  const view = window.open('', '_blank')
  if (!view) return false
  view.opener = null
  view.document.open()
  view.document.write(html)
  view.document.close()
  const button = view.document.getElementById('print-chat')
  button.addEventListener('click', async () => {
    button.disabled = true
    try {
      // Give already-rendered images/fonts time to finish before pagination.
      const images = [...view.document.images].map(img => img.complete ? Promise.resolve() :
        new Promise(resolve => { img.addEventListener('load', resolve, { once: true }); img.addEventListener('error', resolve, { once: true }) }))
      let timeout
      await Promise.race([
        Promise.all([view.document.fonts.ready, ...images]),
        new Promise(resolve => { timeout = setTimeout(resolve, 5000) })
      ])
      clearTimeout(timeout)
      view.focus()
      view.print()
    } finally { button.disabled = false }
  })
  return true
}
