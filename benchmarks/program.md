# Agent Improvement Program

## Objective
Improve agent benchmark scores through systematic prompt engineering.
Each iteration proposes one focused change to an agent's system prompt,
evaluates the impact, and keeps or reverts based on measurable improvement.

## Strategies to try (in priority order)

### High impact
- Add explicit output structure instructions (what sections to include)
- Add tool-use guidance (when to call which tool, in what order)
- Add few-shot examples for common task patterns
- Clarify the agent's decision-making criteria

### Medium impact
- Add domain-specific terminology and best practices
- Improve edge case handling (ambiguous inputs, missing data)
- Add quality self-check instructions ("before responding, verify...")
- Refine tone/voice for the target audience

### Lower impact
- Reorder existing instructions by importance
- Remove redundant or contradictory instructions
- Tighten language (fewer words, same meaning)

## Constraints
- Only modify the `system_prompt` property return value
- Keep prompts under 2000 tokens (avoid bloat that hurts focus)
- Maintain the agent's core identity and role description
- Don't add instructions that conflict with BaseAgent behavior
- Don't add tool definitions in the prompt (tools are injected separately)
- Each iteration should make ONE focused change, not multiple

## What NOT to do
- Don't add "you are the best" style motivation prompts
- Don't repeat the tool schemas in the prompt
- Don't add extremely specific rules that only apply to one edge case
- Don't make the prompt so long that the model loses focus on key instructions
