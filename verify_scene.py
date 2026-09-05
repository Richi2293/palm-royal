"""Check that a rebuilt scene matches the expected contents.

The build scripts pin their random seeds, so rebuilding from a clean checkout
must produce the same geometry rather than something merely similar. This
script turns that promise into a check anyone can run.

Usage, from the Makefile or by hand:

    blender --background --factory-startup --python verify_scene.py -- <scene.blend>
    blender --background --factory-startup --python verify_scene.py -- <scene.blend> --dump

Without --dump the counts are compared against scene-expectations.json and the
process exits non-zero on any mismatch. With --dump the measured counts are
written back into that file, which is how the reference values are recorded
after an intentional change to the scene.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
EXPECTATIONS = ROOT / 'scene-expectations.json'


def measure():
    """Summarise the loaded scene as a dictionary of stable counts."""
    types = Counter(obj.type for obj in bpy.data.objects)
    return {
        'objects': len(bpy.data.objects),
        'meshes': types['MESH'],
        'lights': types['LIGHT'],
        'cameras': types['CAMERA'],
        'materials': len(bpy.data.materials),
        'collections': len(bpy.data.collections),
        'vertices': sum(len(mesh.vertices) for mesh in bpy.data.meshes),
    }


def report(scene, measured, expected):
    """Print a per-field comparison and return True when everything matches."""
    ok = True
    for key in sorted(measured):
        got = measured[key]
        want = expected.get(key)
        if want is None:
            print(f'  {key:12} {got:>9}  (no reference value recorded)')
        elif got == want:
            print(f'  {key:12} {got:>9}  ok')
        else:
            print(f'  {key:12} {got:>9}  MISMATCH, expected {want}')
            ok = False
    return ok


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not args:
        raise SystemExit('verify_scene.py needs a .blend path after "--".')

    target = Path(args[0])
    if not target.is_absolute():
        target = ROOT / target
    if not target.exists():
        raise SystemExit(
            f'{target.name} does not exist yet. Build it first, for example with "make all".'
        )

    dump = '--dump' in args
    bpy.ops.wm.open_mainfile(filepath=str(target))
    measured = measure()

    stored = json.loads(EXPECTATIONS.read_text(encoding='utf-8')) if EXPECTATIONS.exists() else {}

    if dump:
        stored[target.name] = measured
        EXPECTATIONS.write_text(json.dumps(stored, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(f'Recorded reference values for {target.name}:')
        for key in sorted(measured):
            print(f'  {key:12} {measured[key]:>9}')
        return

    expected = stored.get(target.name)
    if expected is None:
        raise SystemExit(
            f'No reference values recorded for {target.name}. '
            'Run the same command with --dump to record them.'
        )

    print(f'Verifying {target.name}:')
    if not report(target.name, measured, expected):
        raise SystemExit(
            f'{target.name} does not match its reference values. Either the build is '
            'not reproducible, or the scene changed on purpose and the reference '
            'values need updating with --dump.'
        )
    print(f'{target.name} matches its reference values.')


main()
