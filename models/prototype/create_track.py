"""
Rigid Chain Baker driven by a rotating gear (Blender)

WHAT THIS SCRIPT DOES
---------------------
Builds a CLOSED chain/track from REAL rigid link objects (no deformation),
places them along a Curve path by true pitch steps, and BAKES the motion
into per-object transform keyframes (location + rotation_quaternion).

Key features:
- Rigid links (real objects, no curve deform)
- Every Nth link can be a special connector (0,6,12,...)
- No roll flips: uses a stable transported "up" frame
- Uses two joint markers (J0/J1 empties) inside each master link so that
  hinge pins/holes stay perfectly aligned (mechanically correct)
- Reads gear rotation and converts it to chain travel distance: traveled = theta * r
- Output is glTF/GLB-friendly (BabylonJS): baked object transforms

REQUIREMENTS / SETUP
--------------------
Scene objects:
1) A Curve object that represents the track path:
   - Default name: "TrackPath" (CURVE_NAME)
   - Must be cyclic (closed loop) for a closed chain

2) Two master link objects (Mesh):
   - Default names: "Link_A" and "Link_B"
   - Link_B is used as a connector every PERIOD_N links (default every 6th)

3) Each master link MUST contain two child Empty objects that mark hinge centers:
   - J0 = hinge center for the "start" of the link (connects to previous link)
   - J1 = hinge center for the "end" of the link (connects to next link)
   Notes:
   - They can be named J0/J1 or have Blender suffixes (J0.001, J1.002, etc.)
   - Parent them to the link (select empty, shift-select link, Ctrl+P → Object (Keep Transform))
   - If your link local forward is -Y and you placed J1 at (0,-pitch,0), that's fine:
     AUTO_SWAP_JOINTS + EXPECTED_LOCAL_FORWARD controls orientation.

4) A Gear object (drives chain travel):
   - Default name: "Gear"
   - The chain travel per frame = gear_angle * gear_radius
   - IMPORTANT: This script reads gear.rotation_euler.
     If your gear is rotated via parent/constraint/driver (visual rotation),
     you may need to BAKE the gear's action first (Object → Animation → Bake Action, Visual Keying).

TRANSFORMS (IMPORTANT FOR STL IMPORTS)
-------------------------------------
If your links/gears were imported from STL, make sure their SCALE is applied:
- Select Link_A, Link_B, Gear → Ctrl+A → Scale
(Empties J0/J1 should NOT need Apply.)

HOW TO USE
----------
1) Ensure you have:
   - TrackPath curve
   - Link_A and Link_B masters
   - J0/J1 empties parented under each master link
   - Gear animated (keyframes or baked)

2) Adjust SETTINGS below:
   - CURVE_NAME, LINK_A_NAME, LINK_B_NAME, GEAR_NAME
   - PERIOD_N / SPECIAL_AT (connector pattern)
   - GEAR_ROT_AXIS (X/Y/Z) and DIR_SIGN
   - FRAME_START / FRAME_END

3) Run the script.

OUTPUT
------
Creates/overwrites a Collection named COLLECTION_NAME (default "BakedChain")
containing objects:
  ChainLink_0000, ChainLink_0001, ...
Each object has baked keyframes for:
  - location
  - rotation_quaternion

Export to BabylonJS:
- File → Export → glTF 2.0
- Enable: Export Animations, Always Sample Animations
- Export as .glb

TROUBLESHOOTING
---------------
- Chain doesn't move even though gear "spins":
  Your gear's rotation is probably coming from a parent/constraint/driver.
  Bake the gear first (Visual Keying) so rotation_euler changes per frame.

- Chain moves opposite direction:
  Set DIR_SIGN = -1.0

- Links appear reversed:
  Adjust EXPECTED_LOCAL_FORWARD, or disable AUTO_SWAP_JOINTS.

- Link_B was not found correctly when empties are named J0.001/J1.001:
  This script supports suffixes by design (base name before ".").

"""

import bpy
import math
from mathutils import Vector, Matrix

# =========================
# SETTINGS
# =========================
CURVE_NAME  = "TrackPath"
LINK_A_NAME = "Link_A"
LINK_B_NAME = "Link_B"
GEAR_NAME   = "Gear"
COLLECTION_NAME = "BakedChain"

PERIOD_N   = 6
SPECIAL_AT = 0          # 0,6,12,... => Link_B

GEAR_ROT_AXIS = 'X'     # gearin LOCAL rotaatioakseli: 'X'/'Y'/'Z'
DIR_SIGN = 1.0          # -1 jos liikesuunta väärä

FRAME_START = 1
FRAME_END   = 250       # testaa ensin vaikka 1..3 jos haluat

JOINT0_NAME = "J0"
JOINT1_NAME = "J1"

WORLD_UP = Vector((0, 0, 1))

# jos empties puuttuu
LINK_PITCH_FALLBACK = 6.4

# jos J1 on siirretty "-6.4" tms ja haluat automaattisen suunnan valinnan
AUTO_SWAP_JOINTS = True
EXPECTED_LOCAL_FORWARD = Vector((0, 1, 0))  # oletus: local +Y on ketjun suunta
# =========================


def get_obj(name, type_=None):
    o = bpy.data.objects.get(name)
    if not o:
        raise RuntimeError(f"Missing object: {name}")
    if type_ and o.type != type_:
        raise RuntimeError(f"Object {name} is {o.type}, expected {type_}")
    return o


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def clear_collection(col):
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def duplicate_link(src_obj, name, collection):
    obj = src_obj.copy()
    obj.data = src_obj.data  # linked mesh
    obj.name = name
    collection.objects.link(obj)
    return obj


def eval_curve_polyline(curve_obj):
    deps = bpy.context.evaluated_depsgraph_get()
    eval_obj = curve_obj.evaluated_get(deps)
    cu = eval_obj.data
    if not cu.splines:
        raise RuntimeError("Curve has no splines")
    spl = cu.splines[0]

    pts = []
    if spl.type == 'BEZIER':
        for p in spl.evaluated_points:
            pts.append(p.co.to_3d())
    else:
        if hasattr(spl, "evaluated_points") and len(spl.evaluated_points) >= 2:
            for p in spl.evaluated_points:
                pts.append(p.co.to_3d())
        else:
            for p in spl.points:
                pts.append(p.co.to_3d())

    if len(pts) < 2:
        raise RuntimeError("Not enough evaluated points on curve")

    pts2 = pts + [pts[0]]

    total = 0.0
    seglen = []
    cum = [0.0]
    for i in range(len(pts2) - 1):
        l = (pts2[i+1] - pts2[i]).length
        seglen.append(l)
        total += l
        cum.append(total)

    return eval_obj, pts2, seglen, cum, total


def eval_curve_at_distance(eval_obj, pts2, seglen, cum, total, dist):
    """Evaluate world position at arc-length distance (wraps)."""
    mw = eval_obj.matrix_world
    target = dist % total

    j = 0
    while j < len(seglen) and cum[j+1] < target:
        j += 1
    if j >= len(seglen):
        j = len(seglen) - 1

    lseg = seglen[j]
    seg_t = 0.0 if lseg < 1e-9 else (target - cum[j]) / lseg

    p_local = pts2[j].lerp(pts2[j+1], seg_t)
    return mw @ p_local


def estimate_gear_radius(gear_obj, rot_axis='X'):
    d = gear_obj.dimensions
    ax = rot_axis.upper()
    if ax == 'X':
        r = 0.5 * max(d.y, d.z)
    elif ax == 'Y':
        r = 0.5 * max(d.x, d.z)
    else:
        r = 0.5 * max(d.x, d.y)
    return float(r)


def get_axis_angle(gear_obj, rot_axis='X'):
    ax = rot_axis.upper()
    gear_obj.rotation_mode = 'XYZ'
    e = gear_obj.rotation_euler
    return float(getattr(e, ax.lower()))


def get_joint_local_positions(master_obj):
    """
    Finds child empties named J0/J1, accepting Blender suffixes:
    J0, J0.001, J0.123 ... (same for J1)
    Returns: (j0_local, j1_local) or (None, None)
    """
    j0 = None
    j1 = None
    for ch in master_obj.children:
        base = ch.name.split(".", 1)[0]  # "J0.001" -> "J0"
        if base == JOINT0_NAME:
            j0 = ch
        elif base == JOINT1_NAME:
            j1 = ch

    if not j0 or not j1:
        return None, None

    return j0.matrix_local.translation.copy(), j1.matrix_local.translation.copy()


def stable_basis_from_forward(forward, prev_up=None):
    """Parallel-transport-ish up to avoid flips."""
    y = forward.normalized()

    if prev_up is None:
        z = WORLD_UP - y * WORLD_UP.dot(y)
        if z.length < 1e-6:
            z = Vector((0, 1, 0)) - y * Vector((0, 1, 0)).dot(y)
        z.normalize()
    else:
        z = prev_up - y * prev_up.dot(y)
        if z.length < 1e-6:
            z = WORLD_UP - y * WORLD_UP.dot(y)
        z.normalize()

    x = y.cross(z)
    if x.length < 1e-9:
        x = Vector((1, 0, 0))
    x.normalize()

    z = x.cross(y).normalized()
    return x, y, z, z  # new up = z


def link_matrix_world_for_two_joints(p0_w, p1_w, j0_l, j1_l, prev_up=None):
    """
    Compute rigid transform so that:
    - local j0_l maps to p0_w
    - local j1_l maps to p1_w
    Also keeps roll stable using transported up.
    """
    fwd_w = (p1_w - p0_w)
    if fwd_w.length < 1e-9:
        fwd_w = Vector((0, 1, 0))
    fwd_w.normalize()

    fwd_l = (j1_l - j0_l)
    if fwd_l.length < 1e-9:
        raise RuntimeError("J0 and J1 are at same position in link local space.")
    fwd_l.normalize()

    wx, wy, wz, new_up = stable_basis_from_forward(fwd_w, prev_up)
    W = Matrix((wx, wy, wz)).transposed()

    local_up_hint = Vector((0, 0, 1))
    lx, ly, lz, _ = stable_basis_from_forward(fwd_l, local_up_hint)
    L = Matrix((lx, ly, lz)).transposed()

    R = W @ L.inverted()
    T = Matrix.Translation(p0_w - (R @ j0_l))
    return (T @ R.to_4x4()), new_up


def main():
    curve = get_obj(CURVE_NAME, "CURVE")
    link_a = get_obj(LINK_A_NAME, "MESH")
    link_b = get_obj(LINK_B_NAME, "MESH")
    gear = get_obj(GEAR_NAME)

    col = ensure_collection(COLLECTION_NAME)
    clear_collection(col)

    eval_obj, pts2, seglen, cum, total_len = eval_curve_polyline(curve)
    gear_r = estimate_gear_radius(gear, GEAR_ROT_AXIS)

    a_j0, a_j1 = get_joint_local_positions(link_a)
    b_j0, b_j1 = get_joint_local_positions(link_b)

    if a_j0 is None or a_j1 is None:
        print("⚠️ Link_A: J0/J1 not found. Using fallback.")
        a_j0 = Vector((0, 0, 0))
        a_j1 = Vector((0, LINK_PITCH_FALLBACK, 0))
    if b_j0 is None or b_j1 is None:
        print("⚠️ Link_B: J0/J1 not found. Using fallback.")
        b_j0 = Vector((0, 0, 0))
        b_j1 = Vector((0, LINK_PITCH_FALLBACK, 0))

    def maybe_swap(j0, j1):
        if not AUTO_SWAP_JOINTS:
            return j0, j1
        f = (j1 - j0)
        if f.length < 1e-9:
            return j0, j1
        f.normalize()
        if f.dot(EXPECTED_LOCAL_FORWARD.normalized()) < 0.0:
            return j1, j0
        return j0, j1

    a_j0, a_j1 = maybe_swap(a_j0, a_j1)
    b_j0, b_j1 = maybe_swap(b_j0, b_j1)

    pitch_a = (a_j1 - a_j0).length
    pitch_b = (b_j1 - b_j0).length

    if abs(pitch_a - pitch_b) > 1e-4:
        print(f"⚠️ Warning: Link_A pitch {pitch_a:.4f} != Link_B pitch {pitch_b:.4f}. Using Link_A pitch.")

    pitch = pitch_a if pitch_a > 1e-6 else LINK_PITCH_FALLBACK

    count = max(2, int(round(total_len / pitch)))
    print(f"Track length={total_len:.3f}, pitch≈{pitch:.4f}, count={count}")
    print(f"Gear radius approx={gear_r:.3f} (axis {GEAR_ROT_AXIS})")

    links = []
    link_joint_data = []
    is_special_flags = []
    for i in range(count):
        is_special = ((i % PERIOD_N) == SPECIAL_AT)
        src = link_b if is_special else link_a
        obj = duplicate_link(src, f"ChainLink_{i:04d}", col)
        obj.rotation_mode = 'QUATERNION'
        links.append(obj)
        link_joint_data.append((b_j0, b_j1) if is_special else (a_j0, a_j1))
        is_special_flags.append(is_special)

    scene = bpy.context.scene

    for f in range(FRAME_START, FRAME_END + 1):
        scene.frame_set(f)

        theta = get_axis_angle(gear, GEAR_ROT_AXIS) * DIR_SIGN
        traveled = theta * gear_r

        ps = [None] * count
        for i in range(count):
            dist = (i * pitch) + traveled
            ps[i] = eval_curve_at_distance(eval_obj, pts2, seglen, cum, total_len, dist)

        prev_up = None
        for i, obj in enumerate(links):
            p0 = ps[i]
            p1 = ps[(i + 1) % count]

            j0_l, j1_l = link_joint_data[i]
            Mw, prev_up = link_matrix_world_for_two_joints(p0, p1, j0_l, j1_l, prev_up)

            obj.matrix_world = Mw
            obj.keyframe_insert(data_path="location", frame=f)
            obj.keyframe_insert(data_path="rotation_quaternion", frame=f)

    print("✅ Done. Pitch-stepped + two-joint placement baked (suffix-safe joints).")

main()
