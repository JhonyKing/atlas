# Frontend UX/UI QA Contract v1

Each vertical slice must provide:

1. A route smoke check for its locale-aware path.
2. A 1440×900 screenshot and a 390×844 screenshot.
3. A responsive check at 375, 768, 1024, 1280, and 1920px.
4. Keyboard/focus and semantic-label checks for interactive controls.
5. Contrast/state checks proving evidence status is not color-only.
6. A horizontal-overflow check.
7. An SVG asset rendering check where branding is present.
8. A record of any intentional deviation and its follow-up task.

The QA artifact must identify route, viewport, source revision, browser, timestamp, screenshot path,
and pass/fail findings. Functional tests remain required; a screenshot cannot replace them.
