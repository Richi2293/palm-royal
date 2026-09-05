# How it was built

The rule for this project was that I never touch the geometry by hand. I do not open Blender's modelling tools, I do not move a vertex, I do not place a building. The models write Python, Blender runs it in background mode, a PNG comes out, and I say what is wrong with it. That is the whole loop.

What follows is what the repository actually shows about that loop, including the parts that are more accident than design.

## The models

Three models worked on this city: Claude (through Claude Code), GPT 5.6 and GPT 6.

> To complete before merging: which model handled which stage, whether the same
> task was ever given to more than one model, and the concrete failures worth
> naming. This section is the reason anyone reads this file, so it should not be
> vague.

## The pipeline is incremental, not regenerative

The obvious way to build a city in scripts is one big generator that produces the final scene. That is not what happened. Each stage opens the `.blend` the previous stage saved, changes part of it, and saves under a new name:

```
build_world.py       ->  scenes/palm-royal.blend
build_city.py        ->  scenes/coastal-city.blend
build_showcase.py    ->  scenes/coastal-city-detailed.blend   (opens scenes/coastal-city.blend)
refine_showcase.py   ->  scenes/coastal-city-detailed.blend   (in place)
finalize_showcase.py ->  scenes/coastal-city-detailed.blend   (in place)
upgrade_windows_cafe.py -> scenes/coastal-city-interiors.blend
upgrade_sign.py      ->  scenes/coastal-city-neon.blend
```

This falls out of how the work was requested. Each session asked for a change to what already existed, so each script was written to mutate a saved scene rather than to rebuild the world. It has a real cost: to reproduce stage 5 you must run all seven scripts in order, and a change to stage 2 invalidates everything downstream.

## The scripts reuse each other by parsing their own source

The later stages need the helpers from the earlier ones: `material()`, `box()`, `rod()`, `collection()`, `camera()`. A normal Python program would import them. Importing `build_world.py` is not an option, because its module level is the scene generation itself: importing it would wipe the current scene and rebuild the diorama.

The solution in the repository is to parse the earlier script and execute only its function definitions:

```python
for filename in ['build_world.py', 'build_city.py']:
    for node in ast.parse((ROOT / filename).read_text()).body:
        if isinstance(node, ast.FunctionDef) and node.name in ['material', 'text', 'collection', 'place', 'box', 'rod']:
            exec(compile(ast.Module(body=[node], type_ignores=[]), filename, 'exec'))
```

`build_city.py` goes further and slices the source by a comment marker, running everything above `# Fine procedural` to recover the shared colour palette.

This is a workaround for a structural problem that a human would have solved by extracting a module. It works, it is deterministic, and it is completely load-bearing: renaming a helper or moving that comment breaks four scripts at once. I am leaving it in because it is an honest artefact of how the project grew, and it is exactly the kind of thing a model reaches for when told to add a feature without refactoring.

## Everything is seeded

Each generating stage sets an explicit seed before it places anything:

| Stage | Seed |
| --- | --- |
| `build_world.py` | 18 |
| `build_city.py` | 41 |
| `build_showcase.py` | 73 |
| `upgrade_windows_cafe.py` | 106 |

Same scripts, same Blender version, same city. This matters more than it sounds: without it, "the palm on the corner is clipping the awning" is not a reproducible bug report, and the whole feedback loop stops working.

## Linked duplicates, on purpose

The stage 2 city is 11,928 objects sharing 1,090 unique meshes. Repeated props are instances of shared mesh data rather than independent copies. This was a deliberate choice while building, and it is the only reason the web viewer exists: the glTF export carries 1,571 unique meshes referenced by 11,948 nodes, which compresses to 3.7 MB, and the viewer collapses those nodes back into instanced draw calls in the browser.

## Snapshots before every risky change

`prepare_navigation.py`, `open_cafe_interior.py` and `open_neon_sign.py` do almost nothing except save a copy of the current scene under a `*-before-*.blend` name before the next destructive script runs. Undo does not exist in background mode, and a bad script that saves over a 400 MB scene costs an hour of re-rendering. The defensive snapshot habit appeared early and stayed.

## The code style changes visibly between stages

`build_world.py` is written in spaced, documented, PEP 8 style, with docstrings on every helper. From `build_showcase.py` onwards the code is dense: `ROOT=Path(__file__).resolve().parent`, no spaces around assignment, no docstrings on locals. Counting assignments written as `name = value` at the start of a line: 20 in `build_world.py`, 4 in `build_city.py`, 0 in every script after that.

Nothing in the project asked for that change. It is a fingerprint of different authorship across the stages, and it is visible without reading a single line of logic.

## Limits worth stating

- The detailed pass covers one block. The other eight districts are still the stage 2 geometry, and they look it up close.
- There is no collision, no navigation mesh, no gameplay. Walk navigation in Blender and in the web viewer both pass straight through walls.
- Interiors exist for the cafe and for the hotel front rooms only. Everything else with a lit window is a lit window.
- The stage 3 to 5 scenes are 280 to 430 MB because the textures are packed into the `.blend`. They cannot be tracked in git, which is why the pipeline has to be reproducible instead.
