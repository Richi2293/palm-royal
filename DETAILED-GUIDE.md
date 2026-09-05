# Coastal City: Detailed Central Block

Open `coastal-city-detailed.blend`. The large coastal city is preserved, with a higher-detail showcase around Palm Royal and Café Miramar near world coordinates (30, -14).

## What was upgraded

- Two custom buildings with weathered plaster, textured masonry, projecting cornices, framed windows, balcony railings, shutters, awnings, and open ground-floor interiors.
- Scanned PBR materials up to 4K, including surface color, roughness, and height-derived bump. Imported assets retain their authored UVs and normal maps.
- Textured asphalt with variable wetness, individual curb stones, storm drains, and a modeled manhole cover.
- A detailed imported concept car with an interior and authored PBR materials.
- Eight imported Poly Haven model types, including cafe furniture, a hydrant, lamps, plants, trees, benches, and air-conditioning units.
- Four custom palms with individually modeled leaflets and textured curved trunks.
- HDR environment lighting, warm interior lighting, neon signage, and restrained glow in rendered images.

The rest of the city remains the earlier stylized context. This is a focused quality study, not a full-city asset replacement or a finished game level.

## Views

- Camera 06: Detailed Palm Royal block, default view.
- Camera 07: Cafe materials and street props, close-up for surface inspection.
- Cameras 01-05: the earlier city exploration viewpoints.

Use the scene camera selector to switch views. View > Navigation > Walk Navigation provides first-person viewport navigation. W/A/S/D moves and the mouse looks around.

Material Preview is useful for editing. F12 renders the actual scene lighting and compositor effects. The source textures are packed into the Blender file. Models remain editable, with repeated assets represented by collection instances.

## Outputs and sources

- `showcase-hero.png`: 1800 × 1250 overview of the detailed block.
- `showcase-closeup.png`: 1600 × 1100 cafe close-up.
- `ASSET-CREDITS.md`: source links, authors, licenses, and modifications.
- `assets/`: original downloaded resources and manifests.
- `coastal-city-before-detail.blend`: preserved session before loading the new project.

## Reproduce

After `download_assets.py` completes, run these scripts in order with Blender in background mode:
1. `build_showcase.py`
2. `refine_showcase.py`
3. `finalize_showcase.py`

They use `coastal-city.blend` as the starting scene and overwrite only the detailed project and its renders.
