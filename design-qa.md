# Guardian mobile design QA — 2026-10-13

## Reference and scope
- Source: https://xd.adobe.com/view/9b919913-de49-4197-a406-0585fdb1310b-cec2/ (main_m), guardian dashboard, menu and detail screens.
- Implemented in the existing React application, not a separate static mockup. Staff layout and backend are unchanged.
- Source canvas is 430px; implementation uses max-width 430px and fits narrower phones. Desktop displays the same centered guardian canvas.

## Visual comparison
Actual source and local rendered dashboard screenshots were inspected together in one CUA response at source zoom 100%. Menu/detail screenshots were also inspected. Local widths: 1280 desktop, 430, 390 and 320. Final preview: /private/tmp/guardian-mobile-final.jpg (local evidence, not committed).

| Area | Finding and resolution |
| --- | --- |
| Frame/header | White narrow canvas, blue branding and hamburger; desktop guardian navigation moved into menu. Staff remains wide. |
| Profile | Excess inherited spacing found in initial rendering; removed, keeping portrait, relationship/name, detail action and pending counts. |
| Latest update | Pale-blue summary card retained, driven by existing published data. |
| Topics | Long rows changed to compact pills. Text labels retained alongside icons for clarity; three columns, two below 350px. |
| Menu | Full-height blue sheet, guardian identity, close/logout, detail destinations and language setting. Native dialog provides modal focus behavior. |
| Details | Single-column cards, compact resident header, touch-sized controls and wrapping date selection. |
| Login | Narrow guardian login and photo background. Fixed negative-layer background stacking with isolation. Staff login unchanged. |
| Supplied residents | Same narrow shell, menu routes select details/questions/sharing tabs. Local supplied-family question navigation verified. |

## Intentional differences
- Uses current authorized synthetic data, relationship/name and selected interface language, not copied reference values or counts.
- Counts explicitly mean records, not health scores. Existing charts, KIDE test menu, provenance and empty-state explanations remain.
- Topic labels and minimum 44px interactive controls improve mobile readability over icon-only reference pills.
- Existing detail functions and supplied-data graphs remain available; no source artwork interpreted as medical evidence.

## Verification
- CUA: legacy guardian login, menu, period detail, logout, supplied-family questions, staff review; 320/390px document width equals viewport.
- TypeScript typecheck and XD production build passed.
- Full tracked E2E: 32/33 initially passed; sole failure expected the superseded one-column grid. Updated assertion to three columns. Targeted re-run 5/5 passed, including that test, guardian responsive navigation and staff width assertion.
- XD variant E2E: 4/4 passed (design navigation/charts, independent-session English publishing loop, two role-login tests).
- No real AI, physical microphone or clinical quality validation performed for this visual change.

P0/P1/P2 unresolved: none found in reviewed scope.
final result: passed

## Welcome cards — 2026-10-13
- Source: user screenshots b01ee148 (copy), cd619332 (white card), 26f4a678 (existing portals), under supplied clipboard paths.
- Implementation: /private/tmp/welcome-desktop.jpg (1280x1100 full page), /private/tmp/welcome-mobile.jpg (390x1082 full page); logged-out English, local port8780.
- Comparison: desktop capture and reference card opened together. Reference1044x550 is a cropped approximately2x card; implementation500CSS-px card, 1x capture. Card height intentionally grows for the supplied three-line headline. Full-page and mobile viewed for spacing and wrapping.
- Typography: existing sans-serif, bold48px desktop/32px mobile, exact English line breaks; body18/16px. Colors: white translucent card, dark readable heading, blue emphasis intentionally darker than brown-background source for white-card contrast. Radius20px, soft shadow, 30px desktop padding match reference proportions. Existing hero photo retained, no substitute asset.
- Copy: user supplied marketing text, not a patient status result; synthetic PoC notice retained. ko/fi variants added; professional Finnish review pending.
- Interactions: guardian link opens two-resident selector; staff link opens nurse login. Mobile cards stack without clipping. No actionable P0/P1/P2 findings in first comparison, no QA fix iteration required.
- final result: passed

## Guardian overview — 2026-10-13
- Source: supplied mobile summary reference7dcd9a1b; previous graph-heavy first screenf0e9b488. Intent: quick dated summary and category rows; graphs in details, retain current blue design.
- Implementation: /private/tmp/provided-overview-mobile.jpg,390CSS px viewport,390px scroll width, full-page1x screenshot; real local guardian session with authorized shared fields.
- Initial P1: inherited provided-data SVG width stretched icons and clipped card text. Fixed explicit28px width/height; post-fix screenshot has readable rows, colored assessment badges and quantitative changes. Navigation to period selector/graphs/daily details verified.
- Typography16px category/14px values/13px changes, rounded white rows, green summary, blue existing icons; no new generated assets. Copy separates measurements from health assessment; no avatar invented. Long source descriptions wrap; no horizontal overflow.
- final result: passed
