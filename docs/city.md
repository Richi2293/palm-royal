# Coastal City

> This guide covers one stage of the pipeline. The scene it names is a build intermediate: run the pipeline from the [README](../README.md#reproduce) to produce it. The finished city is `scenes/palm-royal-city.blend`.


## Scale and contents
The expanded city contains 280 × 250 meters of terrain (70,000 square meters), approximately 30.4 times the original 59 × 39 meter diorama footprint. A marina and surrounding ocean extend beyond the land footprint. The expansion adds distinct connected streets and districts; the original geometry has not simply been enlarged.

- Nine city blocks with 36 detailed low- and mid-rise buildings.
- Six downtown towers, up to 75 meters before rooftop structures.
- Four connected east-west boulevards and four north-south avenues.
- Oceanfront parks, beach umbrellas, loungers and a landmark observation wheel.
- Marina with five piers and fifteen stylized yachts.
- Rooftop pools, balconies, shop signs, traffic signals, vehicles and pedestrian scale figures.

## Open and explore
Open `scenes/coastal-city.blend` in Blender 5.1.2 or later. The default view is the aerial camera.

The Exploration cameras collection contains:
1. Entire coastal city.
2. Walk Ocean Boulevard.
3. Marina and skyline.
4. Beach promenade.
5. Downtown roof terraces.

Select a camera in the Outliner and press Ctrl+Numpad 0 to make it active. Numpad 0 enters or leaves camera view. For keyboard layouts without a numpad, use View > Cameras > Set Active Object as Camera.

For first-person exploration, use View > Navigation > Walk Navigation from the 3D viewport. Move with W/A/S/D, look with the mouse, and use the wheel to adjust movement speed. Use the on-screen navigation help for vertical movement and confirmation controls. This is Blender viewport navigation, not a gameplay controller or a collision-tested game level.

Material Preview provides a convenient editing view. Rendered shading and F12 show the actual lighting; performance depends on the machine. The saved project uses Cycles and denoising. Bright-sign glow is applied in final renders.

## Files
- `scenes/coastal-city.blend`: expanded editable project.
- `renders/coastal-city-aerial.png`: overview render.
- `renders/coastal-city-street.png`: pedestrian-level render.
- `build_city.py`: reproducible scene-generation script.
- `city-build.log`: execution log.

The original Palm Royal project remains available separately. All assets are original procedural geometry. Architecture and props are stylized; buildings have exterior detail rather than furnished interiors.
