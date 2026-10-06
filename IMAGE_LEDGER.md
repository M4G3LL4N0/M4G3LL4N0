# Image ledger

Every image referenced by a public owned repository. **27 images** across **100 repositories**.

Unresolved images must equal zero. A file that declares CSS `@keyframes` but no SMIL is reported `CSS_ONLY_NOT_ANIMATED`: GitHub's SVG renderer does not honour CSS animation, so it does not move in the browser.

## Summary

| state | count |
| --- | --- |
| animated | 2 |
| css_only | 1 |
| static | 15 |
| static_by_platform | 9 |

## Per-image detail

| repo | path | purpose | animation | fallback | live | note |
| --- | --- | --- | --- | --- | --- | --- |
| `agentos` | `assets/social-card.png` | social-card | STATIC_BY_PLATFORM | n/a | yes | 74697 bytes raster |
| `gh0st` | `https://github.com/M4G3LL4N0/gh0st/actions/workflows` | ci_badge | STATIC_BY_PLATFORM | n/a | yes | remote badge, static by design |
| `gh0st` | `https://github.com/M4G3LL4N0/gh0st/actions/workflows` | ci_badge | STATIC_BY_PLATFORM | n/a | yes | remote badge, static by design |
| `gh0st` | `https://img.shields.io/badge/License-MIT-yellow.svg` | shields_badge | STATIC_BY_PLATFORM | n/a | yes | remote badge, static by design |
| `gh0st` | `https://img.shields.io/github/v/release/M4G3LL4N0/gh` | release_badge | STATIC_BY_PLATFORM | n/a | yes | remote badge, static by design |
| `gh0st` | `https://img.shields.io/badge/Tauri-2.0-blue` | shields_badge | STATIC_BY_PLATFORM | n/a | yes | remote badge, static by design |
| `gh0st` | `https://img.shields.io/badge/TypeScript-5.5-blue` | shields_badge | STATIC_BY_PLATFORM | n/a | yes | remote badge, static by design |
| `gh0st` | `https://img.shields.io/badge/Platform-macOS%20%7C%20` | shields_badge | STATIC_BY_PLATFORM | n/a | yes | remote badge, static by design |
| `gh0st` | `https://img.shields.io/badge/Local--First-✓-brightgr` | shields_badge | STATIC_BY_PLATFORM | n/a | yes | remote badge, static by design |
| `gh0st` | `https://img.shields.io/badge/Telemetry-None-brightgr` | shields_badge | STATIC_BY_PLATFORM | n/a | yes | remote badge, static by design |
| `gh0st` | `assets/social-card.png` | social-card | STATIC_BY_PLATFORM | n/a | yes | 74842 bytes raster |
| `grokinstall` | `assets/social-card.png` | social-card | STATIC_BY_PLATFORM | n/a | yes | 74100 bytes raster |
| `grokmax` | `assets/social-card.png` | social-card | STATIC_BY_PLATFORM | n/a | yes | 80796 bytes raster |
| `M4G3LL4N0` | `assets/profile/hero-motion.svg` | hero-motion | ANIMATED | reduced_motion | yes | 55 SMIL, css=True, a11y=True |
| `M4G3LL4N0` | `assets/profile/nav/noaerth-dark.svg` | noaerth-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/nav/repositories-dark.svg` | repositories-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/nav/why-dark.svg` | why-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/build-signal-dark.svg` | build-signal-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/windows/agentos-dark.svg` | agentos-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/windows/grokinstall-dark.svg` | grokinstall-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/windows/grokmax-dark.svg` | grokmax-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/windows/gh0st-dark.svg` | gh0st-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/windows/opencode-watchdog-dark.svg` | opencode-watchdog-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/system-map-dark.svg` | system-map-dark | STATIC | check | yes | 0 SMIL, css=False, a11y=True |
| `M4G3LL4N0` | `assets/profile/portfolio-economics-motion.svg` | portfolio-economics-motion | CSS_ONLY_NOT_ANIMATED | reduced_motion | yes | 0 SMIL, css=True, a11y=True |
| `M4G3LL4N0` | `assets/profile/terminal-motion.svg` | terminal-motion | ANIMATED | reduced_motion | yes | 13 SMIL, css=True, a11y=True |
| `opencode-watchdog` | `assets/social-card.png` | social-card | STATIC_BY_PLATFORM | n/a | yes | 89560 bytes raster |

## Unresolved: **0**

None.
