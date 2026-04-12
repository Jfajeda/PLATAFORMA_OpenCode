# AGENTS.md — PLATAFORMA_OpenCode

> Instructions for AI coding agents operating in this repository.
> Maintained by Jafa, S.L. (CODANOR), Barcelona, Catalunya.

## Project Overview

This repository contains documentation and tooling for the OpenCode platform
used internally at CODANOR. It currently includes an HTML-based user manual
and may grow to include additional utilities, scripts, or web assets.

## Build / Lint / Test Commands

No build system is currently configured. When one is added, update this section.

```bash
# Build (placeholder — update when a build tool is configured)
# npm run build

# Lint (placeholder)
# npm run lint

# Run all tests (placeholder)
# npm test

# Run a single test file (placeholder)
# npm test -- path/to/test.spec.ts

# Type-check (placeholder)
# npx tsc --noEmit
```

## Repository Structure

```
PLATAFORMA_OpenCode/
  AGENTS.md                          # This file — agent instructions
  Manual_OpenCode_Codanor.html       # Corporate HTML manual (Codanor branding)
```

## Code Style Guidelines

### Language & Encoding

- All source files must use **UTF-8** encoding.
- Comments and documentation should be written in **Spanish** unless the
  surrounding codebase or library convention requires English.

### Formatting

- **Indentation**: 2 spaces (no tabs).
- **Line length**: max 100 characters for code, 80 for markdown/comments.
- **Trailing whitespace**: remove it.
- **Final newline**: every file must end with exactly one newline.
- **Semicolons** (JS/TS): always use them.
- **Quotes** (JS/TS): prefer single quotes (`'`) for strings; use backticks
  for template literals only when interpolation is needed.

### Naming Conventions

| Element            | Convention         | Example                |
| ------------------ | ------------------ | ---------------------- |
| Files/directories  | kebab-case         | `user-profile.ts`     |
| Variables/funcs    | camelCase          | `getUserName()`        |
| Constants          | UPPER_SNAKE_CASE   | `MAX_RETRY_COUNT`      |
| Classes/types      | PascalCase         | `UserProfile`          |
| CSS classes        | kebab-case / BEM   | `card__title--active`  |
| HTML IDs           | camelCase          | `sidebarNav`           |
| Env variables      | UPPER_SNAKE_CASE   | `DATABASE_URL`         |

### Imports (JS/TS)

- Group imports in this order, separated by a blank line:
  1. Node built-ins (`fs`, `path`, `http`)
  2. External packages (`react`, `express`)
  3. Internal aliases / modules (`@/utils`, `@/components`)
  4. Relative imports (`./helpers`, `../types`)
- Use named imports; avoid wildcard (`* as`) unless required.
- Never use `require()` in TypeScript files.

### TypeScript

- Prefer `interface` over `type` for object shapes.
- Avoid `any`; use `unknown` when the type is truly unknown.
- Export types/interfaces that are consumed by other modules.
- Use `readonly` for properties that should not be mutated.
- Use strict mode (`"strict": true` in tsconfig).

### Error Handling

- Always catch errors at the boundary (API handler, event listener, main).
- Use typed/custom error classes when multiple error kinds exist.
- Never swallow errors silently — at minimum, log them.
- Async functions: prefer `try/catch` over `.catch()` chains.
- Return early on error conditions to reduce nesting.

### HTML / CSS

- Use semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<section>`).
- Follow the CODANOR brand palette:
  - Primary: `#178DC2`
  - Accent: `#12A79D`
  - Fonts: Poppins (headings), Nunito Sans (body), Muli (alt).
- Keep CSS specificity low; prefer class selectors over IDs.
- Use CSS custom properties for colors and spacing tokens.

### Git Practices

- Branch names: `feature/short-description`, `fix/issue-number`.
- Commit messages: imperative mood, max 72 chars for the subject line.
  Example: `Add user authentication endpoint`.
- Keep commits atomic — one logical change per commit.
- Do not commit secrets, `.env` files, or credentials.

## Agent-Specific Instructions

### Context Management

- This workspace may be used with long-running OpenCode sessions. If the
  conversation grows large, suggest `/compact` or starting a new session.
- When creating or editing HTML files, preserve CODANOR corporate branding.

### File Operations

- Prefer editing existing files over creating new ones.
- Never overwrite `Manual_OpenCode_Codanor.html` without explicit user consent.
- When generating new documentation, use the same branding and styles.

### Communication

- Respond in **Spanish** unless the user switches to another language.
- Be concise; avoid unnecessary praise or filler.
- Reference specific file paths and line numbers when discussing code.

### Performance

- Avoid scanning the entire filesystem; target specific directories.
- Use `/compact` if the session history causes slowness or API errors.
- For large tasks, break work into smaller steps using a todo list.

## External Rules

No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md`
files exist in this repository. When any are added, incorporate their
contents into this section.

---

*Last updated: 2026-04-01*
