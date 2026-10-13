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
