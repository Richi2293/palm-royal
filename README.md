# Palm Royal — Tropical Street Diorama

An original, stylized tropical neighborhood in the spirit of a 1980s Art Deco coastal resort. All geometry is created procedurally; no external assets or add-ons are required.

## Files
- `palm-royal.blend`: editable Blender 5.1.2 scene, with 669 objects organized into collections.
- `palm-royal-preview.png`: verified 1500 × 1100 Cycles render.
- `build_world.py`: reproducible scene builder. Running it replaces the generated project and preview in this directory.
- `previous-session.blend`: backup of the Blender session before loading this project.
- `build.log`: generation log.

## Explore
Use the middle mouse button to orbit and the wheel to zoom. Numpad 0 toggles the active camera. Two cameras are provided: a neighborhood overview and a street-level view. To switch cameras, select the desired camera in the Cameras collection and use Ctrl+Numpad 0. F12 renders the active camera.

The scene includes an Art Deco hotel, diner, social club, ten palms, three stylized cars, street furniture, a beach edge, and a simple skyline. It is a static exterior diorama, without gameplay, building interiors, character animation, or vehicle simulation.

## Rebuild
```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python build_world.py
```
