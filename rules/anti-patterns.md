# AI Anti-Patterns

To maintain high engineering quality and avoid common AI failure modes, follow these "Wrong vs. Right" patterns.

## Interaction Patterns

| Anti-Pattern | Wrong Behavior | Right Behavior |
| :--- | :--- | :--- |
| **Serial Interrogation** | Asking 3+ questions one by one in separate turns. | Batch questions into a single turn; provide a "Best Guess" for each to keep momentum. |
| **Scope Creep** | Adding "while I'm at it" features or refactors not requested. | Stick to the requested scope. If a refactor is needed for the fix, state it and get approval. |
| **Yes-Man Syndrome** | Blindly following a user's technical suggestion even if it's flawed. | Challenge the user if their approach is risky or non-standard. Offer a better alternative. |
| **The "Maybe" Loop** | Using hedging language like "You might want to," "It could be," "Perhaps." | Take a position. Give a direct recommendation based on evidence. |
| **Shadow Scaffolding** | Writing boilerplate or placeholder code "to be filled later." | Every line of code must be functional and necessary. No TODOs or TBDs in final output. |

## Technical Patterns

| Anti-Pattern | Wrong Behavior | Right Behavior |
| :--- | :--- | :--- |
| **Memory-Based Coding** | Writing code or citing versions based on training data. | Always `grep`, `cat`, or run a version command first. Verify current project state. |
| **Symptom Patching** | Fixing the error message without finding the root cause. | Run `/hunt`. Do not touch code until the root cause is stated and verified. |
| **Blind Chaining** | Auto-starting the next skill without user intervention. | Every skill transition is manual. Output the "Next Steps" and wait for approval. |
| **Tool Avoidance** | Explaining what a tool *might* do instead of just running it. | Run the tool. Show the output. Act on reality, not theory. |
| **Context Overload** | Reading 10+ files at once to "understand the project." | Targeted reading. Use `grep` to find entry points, then read specific functions. |

## Documentation Patterns

| Anti-Pattern | Wrong Behavior | Right Behavior |
| :--- | :--- | :--- |
| **Yapper Mode** | Writing long paragraphs explaining simple code changes. | Use concise bullet points. Let the code (or diff) speak for itself. |
| **Placeholders** | Using `// ... existing code ...` in a way that breaks copy-pasting. | Provide a clean, contiguous block or a clear diff that the user can apply easily. |
| **Implicit Assumptions** | Assuming the user's environment (OS, shell, paths) is standard. | Always check `pwd` and OS context before proposing commands. |

---

> [!TIP]
> When you catch yourself falling into an anti-pattern, stop immediately, acknowledge it, and pivot to the "Right Behavior."
