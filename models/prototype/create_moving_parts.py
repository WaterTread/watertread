import bpy
import math
from bisect import bisect_right
from mathutils import Vector, Matrix

CURVE_L_NAME = "TrackPath_L"
CURVE_R_NAME = "TrackPath_R"

LINK_A_NAME = "Link_A"
LINK_B_NAME = "Link_B"

GEAR_NAME   = "Gear"
GEAR_ROT_AXIS = 'X'

GEAR_TEETH = 40

COL_CHAIN_L = "BakedChain_L"
COL_CHAIN_R = "BakedChain_R"
COL_RIGS    = "BakedCamAndWings"

PERIOD_N   = 6
SPECIAL_AT = 0

FRAME_START = 0
FRAME_END   = 57

JOINT0_NAME = "J0"
JOINT1_NAME = "J1"
CAM0_NAME   = "C0"

LINK_PITCH_FALLBACK = 6.4

AUTO_SWAP_JOINTS = True
EXPECTED_LOCAL_FORWARD = Vector((0, -1, 0))

WORLD_UP = Vector((0, 0, 1))

AUTO_MATCH_CURVE_DIRECTION = True
CURVE_DIR_L = +1.0
CURVE_DIR_R = +1.0

PIN_MASTER_NAME      = "CamPin"
FOLLOWER_MASTER_NAME = "CamFollower"
WING_MASTER_NAME     = "Wing"

USE_EMPTY_FOR_PIN = False
USE_EMPTY_FOR_FOLLOWER = False
USE_EMPTY_FOR_WING = False

HINGE_MARKER_NAME = "H0"

FORCE_WING_WORLD_X_ZERO = True

PIN_OUTER_HALF_DIST = 72.0
FOLLOWER_OUTER_HALF_DIST = 76.0

USE_MASTER_THETA = True

# master angle (radians) = frame * speed + phase
MASTER_SPEED_RAD_PER_FRAME = 0.05
MASTER_PHASE_RAD = 0.0

# Chain travel direction ONLY (do not touch gear visual direction)
CHAIN_SIGN = +1.0  # flip if chain moves wrong way: +1 / -1

# Gear visual direction
GEAR_VIS_SIGN = -1.0  # flip if Gear visual spin should invert: +1 / -1

# Pinion visual direction
PINION_VIS_SIGN = +1.0  # flip if Pinion visual spin should invert: +1 / -1
BAKE_MECHANICS = True
CLEAR_EXISTING_MECH_ANIM = True

MECH_ROT = [
    ("Gear", 1.0, GEAR_VIS_SIGN, GEAR_ROT_AXIS),
    ("Gear.001", 1.0, GEAR_VIS_SIGN, GEAR_ROT_AXIS),
    ("Gear.002", 1.0, GEAR_VIS_SIGN, GEAR_ROT_AXIS),
    ("Gear.003", 1.0, GEAR_VIS_SIGN, GEAR_ROT_AXIS),
    ("Axle", 1.0, GEAR_VIS_SIGN, GEAR_ROT_AXIS),
    ("Axle.001", 1.0, GEAR_VIS_SIGN, GEAR_ROT_AXIS),
    ("Pinion", 5.0, PINION_VIS_SIGN, GEAR_ROT_AXIS),
    ("PinionAxle", 5.0, PINION_VIS_SIGN, GEAR_ROT_AXIS),
    ("Pinion.001", 5.0, PINION_VIS_SIGN, GEAR_ROT_AXIS),
    ("PinionAxle.001", 5.0, PINION_VIS_SIGN, GEAR_ROT_AXIS),
]

WING_CAM_ENABLE = True
WING_MAP_SMOOTHSTEP = True
WING_FLIP_AROUND_HINGE_X = True
WING_MAP_AUTO_FIX_LOOP = True

# If cam feels reversed, flip:
CAM_ANGLE_SIGN = -1.0

WING_MAP = [
    (0.00, 10.0),
    (0.04, 0.0),
    (0.06, 320.0),
    (0.07, 300.0),
    (0.08, 270.0),
    (0.15, 270.0),
    (0.23, 270.0),
    (0.31, 270.0),
    (0.38, 270.0),
    (0.44, 270.0),
    (0.46, 305.0),
    (0.48, 0.0),
    (0.54, 0.0),
    (0.62, 0.0),
    (0.69, 0.0),
    (0.77, 0.0),
    (0.85, 0.0),
    (0.92, 0.0),
    (0.96, 0.0),
    (1.00, 10.0),
]
# =========================


# ---------- helpers ----------
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

def strip_animation(obj):
    if obj.animation_data:
        obj.animation_data_clear()

def duplicate_object(src_obj, name, collection):
    obj = src_obj.copy()
    if src_obj.data:
        obj.data = src_obj.data
    obj.name = name
    obj.rotation_mode = 'QUATERNION'
    obj.scale = (1, 1, 1)
    collection.objects.link(obj)
    strip_animation(obj)
    return obj

def new_empty(name, collection, empty_type='PLAIN_AXES'):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = empty_type
    obj.rotation_mode = 'QUATERNION'
    obj.scale = (1, 1, 1)
    collection.objects.link(obj)
    strip_animation(obj)
    return obj

def base_name(n: str) -> str:
    return n.split(".", 1)[0]

def get_child_local(parent_obj, marker_name: str):
    for ch in parent_obj.children:
        if base_name(ch.name) == marker_name:
            return ch.matrix_local.translation.copy()
    return None

def get_joint_locals(master_obj):
    return get_child_local(master_obj, JOINT0_NAME), get_child_local(master_obj, JOINT1_NAME)

def maybe_swap_joints(j0, j1):
    if (not AUTO_SWAP_JOINTS) or j0 is None or j1 is None:
        return j0, j1
    f = (j1 - j0)
    if f.length < 1e-9:
        return j0, j1
    f.normalize()
    if f.dot(EXPECTED_LOCAL_FORWARD.normalized()) < 0.0:
        return j1, j0
    return j0, j1

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

def eval_curve_at_distance_fast(eval_obj, pts2, seglen, cum, total, dist):
    mw = eval_obj.matrix_world
    target = dist % total

    j = bisect_right(cum, target) - 1
    if j < 0:
        j = 0
    if j >= len(seglen):
        j = len(seglen) - 1

    lseg = seglen[j]
    seg_t = 0.0 if lseg < 1e-9 else (target - cum[j]) / lseg
    p_local = pts2[j].lerp(pts2[j+1], seg_t)
    return mw @ p_local

def master_theta(frame: int) -> float:
    return (float(frame) * float(MASTER_SPEED_RAD_PER_FRAME)) + float(MASTER_PHASE_RAD)

def axis_vec_from_letter(letter: str) -> Vector:
    l = letter.upper()
    if l == 'X': return Vector((1,0,0))
    if l == 'Y': return Vector((0,1,0))
    return Vector((0,0,1))

def quat_from_axis_angle(axis_vec: Vector, angle_rad: float):
    axis = axis_vec.normalized() if axis_vec.length > 1e-9 else Vector((1,0,0))
    return Matrix.Rotation(angle_rad, 4, axis).to_quaternion()

def set_obj_quat(obj, q, frame):
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = q
    obj.keyframe_insert("rotation_quaternion", frame=frame)

def clear_anim_on(obj):
    if obj and obj.animation_data:
        obj.animation_data_clear()

def bake_mechanics(scene):
    if not BAKE_MECHANICS:
        return

    if CLEAR_EXISTING_MECH_ANIM:
        for (name, _, _, _) in MECH_ROT:
            o = bpy.data.objects.get(name)
            if o:
                clear_anim_on(o)

    axis_cache = {}

    for f in range(FRAME_START, FRAME_END + 1):
        scene.frame_set(f)
        bpy.context.view_layer.update()

        th = master_theta(f)

        for (name, ratio, sign, ax_letter) in MECH_ROT:
            obj = bpy.data.objects.get(name)
            if not obj:
                continue

            if ax_letter not in axis_cache:
                axis_cache[ax_letter] = axis_vec_from_letter(ax_letter)

            axis = axis_cache[ax_letter]
            q = quat_from_axis_angle(axis, th * float(ratio) * float(sign))
            set_obj_quat(obj, q, f)

def stable_basis_from_forward(forward, prev_up=None):
    y = forward.normalized()

    if prev_up is None:
        z = WORLD_UP - y * WORLD_UP.dot(y)
        if z.length < 1e-6:
            alt = Vector((0, 1, 0))
            z = alt - y * alt.dot(y)
        z.normalize()
    else:
        z = prev_up - y * prev_up.dot(y)
        if z.length < 1e-6:
            z = WORLD_UP - y * WORLD_UP.dot(y)
        if z.length < 1e-6:
            alt = Vector((0, 1, 0))
            z = alt - y * alt.dot(y)
        z.normalize()

    x = y.cross(z)
    if x.length < 1e-9:
        x = Vector((1, 0, 0))
    x.normalize()

    z = x.cross(y).normalized()
    return x, y, z, z

def link_matrix_world_for_two_joints(p0_w, p1_w, j0_l, j1_l, prev_up=None):
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

def detect_curve_direction_match(evalL0, evalR0, pitch):
    (evalL, pts2L, segL, cumL, totalL) = evalL0
    (evalR, pts2R, segR, cumR, totalR) = evalR0

    pL0 = eval_curve_at_distance_fast(evalL, pts2L, segL, cumL, totalL, 0.0)
    pL1 = eval_curve_at_distance_fast(evalL, pts2L, segL, cumL, totalL, pitch)
    tL = (pL1 - pL0)
    if tL.length < 1e-9:
        return +1.0
    tL.normalize()

    pR0 = eval_curve_at_distance_fast(evalR, pts2R, segR, cumR, totalR, 0.0)
    pR1 = eval_curve_at_distance_fast(evalR, pts2R, segR, cumR, totalR, pitch)
    tR = (pR1 - pR0)
    if tR.length < 1e-9:
        return +1.0
    tR.normalize()

    return -1.0 if (tL.dot(tR) < 0.0) else +1.0

def clamp01(x: float) -> float:
    if x < 0.0: return 0.0
    if x > 1.0: return 1.0
    return x

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def ease_cos(u: float) -> float:
    u = clamp01(u)
    return 0.5 - 0.5 * math.cos(math.pi * u)

def unwrap_angle_sequence(points):
    pts = [(float(t), float(a)) for (t, a) in points]
    out = [list(pts[0])]
    for i in range(1, len(pts)):
        prev = out[-1][1]
        a = pts[i][1]
        while a - prev > 180.0:
            a -= 360.0
        while a - prev < -180.0:
            a += 360.0
        out.append([pts[i][0], a])
    return [(t, a) for t, a in out]

def fix_loop_end(points_unwrapped):
    if len(points_unwrapped) < 2:
        return points_unwrapped

    t0, a0 = points_unwrapped[0]
    t1, a1 = points_unwrapped[-1]

    k = int(round((a1 - a0) / 360.0))
    cand = [a0 + 360.0 * (k - 1), a0 + 360.0 * k, a0 + 360.0 * (k + 1)]
    target = min(cand, key=lambda x: abs(x - a1))

    fixed = list(points_unwrapped)
    fixed[-1] = (t1, target)
    return fixed

def prepare_wing_map(points):
    pts = sorted(points, key=lambda x: x[0])

    if abs(pts[0][0] - 0.0) > 1e-6:
        raise RuntimeError("WING_MAP must start at t=0.0")
    if abs(pts[-1][0] - 1.0) > 1e-6:
        raise RuntimeError("WING_MAP must end at t=1.0")

    pts = unwrap_angle_sequence(pts)
    if WING_MAP_AUTO_FIX_LOOP:
        pts = fix_loop_end(pts)
    return pts

def map_angle_from_points(t: float, points_prepared, use_smooth=True) -> float:
    t = t % 1.0

    for i in range(len(points_prepared) - 1):
        t0, a0 = points_prepared[i]
        t1, a1 = points_prepared[i + 1]
        if t0 <= t <= t1:
            u = 0.0 if (t1 - t0) < 1e-12 else (t - t0) / (t1 - t0)
            if use_smooth:
                u = ease_cos(u)
            return lerp(a0, a1, u)

    return points_prepared[-1][1]


# -------------------------
# CAM BASIS RELATIVE TO CHAIN TANGENT
# -------------------------
def basis_from_cam_angle(x_axis_world: Vector, angle_deg: float, base_y_world: Vector) -> Matrix:
    x = x_axis_world.copy()
    if x.length < 1e-9:
        x = Vector((1, 0, 0))
    x.normalize()

    y0 = base_y_world - x * base_y_world.dot(x)
    if y0.length < 1e-9:
        y0 = Vector((0, 1, 0)) - x * Vector((0, 1, 0)).dot(x)
        if y0.length < 1e-9:
            y0 = Vector((0, 0, 1)) - x * Vector((0, 0, 1)).dot(x)
    y0.normalize()

    a = math.radians(angle_deg)
    Rax = Matrix.Rotation(a, 3, x)
    y = (Rax @ y0).normalized()

    z = x.cross(y)
    if z.length < 1e-9:
        z = WORLD_UP.copy()
    z.normalize()

    y = z.cross(x)
    if y.length < 1e-9:
        y = Vector((0, 1, 0))
    y.normalize()

    R = Matrix((x, y, z)).transposed()

    if WING_FLIP_AROUND_HINGE_X:
        R = R @ Matrix.Rotation(math.pi, 3, 'X')

    return R


def main():
    wing_map_prepared = prepare_wing_map(WING_MAP)

    scene = bpy.context.scene
    scene.frame_set(FRAME_START)
    bpy.context.view_layer.update()

    curveL = get_obj(CURVE_L_NAME, "CURVE")
    curveR = get_obj(CURVE_R_NAME, "CURVE")
    linkA  = get_obj(LINK_A_NAME, "MESH")
    linkB  = get_obj(LINK_B_NAME, "MESH")

    gear = get_obj(GEAR_NAME)

    if USE_MASTER_THETA and BAKE_MECHANICS:
        bake_mechanics(scene)
        scene.frame_set(FRAME_START)
        bpy.context.view_layer.update()

    c0_local = get_child_local(linkB, CAM0_NAME)
    if c0_local is None:
        raise RuntimeError("Link_B missing C0 marker (child empty named C0).")

    a_j0, a_j1 = get_joint_locals(linkA)
    b_j0, b_j1 = get_joint_locals(linkB)
    if a_j0 is None or a_j1 is None:
        a_j0 = Vector((0,0,0)); a_j1 = Vector((0, LINK_PITCH_FALLBACK, 0))
    if b_j0 is None or b_j1 is None:
        b_j0 = Vector((0,0,0)); b_j1 = Vector((0, LINK_PITCH_FALLBACK, 0))
    a_j0, a_j1 = maybe_swap_joints(a_j0, a_j1)
    b_j0, b_j1 = maybe_swap_joints(b_j0, b_j1)

    pitch = (a_j1 - a_j0).length
    if pitch <= 1e-6:
        pitch = LINK_PITCH_FALLBACK

    gear_r = pitch / (2.0 * math.sin(math.pi / float(GEAR_TEETH)))

    evalL0 = eval_curve_polyline(curveL)
    totalLenL = evalL0[4]
    count = max(2, int(round(totalLenL / pitch)))

    evalR0 = eval_curve_polyline(curveR)

    dirL = CURVE_DIR_L
    dirR = CURVE_DIR_R
    if AUTO_MATCH_CURVE_DIRECTION:
        dirR = detect_curve_direction_match(
            (evalL0[0], evalL0[1], evalL0[2], evalL0[3], evalL0[4]),
            (evalR0[0], evalR0[1], evalR0[2], evalR0[3], evalR0[4]),
            pitch
        )

    colL = ensure_collection(COL_CHAIN_L)
    colR = ensure_collection(COL_CHAIN_R)
    colRig = ensure_collection(COL_RIGS)
    clear_collection(colL); clear_collection(colR); clear_collection(colRig)
    bpy.ops.outliner.orphans_purge(do_recursive=True)

    pin_master = get_obj(PIN_MASTER_NAME) if not USE_EMPTY_FOR_PIN else None
    fol_master = get_obj(FOLLOWER_MASTER_NAME) if not USE_EMPTY_FOR_FOLLOWER else None
    wing_master = get_obj(WING_MASTER_NAME) if not USE_EMPTY_FOR_WING else None

    pin_h0_local = Vector((0,0,0))
    fol_h0_local = Vector((0,0,0))

    if not USE_EMPTY_FOR_PIN:
        tmp = get_child_local(pin_master, HINGE_MARKER_NAME)
        if tmp is None:
            raise RuntimeError("CamPin master missing child empty H0.")
        pin_h0_local = tmp

    if not USE_EMPTY_FOR_FOLLOWER:
        tmp = get_child_local(fol_master, HINGE_MARKER_NAME)
        if tmp is None:
            raise RuntimeError("CamFollower master missing child empty H0.")
        fol_h0_local = tmp

    pin_h0_off_M = Matrix.Translation(-pin_h0_local) if not USE_EMPTY_FOR_PIN else None
    fol_h0_off_M = Matrix.Translation(-fol_h0_local) if not USE_EMPTY_FOR_FOLLOWER else None

    linksL = [
        duplicate_object(linkB if ((i % PERIOD_N) == SPECIAL_AT) else linkA,
                         f"L_ChainLink_{i:04d}", colL)
        for i in range(count)
    ]
    linksR = [
        duplicate_object(linkB if ((i % PERIOD_N) == SPECIAL_AT) else linkA,
                         f"R_ChainLink_{i:04d}", colR)
        for i in range(count)
    ]

    def bake_chain_from_eval(eval_data, links, curve_dir_sign):
        eval_obj, pts2, seglen, cum, total_len = eval_data

        n_links = len(links)
        prev_up_per_link = [None] * n_links

        frame_set = scene.frame_set
        view_update = bpy.context.view_layer.update

        t0 = master_theta(FRAME_START) if USE_MASTER_THETA else 0.0

        for f in range(FRAME_START, FRAME_END + 1):
            frame_set(f)
            view_update()

            if USE_MASTER_THETA:
                theta = (master_theta(f) - t0) * CHAIN_SIGN
            else:
                theta = 0.0

            traveled = theta * gear_r

            ps = [None] * n_links
            for i in range(n_links):
                dist = curve_dir_sign * (i * pitch) + traveled
                ps[i] = eval_curve_at_distance_fast(eval_obj, pts2, seglen, cum, total_len, dist)

            chain_prev_up = None
            for i, obj in enumerate(links):
                p0 = ps[i]
                p1 = ps[(i + 1) % n_links]
                is_special = ((i % PERIOD_N) == SPECIAL_AT)
                j0_l, j1_l = (b_j0, b_j1) if is_special else (a_j0, a_j1)

                up_hint = prev_up_per_link[i] if prev_up_per_link[i] is not None else chain_prev_up
                Mw, new_up = link_matrix_world_for_two_joints(p0, p1, j0_l, j1_l, up_hint)

                prev_up_per_link[i] = new_up
                chain_prev_up = new_up

                obj.matrix_world = Mw
                obj.scale = (1,1,1)
                obj.keyframe_insert("location", frame=f)
                obj.keyframe_insert("rotation_quaternion", frame=f)

    bake_chain_from_eval(evalL0, linksL, dirL)
    bake_chain_from_eval(evalR0, linksR, dirR)

    rigs = []
    for i in range(count):
        if (i % PERIOD_N) != SPECIAL_AT:
            continue

        pinL = new_empty(f"Pin_L_{i:04d}", colRig) if USE_EMPTY_FOR_PIN else duplicate_object(pin_master, f"Pin_L_{i:04d}", colRig)
        pinR = new_empty(f"Pin_R_{i:04d}", colRig) if USE_EMPTY_FOR_PIN else duplicate_object(pin_master, f"Pin_R_{i:04d}", colRig)

        folL = new_empty(f"Follower_L_{i:04d}", colRig) if USE_EMPTY_FOR_FOLLOWER else duplicate_object(fol_master, f"Follower_L_{i:04d}", colRig)
        folR = new_empty(f"Follower_R_{i:04d}", colRig) if USE_EMPTY_FOR_FOLLOWER else duplicate_object(fol_master, f"Follower_R_{i:04d}", colRig)

        wingPivot = new_empty(f"WingPivot_{i:04d}", colRig)
        wing = new_empty(f"Wing_{i:04d}", colRig) if USE_EMPTY_FOR_WING else duplicate_object(wing_master, f"Wing_{i:04d}", colRig)

        rigs.append((i, pinL, folL, pinR, folR, wingPivot, wing))

    frame_set = scene.frame_set
    view_update = bpy.context.view_layer.update

    t0 = master_theta(FRAME_START) if USE_MASTER_THETA else 0.0

    for f in range(FRAME_START, FRAME_END + 1):
        frame_set(f)
        view_update()

        theta = (master_theta(f) - t0) * CHAIN_SIGN if USE_MASTER_THETA else 0.0
        traveled = theta * gear_r

        for (i, pinL, folL, pinR, folR, wingPivot, wing) in rigs:
            linkL = linksL[i]
            linkR = linksR[i]

            C0L_w = (linkL.matrix_world @ c0_local)
            C0R_w = (linkR.matrix_world @ c0_local)

            x_vec = (C0R_w - C0L_w)
            if x_vec.length < 1e-9:
                x_dir = Vector((1, 0, 0))
                half_sep = 0.0
            else:
                x_dir = x_vec.normalized()
                half_sep = 0.5 * x_vec.length

            pin_extra = (PIN_OUTER_HALF_DIST - half_sep)
            fol_extra = (FOLLOWER_OUTER_HALF_DIST - half_sep)

            PIN_L_w = C0L_w - x_dir * pin_extra
            PIN_R_w = C0R_w + x_dir * pin_extra

            FOL_L_w = C0L_w - x_dir * fol_extra
            FOL_R_w = C0R_w + x_dir * fol_extra

            qL = linkL.matrix_world.to_quaternion()
            qR = linkR.matrix_world.to_quaternion()
            qL_M = qL.to_matrix().to_4x4()
            qR_M = qR.to_matrix().to_4x4()

            if USE_EMPTY_FOR_PIN:
                pinL.matrix_world = Matrix.Translation(PIN_L_w) @ qL_M
                pinR.matrix_world = Matrix.Translation(PIN_R_w) @ qR_M
            else:
                pinL.matrix_world = Matrix.Translation(PIN_L_w) @ qL_M @ pin_h0_off_M
                pinR.matrix_world = Matrix.Translation(PIN_R_w) @ qR_M @ pin_h0_off_M

            pinL.scale = (1,1,1); pinR.scale = (1,1,1)
            pinL.keyframe_insert("location", frame=f); pinL.keyframe_insert("rotation_quaternion", frame=f)
            pinR.keyframe_insert("location", frame=f); pinR.keyframe_insert("rotation_quaternion", frame=f)

            mid = (C0L_w + C0R_w) * 0.5
            if FORCE_WING_WORLD_X_ZERO:
                mid.x = 0.0

            if WING_CAM_ENABLE:
                distL = dirL * (i * pitch) + traveled
                t = (distL % totalLenL) / totalLenL

                ang = map_angle_from_points(t, wing_map_prepared, use_smooth=WING_MAP_SMOOTHSTEP)
                ang *= CAM_ANGLE_SIGN

                base_y = (linkL.matrix_world.to_3x3() @ Vector((0, 1, 0)))
                R = basis_from_cam_angle(x_vec, ang, base_y)
            else:
                x = x_vec
                if x.length < 1e-9:
                    x = Vector((1, 0, 0))
                x.normalize()

                y = (linkL.matrix_world.to_3x3() @ Vector((0, 1, 0)))
                if y.length < 1e-9:
                    y = Vector((0, 1, 0))
                y.normalize()

                z = x.cross(y)
                if z.length < 1e-8:
                    z = WORLD_UP.copy()
                z.normalize()

                y = z.cross(x)
                if y.length < 1e-8:
                    y = Vector((0, 1, 0))
                y.normalize()

                R = Matrix((x, y, z)).transposed()

            R4 = R.to_4x4()

            def bake_one_follower_worldbasis(fol_obj, hinge_world):
                if USE_EMPTY_FOR_FOLLOWER:
                    fol_obj.matrix_world = Matrix.Translation(hinge_world) @ R4
                else:
                    fol_obj.matrix_world = Matrix.Translation(hinge_world) @ R4 @ fol_h0_off_M

                fol_obj.scale = (1,1,1)
                fol_obj.keyframe_insert("location", frame=f)
                fol_obj.keyframe_insert("rotation_quaternion", frame=f)

            bake_one_follower_worldbasis(folL, FOL_L_w)
            bake_one_follower_worldbasis(folR, FOL_R_w)

            wingPivot.matrix_world = Matrix.Translation(mid) @ R4
            wingPivot.scale = (1,1,1)
            wingPivot.keyframe_insert("location", frame=f)
            wingPivot.keyframe_insert("rotation_quaternion", frame=f)

            wing.matrix_world = wingPivot.matrix_world.copy()
            wing.scale = (1,1,1)
            wing.keyframe_insert("location", frame=f)
            wing.keyframe_insert("rotation_quaternion", frame=f)

main()
