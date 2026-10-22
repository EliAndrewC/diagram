export const meta = {
  name: 'check-wave',
  description: 'A wave of typed checks, one agent per unit, each returning its verdict and its reply',
  whenToUse: 'a wave of 4 or more checks of one defined agent type (feature 383 amendment 7): args {agentType, units: [{label, prompt, then?: [{agentType, prompt}]}]}',
  phases: [{ title: 'Checks' }, { title: 'Verify' }],
}
// WHY A WORKFLOW (feature 383 amendment 7, research R20): every agent launched by hand wakes the main session when it finishes,
// and each wake re-reads the whole context - 5,544 wakes a month at a median 405k tokens. A workflow staggers its launches by
// itself (each later one reads the agent file's prefix from the cache) and reports once. `agentType` on every call: the
// workflow's default subagent loads every CLAUDE.md and every tool (~35k written per launch), the typed one its own small file.
// The Workflow guard (scripts/hooks/workflow-hooks.sh) puts every prompt this run can launch - each unit, and each verify step
// its unit declares - through the same per-dispatch guards a hand launch meets, before the run starts.
const REPLY = {
  type: 'object',
  properties: {
    label: { type: 'string', description: 'the unit label you were given' },
    verdict: { type: 'string', description: 'your verdict word(s), as your contract names them' },
    text: { type: 'string', description: 'your whole reply, exactly as you would have written it, EDIT blocks included' },
  },
  required: ['label', 'verdict', 'text'],
}
if (!args || !args.agentType || !Array.isArray(args.units) || args.units.length === 0) {
  throw new Error('check-wave needs args {agentType: "<defined agent>", units: [{label, prompt}, ...]}')
}
const run = (type, prompt, label, phase) => agent(prompt, { agentType: type, label, phase, schema: REPLY })
// The follow-up stages (FR-043), so the session sees one finished result:
// 1. a FAILED unit - null: its agent died after the tool's retries, or was skipped (a schema miss is retried by the tool) - is
//    re-launched ONCE with the same prompt, already guarded, which pairs to the same dispatch;
// 2. each verify step the unit DECLARED runs after it, its declared prompt (guarded at the run's start) followed by the reply
//    before it, as data. A step is never built from a reply: a prompt made mid-run could not be guarded.
const verify = async (got, u) => {
  if (!got) return null
  const then = []
  let before = got
  for (const [k, step] of (u.then || []).entries()) {
    const prompt = `${step.prompt}\n\nThe reply of the ${k ? u.then[k - 1].agentType : args.agentType} check before you:\n${before.text}`
    const r = await run(step.agentType, prompt, `${u.label} / ${step.agentType}`, 'Verify')
    then.push(r || { label: u.label, verdict: 'NO REPLY', text: '' })
    if (!r) break
    before = r
  }
  return { ...got, then }
}
const replies = await pipeline(
  args.units,
  u => run(args.agentType, u.prompt, u.label, 'Checks'),
  (got, u) => got || run(args.agentType, u.prompt, u.label, 'Checks'),
  verify,
)
const back = replies.filter(Boolean).length
log(`${back} of ${args.units.length} ${args.agentType} unit(s) returned`)
// EACH REPLY CARRIES ITS UNIT'S OWN LABEL (feature 405 T131): an agent echoed 'impl-drift dw3' for dw3, and the reply could not be
// matched to its bundle without a second look
return args.units.map((u, i) => (replies[i] ? { ...replies[i], label: u.label } : { label: u.label, verdict: 'NO REPLY', text: '', then: [] }))
