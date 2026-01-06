# Blade

[See 3D-model](./blade.stl)

## Function

The blade captures kinetic energy from flowing water and converts it into mechanical motion, which is transferred to the tread system via the cam follower and link tread.

Blade orientation is actively controlled, allowing it to alternate between a high-drag capture state and a low-drag return state.

---

## Quantity

14 pcs per system

---

## Dimensions (Reference)

- Height: **5L** (including one stud provided by the cam follower interface)
- Width: **20L**

Dimensions are expressed in LEGO units (L) for prototype reference.
Production dimensions are defined in the corresponding system version under `models/`.

---

## LEGO Reference Parts

- [**3705** Technic Axle 4](https://library.ldraw.org/parts/6762) (2 pcs)

---

## Modifications

- Create a cube mesh with size of 159x2x40 (slightly narrower than the cavity)
- Cut bottom corners to make room for **Link Tread with Connector** and **Cam Follower**
- Import two Technic Axles 4 to position 76/0/4 and -76/0/4

---

## Interfaces

- **Cam Follower**
  Blade is connected at both ends to cam followers, enabling controlled rotation between capture and return phases.

- **Link Tread with Connector**
  Blade mounting points align with perpendicular pin-hole connectors on the tread system.

---

## Operating States

- **Capture Phase**
  Blade is oriented vertically to maximize hydrodynamic drag and force transfer.

- **Return Phase**
  Blade is reoriented into a low-drag configuration to minimize resistance while moving upstream.

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/blade/`

- Production implementation (v1.0):
  `models/1.0/parts/blade/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
