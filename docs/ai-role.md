# AI Role

## Current (skeleton)

Gemini acts as a **chat completion proxy**: it receives the conversation history and generates the next assistant response. This is a **passthrough** role — there is no feedback loop, no adaptation, and no structural AI behavior yet.

### What breaks if AI is removed?

Nothing structural. Without AI, you get a static UI with no responses. The current skeleton exists to wire up the streaming infrastructure.

## Future (to be designed)

The skeleton is a foundation for adding **structural AI behavior** such as:

- Inference under ambiguity (e.g., intent detection)
- Adaptation over time (e.g., learning user preferences)
- Dynamic decision-making (e.g., routing, tool use)

These will be designed and documented here when implemented.
