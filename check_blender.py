"""Refuse to build with a Blender version this pipeline does not support.

The build scripts call a fair amount of the bpy API, which moves between major
releases. Without this check a mismatched Blender fails somewhere deep inside a
build script, with a traceback that says nothing about the real cause.

Run it the way the Makefile does:

    blender --background --factory-startup --python check_blender.py
"""
import bpy

# The oldest release the scripts are known to work on, and the one they are
# actually tested against.
MINIMUM = (5, 1, 0)
TESTED = (5, 1, 2)

version = bpy.app.version
readable = '.'.join(str(part) for part in version)

if version < MINIMUM:
    raise SystemExit(
        f'This is Blender {readable}, and the build needs at least '
        f'{".".join(str(part) for part in MINIMUM)}. The scripts use API that '
        'older releases do not have, so the build would fail partway through '
        'with an unrelated-looking error. Install a newer Blender, or point the '
        'build at one you already have:\n'
        '    make all BLENDER=/path/to/blender'
    )

if version[0] > TESTED[0]:
    print(
        f'Warning: this is Blender {readable}, and the pipeline is tested '
        f'against {".".join(str(part) for part in TESTED)}. The scripts still '
        'call Material.use_nodes and World.use_nodes, which Blender 6 removes, '
        'so the build may fail. Report what breaks, or build with a 5.x release.'
    )
else:
    print(f'Blender {readable}: supported.')
