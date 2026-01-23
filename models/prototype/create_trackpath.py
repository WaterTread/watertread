"""
TrackPath generator for two equal-sized gears (Blender)

WHAT THIS SCRIPT DOES
---------------------
Creates a closed Curve object ("TrackPath") representing a mechanically correct
chain / belt / track path around TWO EQUAL-SIZED GEARS:

- 2 straight tangent segments
- 2 exact 180° arcs around the gears
- No BezierCircle is used (avoids Curve modifier deformation issues)
- Intended for use with Array (Fit Curve) + Curve modifier

The resulting curve is suitable for:
- chains
- timing belts
- tank tracks
- LEGO Technic-style mechanisms


HOW TO USE
----------
1. In the 3D Viewport, select EXACTLY TWO objects:
   - These represent the two gears (their origins are treated as gear centers)
   - Gears must be the SAME SIZE

2. Open the Scripting workspace.
3. Paste this script into the Text Editor.
4. Adjust parameters near the bottom of the file if needed:
     - CLEARANCE
     - ARC_SAMPLES
     - LINE_SAMPLES
     - SIDE
5. Run the script (Alt + P or "Run Script").

A new Curve object named "TrackPath" will be created.


PARAMETERS
----------
CLEARANCE
  Radial offset applied to the estimated gear radius.
  Use this to move the chain to the pitch circle.

  For LEGO Technic gears (approximate):
    - 40-tooth gear: CLEARANCE ≈ -3.5 … -4.0 (mm, if 1 Blender unit = 1 mm)
    - Negative values move the path inward
    - Positive values move it outward

ARC_SAMPLES
  Number of points used for each half-circle.
  Higher = smoother arcs (recommended: 64–128).

LINE_SAMPLES
  Number of points used for each straight segment.
  Higher = smoother deformation along straights.

SIDE
  +1 or -1
  Chooses which side of the gears the "upper" straight runs on.
  Flip this if the track is mirrored to the wrong side.


USAGE WITH A CHAIN / LINK OBJECT
-------------------------------
1. Select your link object.
2. Add an Array modifier:
     - Fit Type: Fit Curve
     - Curve Object: TrackPath
     - Relative Offset: along the link's length axis (usually Y)

3. Add a Curve modifier:
     - Curve Object: TrackPath
     - Deform Axis: same axis as Array offset (usually Y)

4. Modifier order MUST be:
     Array
     Curve

To animate the chain:
- Animate or drive the Array -> Relative Offset value.


LIMITATIONS
-----------
- Works ONLY for two gears of equal radius.
- Assumes the mechanism lies in a single plane.
- Not intended for crossed belts or unequal pulley sizes.


AUTHOR / NOTES
--------------
Created as a robust alternative to BezierCircle-based setups,
which tend to deform meshes unpredictably when used with Curve modifiers.

"""

import bpy
import math
from mathutils import Vector

def _pick_up_ref(u: Vector) -> Vector:
    """Valitse up_ref joka ei ole lähes samansuuntainen u:n kanssa."""
    up = Vector((0, 0, 1))
    if abs(u.dot(up)) > 0.99:
        up = Vector((0, 1, 0))
    return up

def _estimate_radius(obj, u: Vector, v: Vector) -> float:
    """
    Arvioi rattaan säde objektille, projektoiden obj.dimensions u/v-tasoon.
    Toimii vaikka ratas olisi hieman kääntynyt.
    """
    mw = obj.matrix_world.to_3x3()
    axes = [mw @ Vector((1,0,0)), mw @ Vector((0,1,0)), mw @ Vector((0,0,1))]
    dims = [obj.dimensions.x, obj.dimensions.y, obj.dimensions.z]

    # Kuinka paljon kukin local-akseli “osuu” u/v tasoon
    scored = []
    for ax, d in zip(axes, dims):
        axn = ax.normalized()
        score = abs(axn.dot(u)) + abs(axn.dot(v))
        scored.append((score, d))

    scored.sort(reverse=True, key=lambda t: t[0])
    # ota parhaiden akselien dimensioista suurin ja puolita => säde
    return 0.5 * max(scored[0][1], scored[1][1])

def make_track_equal_gears(obj_a, obj_b, clearance=0.0, arc_samples=64, line_samples=20,
                           side=+1, name="TrackPath"):
    """
    Luo suljetun track-polun kahden saman-säteisen rattaan ympärille:
      - 2 puolikaarta (180°)
      - 2 suoraa tangenttia
    side = +1 tai -1: kummalle puolelle “ylä” menee (vaihtaa koko loopin peiliksi).
    """

    c1 = obj_a.matrix_world.translation.copy()
    c2 = obj_b.matrix_world.translation.copy()

    d = c2 - c1
    dist = d.length
    if dist < 1e-6:
        raise RuntimeError("Rattaiden keskipisteet ovat liian lähellä toisiaan (dist ~ 0).")

    # u = rattaiden välinen suunta
    u = d.normalized()

    # Määritä taso automaattisesti: valitaan up_ref ja siitä taso
    up_ref = _pick_up_ref(u)
    n = u.cross(up_ref).normalized()    # tasosta ulos
    v = n.cross(u).normalized()         # tasossa, kohtisuoraan u:lle

    if side < 0:
        v = -v

    # Säde (saman kokoiset -> käytä keskiarvoa)
    r1 = _estimate_radius(obj_a, u, v)
    r2 = _estimate_radius(obj_b, u, v)
    r = 0.5 * (r1 + r2) + clearance

    # Tangenttipisteet (equal radii => suorat ovat u-suuntaiset)
    p1_top = c1 + v * r
    p2_top = c2 + v * r
    p1_bot = c1 - v * r
    p2_bot = c2 - v * r

    # kulma u/v -koordinaateissa
    def ang_uv(vec: Vector) -> float:
        x = vec.dot(u)
        y = vec.dot(v)
        return math.atan2(y, x)

    def sample_arc(center: Vector, start_pt: Vector, end_pt: Vector, samples: int, clockwise: bool):
        vs = start_pt - center
        ve = end_pt - center
        a0 = ang_uv(vs)
        a1 = ang_uv(ve)

        # pakota suunta
        if clockwise:
            while a1 >= a0:
                a1 -= math.tau
        else:
            while a1 <= a0:
                a1 += math.tau

        pts = []
        for i in range(samples + 1):
            t = i / samples
            a = a0 + (a1 - a0) * t
            pts.append(center + (math.cos(a) * u + math.sin(a) * v) * r)
        return pts

    def sample_line(a: Vector, b: Vector, samples: int):
        # Sisäpisteet (ei päätä), jotta ei tule tuplapisteitä
        pts = []
        for i in range(1, samples):
            t = i / samples
            pts.append(a.lerp(b, t))
        return pts

    # Tässä on se “mekaanisesti oikea” järjestys:
    # Puolikaari 1: top -> bottom (180°)
    # Suora: bottom1 -> bottom2
    # Puolikaari 2: bottom -> top (180°)
    # Suora: top2 -> top1
    #
    # Kumman puolen loopin haluat riippuu clockwise-valinnasta + side-parametrista.
    arc1 = sample_arc(c1, p1_top, p1_bot, arc_samples, clockwise=False)
    arc2 = sample_arc(c2, p2_bot, p2_top, arc_samples, clockwise=False)

    pts = []
    pts.extend(arc1)  # sisältää p1_top..p1_bot
    pts.extend(sample_line(p1_bot, p2_bot, line_samples))
    pts.append(p2_bot)

    # lisää arc2 ilman ensimmäistä pistettä (p2_bot), ettei tule tuplaa
    pts.extend(arc2[1:])

    pts.extend(sample_line(p2_top, p1_top, line_samples))
    pts.append(p1_top)

    # poista viimeinen jos sama kuin ensimmäinen
    if (pts[0] - pts[-1]).length < 1e-9:
        pts.pop()

    # Jos sama niminen curve on jo olemassa, siivotaan vanha pois (valinnainen)
    if name in bpy.data.objects:
        old = bpy.data.objects[name]
        bpy.data.objects.remove(old, do_unlink=True)

    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12
    curve_data.twist_mode = 'MINIMUM'  # auttaa ettei “twistaa”

    spline = curve_data.splines.new(type='POLY')
    spline.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        spline.points[i].co = (p.x, p.y, p.z, 1.0)
    spline.use_cyclic_u = True

    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)

    bpy.ops.object.select_all(action='DESELECT')
    curve_obj.select_set(True)
    bpy.context.view_layer.objects.active = curve_obj

    return curve_obj


# ---------- AJO ----------
sel = [o for o in bpy.context.selected_objects if o is not None]
if len(sel) != 2:
    raise RuntimeError("Valitse tasan KAKSI ratasta/objektia ja aja skripti uudelleen.")

obj_a, obj_b = sel[0], sel[1]

# Säädä näitä:
CLEARANCE = -1.6     # esim 0.02 jos haluat ketjun keskilinjan ulommas
ARC_SAMPLES = 96    # sileys kaarissa
LINE_SAMPLES = 30   # sileys suorissa
SIDE = +1           # vaihda -1 jos haluat loopin “toiselle puolelle”

make_track_equal_gears(obj_a, obj_b,
                       clearance=CLEARANCE,
                       arc_samples=ARC_SAMPLES,
                       line_samples=LINE_SAMPLES,
                       side=SIDE,
                       name="TrackPath")

print("Valmis: TrackPath luotu.")
