# Valve Limit R — ROG Ally / Bazzite

Version 0.1.0. Bring your own legally obtained game files. This repository contains only original integration code and documentation, under the MIT license. It includes no game executable, assets, saves, artwork or third-party runtime binaries.

The integration provides direct ROG Ally controls, a pause screen, native cabinet storage backups and a local HD build. The game renders at **1440×1080**, preserving its original 4:3 aspect ratio on a 1920×1080 display, with black side bars. A small original Direct3D 9 bridge corrects the sprite projection so the interface scales with the 3D scene. The original textures and fonts remain low resolution; this is not a texture replacement pack. The native approximately 30 FPS timing is preserved.

The tested revision identifies itself as VL1.34JA. Its original `launcher.exe` SHA-256 must be:

```
f3cfe44a82b16d935d8e6dc46c83cb9893483c2b6018d65e4ed911063061d70e
```

## Requirements and installation

Tested on ROG Ally with Bazzite, GE-Proton11-12, Python 3, SDL2, Pillow, fontconfig, GCC (i386 code generation) and GNU binutils. The compiler produces a freestanding bridge and does not require 32-bit libc. Reuse existing dependencies when available.

1. Place the project in `~/Games/ValveLimitR` and your game files in `game/`, with `game/launcher.exe` and the original data folders.
2. Obtain `wal-loader.exe`, `wal_typex.dll` and the Valve Limit R profile `valve-limit-r.yaml` from the official [Windows Arcade Loader project](https://github.com/aderumier/windowsarcadeloader). Place these in `dependencias/`. The tested runtime release is v0.1. Keep its GPL license with your private installation; it is distributed separately from this project.
3. Build locally on Linux: `python3 source/build.py`. This validates the original file, creates `game/valve-ally.exe`, and records its hash in `docs/hd-build.json`. The original remains intact.
4. Run `chmod +x jogar.sh`, then add `jogar.sh` to Steam as a non-Steam shortcut. Do not force a Steam compatibility tool on this shell script; it invokes Proton itself. Set the shortcut display resolution to 1920×1080 and disable Steam Input for the shortcut, since this integration reads the physical controller directly.
5. Close other games before launching. Run `./jogar.sh`. Set `VALVE_PROTON` to the full Proton executable path if using another installed version.

The launcher reads the upstream standalone cabinet setting from the external profile. No online service or linked cabinet is required. First-time native calibration is required on a fresh installation; an existing calibrated cabinet save is retained.

## Controls

| Ally input | Action |
| --- | --- |
| Left stick | Steering / selection |
| RT | Accelerate / confirm selections |
| LT | Brake |
| A | Nitro / start |
| B | Handbrake |
| X | Camera |
| Y | Start / confirm service menu |
| LB / RB | Shift down / up |
| View | Coin, if free play is off |
| Menu | Pause / resume |
| A / B in pause | Resume |

The pause menu is English. Pause suspends the game and subtracts the paused interval from its imported clocks. It is a session pause, not a save state.

## First-time cabinet setup

With the game running, use `python3 source/service.py test` to open its technical menu. The green text is the selected row. Use RB to move down, LB to move up, and Y to confirm. The red I/O arrow is a calibration reminder, not the cursor.

Under I/O Check, choose Accel/Brake Calibration. Follow the full-press and release instructions for RT and LT, then choose Save & Exit. Under Coin Setting, enable Free Play and choose Save & Exit. Under Game Setting, choose Easy if desired and save. The native settings persist across launches. The private tested installation is already calibrated, set to Free Play and Easy.

## Automatic storage

The game uses `game/WindowsLoader/expdat` and `extdat` as its native cabinet storage, including settings and ranking data it commits. These files remain in place between launches. Every ten seconds and on clean exit, the integration checks all six native checksums and copies valid changed files into `saves/latest`, with up to twenty content-addressed historical versions per file. Missing native files are restored from valid backups on launch. Existing native files are never overwritten by an older backup.

This preserves the game's native saved data, not an unfinished race or a console-style career. The integration cannot persist progression that the original game never writes.

## Language and limits

The tested game is Japanese. No confirmed compatible English translation was found in the GitHub repositories and source searches checked on 2026-11-16, including [Windows Arcade Loader](https://github.com/aderumier/windowsarcadeloader) and [windowsloader](https://github.com/njz3/windowsloader). The cabinet settings do not expose a language selector. The external pause menu is English, but that does not translate the game itself.

HD was checked in attract mode, car selection and a race on the Ally. This is an initial integration, not exhaustive validation of every course or effect. No new textures, widescreen field-of-view patch, or 60 FPS simulation patch is included. To revert to native resolution for troubleshooting, set `WAL_D3D9_FULLSCREEN_SIZE` in `source/runtime-env.json` to `640x480`; the bridge then leaves the original projection alone.

Game names identify compatibility only. This project is not affiliated with the game publisher or hardware vendors.
