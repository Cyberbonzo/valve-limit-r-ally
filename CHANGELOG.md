# Changelog

## 0.1.3 — 2026-11-16

- Render active races at approximately 60 FPS by interpolating scene poses between original 30 Hz updates; keep the native logic gate unchanged.
- Interpolate camera, supported scene meshes and cars, restoring endpoint values before the normal render pass.
- Prevent the extra render pass from advancing movie/overlay updates and crash-animation physics a second time.
- Retain original cadence in menus, videos and results; document interpolation limits and visual delay.
- Validate 1080p/16:9, approximately 60 rendered FPS / 30 native updates per second, pause freeze, boost ON/OFF and race transitions on the Ally.

## 0.1.2 — 2026-11-16

- Add an English Infinite Boost ON/OFF option to the pause menu, with controller navigation and a persistent private preference.
- Refill local-player nitro charges during active races; retain native boost activation and duration.
- Verify pause freeze, normal depletion with the cheat OFF, and repeated boosts with it ON.
- Document the 60 FPS frame-gate experiment and restore native timing because fixed-step logic also speeds up.

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
