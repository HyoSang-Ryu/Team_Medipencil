# Guardian mobile app shell — 2026-10-14

final result: passed

## Evidence and scope
- Source visual truth: user-provided phone reference `/var/folders/4_/phnbk0312kz78clxwhsnnj4h0000gn/T/codex-clipboard-7dcd9a1b-07a6-49e0-a2c2-eef4171327dd.png` (400×786 pixels; photographed angled phone, not a CSS viewport).
- Implementation: local browser `http://127.0.0.1:8780/family/provided`, Finnish guardian overview; screenshot `/private/tmp/guardian-app-final-390.png` (390×844 pixels, viewport390×844 CSS px, density1).
- Full-view comparison: `/private/tmp/guardian-app-final-comparison.png` (810×844); source shown at native resolution beside implementation. No false pixel-perfect alignment: source has a physical phone frame, different data and text. Target is its app navigation/card hierarchy using current product styling, not literal illustration replication.
- Focused inspection: navigation icon sizing and bottom boundary inspected in browser screenshot plus DOM bounds; final bar77px tall,24px icons. Expanded bottom record-information section ends703px, above navigation top767px at390×844.

## Comparison history
1. Initial render: P2 global SVG sizing enlarged bottom icons and bar136.5px; explicit24px SVG dimensions fixed this. Initial comparison also showed excessive doubled card gaps. Removed duplicate bottom margins and reduced card padding/min-height.
2. Post-fix capture and combined comparison above: no remaining actionable P0/P1/P2 findings in tested states.

## Fidelity surfaces
- Typography: existing Arial/system Korean fallback retained. Resident22px, summary17px, body14px, navigation12px; hierarchy/wrapping readable. Not attempting to reproduce perspective-distorted mockup lettering.
- Layout: centered430px app canvas on desktop, full available mobile width; fixed four-item navigation, rounded resident/summary/status cards. Reference's compact illustrations and three-day dot graph remain intentionally outside this change; existing exact numeric comparisons require more space and period graphs live under Records.
- Color: existing product blue navigation, pale blue resident card and green summary retained; up/down/missing semantic colors unchanged. No new clinical color inference.
- Assets: existing demonstration mother portrait reused, standard Phosphor vectors used for app navigation. No drawn replacement for reference artwork; decorative phone frame/sun and inactive guardian portrait intentionally omitted from functional product UI.
- Copy/content: Finnish/Korean/English labels and existing role/consent-filtered data retained. Today's section explicitly states latest record/comparison dates. Record information stays last. Staff styles unchanged through guardian-only selectors.

## Interaction verification
- Real local server/DB read path: overview, period records/graphs, family question form and sharing scope reachable from bottom navigation.
- Browser back restores previous active tab; selected state synchronized through URL. Existing memory-only login still requires reselecting a role after reload; persistence not added.
-320×740: no horizontal overflow, all four destinations visible.390×844: bottom disclosure clickable and not covered.1280×900: app/nav both430px and centered atx425. Keyboard-focus outlines provided; screen-reader names retained.
- Browser collected console errors: none during tested local session. No external AI calls or family-message writes performed.
- Typecheck,45 unit tests and XD production build passed. CI/public deployment tracked in progress log.

## Residual gaps
- Physical iOS/Android software keyboard and safe-area behavior not device-tested; CSS bottom safe-area padding provided.
- Existing external STT/LLM service failures are not addressed by this UI work. No claim of end-to-end AI validation.
