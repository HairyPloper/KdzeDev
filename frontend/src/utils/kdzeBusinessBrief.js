export const KDZE_BUSINESS_WORKFLOW = 'Kdze_new_business_idea.yaml'

export const KDZE_BRIEF_TEMPLATE = `Describe the real Kdze founders:
- Team members and each person's skills/interests
- Shared test budget and currency
- Available hours per person each week
- Location and intended customer market
- Resources you already have
- What you enjoy and want to avoid`

export function isKdzeBusinessWorkflow(workflowFile = '') {
  const filename = String(workflowFile).replaceAll('\\', '/').split('/').pop()
  return filename === KDZE_BUSINESS_WORKFLOW
}

export function needsKdzeBusinessBrief(workflowFile, prompt, attachmentCount = 0) {
  if (!isKdzeBusinessWorkflow(workflowFile) || attachmentCount > 0) {
    return false
  }

  const text = String(prompt || '').trim()
  const isCommandOnly = /^(start|run|go|begin|launch)(?:\s+(?:it|workflow|the workflow))?[.!]?$/i.test(text)
  const hasPlaceholder = /[\[<]\s*(?:amount|currency|budget|number|insert\b|your\b)[^\]>]*[\]>]/i.test(text)
  return isCommandOnly || hasPlaceholder
}
