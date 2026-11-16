# Changelog

## 0.1.1 — 2026-11-16

- Add a true 1920×1080 16:9 camera using REA-assisted analysis, preserving vertical field of view and object proportions.
- Keep the HUD uniformly scaled and centered; retain the original movie aspect ratio.
- Scale the opening movie's separate vertex quad and correct its Direct3D stream access.
- Keep 1440×1080 and 640×480 as optional 4:3 modes.

## 0.1.0 — 2026-11-16

- Initial ROG Ally / Bazzite integration using an external open-source cabinet runtime and existing Proton.
- 1440×1080 rendering with original 4:3 proportions and corrected sprite projection.
- Direct analog controls, English pause overlay and paused-clock compensation.
- Validated native storage backups and restoration of missing files.
- Local build tool, strict supported-revision validation and bring-your-own-game documentation.
