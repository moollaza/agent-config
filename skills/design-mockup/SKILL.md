---
name: design-mockup
description: >
  Generate self-contained HTML mockups for design review and serve them locally with clickable URLs.
  Use this skill whenever the user wants to visualize a design before implementing it, review UI states,
  compare layout options, or get sign-off on a proposed design. Triggers on phrases like "create mockups",
  "mock up", "show me what it looks like", "preview the design", "html mockup", "generate mockups",
  "let me see it first", "design preview", or any request to visualize proposed UI changes before coding them.
  Also use proactively when a design task is complex enough that visual review would prevent wasted iteration —
  mockups are cheap, implementation rework is expensive.
---

# Design Mockup

Generate high-fidelity HTML mockups for design review, serve them locally, and
get sign-off before writing production code.

Design iteration in code is slow and expensive. A mockup you can click through
in a browser takes minutes to create and saves hours of implementation rework.
This skill front-loads visual alignment so that by the time you write real code,
the design is already approved.

## Workflow

### Phase 1: Understand the Work, Then the Design System

This phase has three steps in order. The goal is to extract only the design
system knowledge that's relevant to what you're actually mocking up.

**Step 1: Understand the work context.** Read the source files that will be
changed — components, pages, layouts. Look at screenshots if the user provided
them. Understand what the mockup needs to represent: is it a form? a settings
page? a dashboard? an action panel? What UI primitives does it need — buttons,
cards, inputs, banners, tabs, modals?

**Step 2: Discover the global design system.** Now scan the project for its
design language. The goal is to build a picture of the project's conventions:

- Tailwind config (`tailwind.config.*`, `app.css`, CSS custom properties) for
  custom color tokens, spacing scale, font scale
- Existing components in the UI/shared directory — what's already built?
- Patterns across the codebase — what border-radius do buttons use? cards?
  How many distinct button treatments exist? What are the container patterns?

Don't try to catalog everything. Focus on understanding the vocabulary.

**Step 3: Extract what's relevant.** Based on what the mockup needs (Step 1)
and what the project provides (Step 2), pull the specific tokens and patterns
that apply:

- If the mockup has buttons, extract the project's button classes and variants
- If it has cards, extract the card/container patterns
- If it uses color for status (green = success, red = error), extract those
  specific color tokens
- If it has forms, look at how existing inputs and labels are styled

Build a `tailwind.config` block containing only the tokens the mockup needs.
This keeps the config focused and the mockup honest — it uses real project
tokens, not generic Tailwind defaults.

**Read the actual component markup** for class patterns and structure. The
mockup should mirror real patterns — if the project uses `flex items-center
gap-3` for action rows, the mockup should too. If there's a shared `Button`
component with specific classes, use those classes.

### Phase 2: Align on States

Before rendering a single pixel, present a **state matrix** to the user.

```markdown
## State Matrix — [Feature Name]

| State | Description | Notes |
|-------|-------------|-------|
| Idle | Default, no action taken | Main CTA visible |
| Loading | Action in progress | Spinner, disabled buttons |
| Success | Action completed | Flash message, updated status |
| Error | Something went wrong | Error banner, retry option |
| Empty | No data yet | Empty state illustration |
| Mobile | All states at small viewport | Verify stacking/wrapping |
```

Ask the user to confirm the state list before proceeding. This is the cheapest
possible checkpoint — a few lines of text that prevent hours of "you missed
this state" iteration later.

If the user wants **options mode**, list the alternative design directions
instead:

```markdown
## Design Options — [Feature Name]

| Option | Approach | Key Tradeoff |
|--------|----------|--------------|
| A — Compact | Dense layout, less whitespace | Fits more on screen, feels tighter |
| B — Spacious | Generous padding, clear hierarchy | Cleaner, but more scrolling |
| C — Flat | No cards, divider-separated rows | Simpler, but less visual grouping |
```

### Phase 3: Generate Mockups

Create self-contained HTML files in `.mockups/`. Each file includes the Tailwind
CDN with the extracted project tokens.

**Every mockup file uses this skeleton:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Project] — [State/Option Name]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            // Extracted from project — use real token names
          }
        }
      }
    }
  </script>
</head>
<body class="bg-white text-gray-900">
  <!-- Mockup content -->
</body>
</html>
```

**Quality guidelines:**

- **Use the project's real tokens.** If the project has `qb-green-700` for
  primary buttons, use that — not generic `green-600`.
- **Show real content, not lorem ipsum.** Realistic copy, data, and labels.
- **Include interactive states.** Simple `onclick` toggles for expand/collapse,
  confirm/cancel, show/hide. Keep it minimal — inline JS, no frameworks.
- **Use stable filenames.** `active-healthy.html`, `setup-step-1.html`,
  `option-a-compact.html`. These persist across iterations so browser refresh
  shows the update.
- **Match responsive behavior, not just width.** Mockups at mobile/tablet
  breakpoints must reflect the real app's responsive changes — not just the
  desktop layout in a narrow container. Extract the project's actual responsive
  patterns:
  - **Navigation:** If the app uses a hamburger menu, bottom nav, or drawer at
    mobile widths, the mockup must show that — not the desktop nav bar.
  - **Font sizes:** Extract the project's responsive typography scale (e.g.,
    `text-2xl md:text-4xl` for headings) and apply it. Don't use desktop font
    sizes at mobile widths.
  - **Layout shifts:** Sidebar-to-stacked, grid column changes, hidden elements
    — mirror what the real app does at each breakpoint.

### Phase 4: Choose the Right Viewer Layout

Two defaults cover most cases. Compose other variants (filmstrips, flow
storyboards) only when the work clearly demands them.

#### Tabbed States + Desktop/Mobile Toggle (default)

Best for: **coverage mode** — the standard combination for state review.

Generate a single HTML file with tabs across the top, one tab per state, with
the active tab highlighted and a small pill badge showing the state name. Each
tab swaps the visible content without page navigation.

Inside the tab shell, add a sticky toggle bar with buttons: "Desktop (1280px)"
/ "Tablet (768px)" / "Mobile (375px)". Clicking resizes the content container
to that width, centered on the page.

**Important:** Each breakpoint must render the real responsive variant, not
just a resized container. At mobile width, show the mobile nav
(hamburger/drawer), mobile typography scale, and mobile layout. Read the
project's responsive classes and media queries to understand what actually
changes at each breakpoint.

#### Side-by-Side Options

Best for: **options mode** — choosing between design directions.

Generate one HTML file with 2-3 alternatives rendered in columns. Each column
has a header with the option name and a brief rationale card explaining the
tradeoff. Columns should be wide enough to read comfortably — use a horizontal
scroll if needed rather than cramming.

Below the columns, include a "Differences" summary listing the specific design
decisions that vary between options (e.g., "Option A uses `rounded-md` buttons,
Option B uses `rounded-lg`").

### Phase 5: Build the Index

The `index.html` landing page ties everything together:

- Brief summary of what's being proposed (what changes, why)
- Links to each mockup page with descriptions
- State coverage checklist (green check / red X per state from the matrix)
- If in coverage mode, show completion percentage

Keep it clean — this is the first thing the user sees.

### Phase 6: A11y Quick Audit

Add a small corner toggle ("A11y Check") that overlays the page with: red
outlines on elements below WCAG AA contrast (4.5:1 text, 3:1 large/icons),
flags on hardcoded non-token colors, tap-target size labels. Best-effort, not
a replacement for axe-core. Keep the implementation a single inline script.

### Phase 7: Serve & Present

Ensure `.mockups/` is in `.gitignore`:

```bash
grep -q '\.mockups' .gitignore 2>/dev/null || echo '.mockups/' >> .gitignore
```

Serve locally:

```bash
npx serve .mockups -l 3333 &
```

If port 3333 is in use, try 3334, 3335, etc.

Tell the user what's available with clickable URLs:

> Mockups are live at **http://localhost:3333**
>
> - [All States (tabbed)](http://localhost:3333/states.html)
> - [Options Comparison](http://localhost:3333/options.html)
> - [Setup Flow](http://localhost:3333/flow-setup.html)
>
> Each page has a desktop/mobile toggle. Click "A11y Check" for contrast audit.

### Phase 8: Iterate

The user reviews in their browser and returns with feedback. Update the mockup
files directly and tell them to refresh — the server is still running.

Use stable filenames so the browser tab stays on the right page after refresh.
Don't regenerate the entire file for a small change — edit surgically.

When the user approves, kill the server and proceed to implementation:

```bash
kill %1 2>/dev/null
```

The approved mockups serve as the design spec — but only if you actually read
them. See Phase 9.

### Phase 9: Implementation Handoff

Before implementing, re-read the approved `.mockups/*.html` files (Read tool,
not memory). Extract DOM hierarchy, exact Tailwind classes, project tokens,
content/copy, interactive states, and responsive behavior. If a different
agent handles implementation, include the file paths in the handoff and state
explicitly that `.mockups/` is the source of truth. Don't approximate.

## Tips

- **Start with the hardest state.** Complex states with nested interactions
  reveal design problems that simple states don't.
- **Don't over-engineer interactivity.** A few `onclick` toggles are great. A
  full SPA is overkill. The point is visual review, not a working prototype.
- **Mirror the project's actual markup patterns** so the transition from mockup
  to implementation is smooth.
- **When in doubt, make more states.** Cheaper to mock up an unnecessary state
  than to discover mid-implementation that you forgot one.
- **The state matrix is non-negotiable.** Never skip Phase 2. The 20-round
  screenshot-tweak nightmare starts from an incomplete state list.
