# Screenshot intake (owner supplies SOLIDWORKS screenshots, unlabeled) — from 2026-11-08

Replaces most video watching (W2–W11, H). The owner clicks through SOLIDWORKS and sends batches of
screenshots; the transcripts (`docs/swref/triage/`, cached in the browser) give the workflows/order.

## Owner side (suggested, not required)
- One batch per topic if convenient; labels/names are NOT needed.
- For each action: the moment the command is started (left PM + top CommandManager), one with options
  expanded/changed, and one showing the result/preview in the part. Flyouts, tooltips, right-click
  menus, dialogs and Options pages open. Zoomed crops of icon strips welcome.
- Classic (non-Simplified) layout gives the closest match to the 2020 course.

## Claude side per batch
1. Look at every image once; identify it (command, panel, state) from the picture + transcript context.
2. Store files locally in `dev/refshots/<topic>/` (git-ignored, never committed or pushed).
3. Write `docs/swref/screens/<topic>.md`: per image — what it shows (literal: title, buttons, every
   group in order, labels, defaults, checked/greyed state, icon descriptions, message text, graphics
   preview: colours, handles, callouts) + transcript timestamp that explains the workflow.
4. Icon strips: list each icon (position, meaning) in `docs/swref/icons.md`; FreeWorks icons are
   redrawn originals (same size/position/meaning), never copies.
5. Update catalogue files `docs/swref/0x_*.md` with `[S]` tags; list gaps still needing a screenshot.
6. Commit text notes only; push.
