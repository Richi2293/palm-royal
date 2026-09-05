<p align="center">
  <img src="showcase-hero.png" alt="Dusk street view of the Palm Royal hotel and Cafe Miramar, with a neon sign, palms and a parked concept car">
</p>

# Palm Royal

**A GTA-inspired tropical city, modelled entirely in Blender by AI models writing Python.**

There is no manual modelling in this project. Every building, palm tree, kerb stone, neon tube and window frame exists because a language model wrote a Blender Python script that generates it. I ran the scripts, looked at the renders, said what was wrong, and the model rewrote the script. The repository is the record of that loop.

It is a personal experiment, run for the fun of finding out how far current models can push a 3D scene when the only interface they have is code.

**[Explore the city in your browser](https://richi2293.github.io/palm-royal/)** ·
[How it was built](docs/how-it-was-built.md) ·
[Asset credits](docs/asset-credits.md)

[![Blender 5.1](https://img.shields.io/badge/Blender-5.1-orange)](https://www.blender.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational)](LICENSE)
[![Live viewer](https://img.shields.io/badge/demo-live-2fe0bd)](https://richi2293.github.io/palm-royal/)

## The five stages

Each stage opens the scene the previous one saved and changes it, so the city grows in place rather than being regenerated from scratch. Every stage is one Python script and one deterministic random seed.

### 1. A street diorama

`build_world.py` builds a single Art Deco block on a floating slab: a hotel, a diner, a social club, ten palms, three cars and street furniture. 669 objects, all procedural, no external assets.

<img src="palm-royal-preview.png" alt="Isometric view of a pastel Art Deco street block on a floating slab, with palms and parked cars" width="640">

### 2. A city around it

`build_city.py` expands the block into a 280 × 250 metre city: nine districts, six downtown towers, four boulevards and four avenues, a marina with fifteen yachts, a beach, an observation wheel. The result is 11,928 objects sharing 1,090 unique meshes, which is what later makes it small enough to stream into a browser.

<img src="coastal-city-aerial.png" alt="Aerial view of the full coastal city at dusk, with towers, a marina and a beach" width="420"> <img src="coastal-city-street.png" alt="Street-level view down a boulevard between mid-rise buildings, with a car in the foreground" width="420">

### 3. One block, at full quality

`build_showcase.py`, `refine_showcase.py` and `finalize_showcase.py` rebuild the original Palm Royal block with scanned PBR materials up to 4K, projecting cornices, shutters, balcony railings, individually modelled palm leaflets, wet asphalt, kerb stones and a drivable-looking concept car. The rest of the city stays stylized, which is the point: it is a quality study against a low-detail backdrop.

<img src="showcase-closeup.png" alt="Close-up of Cafe Miramar at dusk, with a glowing sign, stone columns and pavement tables" width="640">

### 4. Real windows and real interiors

`upgrade_windows_cafe.py` replaces glass panels painted onto solid walls with actual openings: sills, mullions, curtains, room depth, furniture. Cafe Miramar gets a full interior with a marble bar, booths, an espresso machine and a pastry vitrine, visible from the street through the open front.

<img src="miramar-windows.png" alt="Close-up of hotel windows with real openings, brass frames, balconies and curtains" width="420"> <img src="miramar-interior.png" alt="Interior of Cafe Miramar with pendant lights, timber floor, booths and a long bar" width="420">

### 5. Neon

`upgrade_sign.py` builds an original Art Deco marquee for the cafe, with emissive tubing and a glow pass in the compositor.

<img src="miramar-neon-sign.png" alt="Cafe Miramar at night with a pink and cyan neon marquee over the pavement tables" width="640">

## See it

Three ways in, from no effort to full rebuild.

**In the browser.** [richi2293.github.io/palm-royal](https://richi2293.github.io/palm-royal/) loads the stage 2 city as 3.7 MB of Draco-compressed geometry. Orbit it, or switch to walk mode and use W A S D to move down the boulevards. Nothing to install.

**In Blender.** `palm-royal.blend` and `coastal-city.blend` are small enough to be tracked in this repository, so you can clone and open them directly in Blender 5.1.2 or later. See [docs/city.md](docs/city.md) for the cameras and the walk navigation controls.

**From scratch.** The stage 3, 4 and 5 scenes are 280 to 430 MB each and are not tracked. Rebuild them with the pipeline below.

## Reproduce

Everything is deterministic. The same scripts on the same Blender version produce the same scene, down to the position of each palm, because every stage seeds its random number generator explicitly.

```sh
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender

# Stages 1 and 2: fully procedural, no downloads.
$BLENDER --background --factory-startup --python build_world.py
$BLENDER --background --factory-startup --python build_city.py

# Stage 3: fetch the CC0 source assets, then upgrade the central block.
python3 download_assets.py
$BLENDER --background --factory-startup --python build_showcase.py
$BLENDER --background --factory-startup --python refine_showcase.py
$BLENDER --background --factory-startup --python finalize_showcase.py

# Stages 4 and 5: interiors and neon.
python3 download_cafe_assets.py
$BLENDER --background --factory-startup --python upgrade_windows_cafe.py
$BLENDER --background --factory-startup --python upgrade_sign.py

# Optional: regenerate the web viewer geometry.
$BLENDER --background --factory-startup --python viewer/export_web.py
```

`download_assets.py` pulls roughly 500 MB from Poly Haven and verifies every file against the provider checksum. Only the manifests are tracked here, so the asset set stays reproducible without committing the binaries.

## What this is not

- Not a game. There is no gameplay, no physics, no collision, no AI traffic. The walk mode in the web viewer glides through walls on purpose.
- Not a full-city asset pass. Only the central block got the high-quality treatment. Zoom into anything else and it is deliberately simple geometry.
- Not built from ripped assets. Nothing here comes from any commercial video game. The architecture is original, the third-party props are CC0 from Poly Haven, and the concept car is CC BY. Full sourcing in [docs/asset-credits.md](docs/asset-credits.md).
- Not affiliated with Rockstar Games. "GTA-inspired" describes a visual mood: sun-bleached Art Deco, palms and neon.

## Documentation

- [How it was built](docs/how-it-was-built.md): the models, the workflow, and the parts that did not work.
- [The coastal city](docs/city.md): scale, districts, cameras, navigation.
- [The detailed block](docs/detailed-block.md): the quality study and its sources.
- [Interiors and windows](docs/interiors.md): real openings, glazing, the cafe interior.
- [Asset credits](docs/asset-credits.md): every third-party asset, author and licence.

## Stack

Blender 5.1.2 and its Python API, Cycles for rendering, Poly Haven for CC0 scanned materials and props, three.js for the web viewer, GitHub Pages for hosting.

## Licence

Project code and original geometry: [MIT](LICENSE). Third-party assets keep their own licences, listed in [docs/asset-credits.md](docs/asset-credits.md).
