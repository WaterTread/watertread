# Blade

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

- **59443** Technic Axle Joiner (2 pcs)
- **3704** Technic Axle 2 (2 pcs)

---

## Modifications

- Increase the height of the Technic Axle Joiner from **2L to 4L**
- Extend the inner wedge profile of each axle joiner so that opposing joiners meet, forming a **continuous and uniform blade surface**
- Shape the blade surface to fully cover the **1L-height gap between the cam followers**, preventing flow leakage during the capture phase
- Cap the outer end of each axle joiner while leaving the internal cavity hollow to reduce mass; the trapped air also contributes to buoyancy when submerged, effectively reducing the blade’s apparent weight in water
- Use Technic Axle 2 elements to connect both ends of the blade assembly to the cam followers, allowing controlled rotational motion

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
