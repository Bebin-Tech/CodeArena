# CodeArena interface foundation

Dark-first, developer-focused identity. Tokens are centralized in `frontend/app/globals.css`: charcoal canvas, layered neutral surfaces, violet primary actions, blue informational accents, green confirmations, rose errors. The identity uses a terminal mark and compact typography; no external font request is required.

Reusable primitives include the shadcn-style Radix Slot button with class-variance-authority variants, labeled form fields, password visibility control, alerts, status labels, workspace panels, loading skeleton, empty/error states and skip navigation. `components.json` records the shadcn configuration. Tailwind v4 is available alongside semantic component styles.

Typography hierarchy: 10px mono eyebrows, 12–14px interface content, 17–23px panel titles, 30–35px page headings, responsive landing display type. Spacing follows a 4px base with 12–30px component padding and 7–12px corner radii. Borders separate surfaces; motion is subtle and respects reduced-motion preferences.

Keyboard focus is visible. Labels are programmatically associated, field errors use `aria-describedby` and `aria-invalid`, success/errors announce through status/alert roles. Buttons expose pending states. Layout collapses to one column at 760px; the workspace uses horizontal navigation on small screens. Color never conveys status alone.

Only implemented actions appear as product controls. Future product modules are labeled with their roadmap milestones. The code illustration is explicitly identified as an illustration. Dashboard statistics are deferred until backed by real submission and competition data.

Optional light mode, modal/dropdown primitives and data tables will be added with workflows that need them; they are not part of the current account-only interface.
