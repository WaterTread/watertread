# Return Guide

## Function

The return guide is a passive guiding element that assists blades during the return phase of the motion cycle.
It helps reorient blades into a low-drag configuration and stabilizes their path as they move upstream through the protected return channel.

The return guide works in conjunction with water flow and blade inertia, without active control or actuation.

---

## Quantity

2 pcs per system (one per side)

---

## Interfaces

- **Blade**
  - Blades contact or are guided by the return guide during the return phase
  - Ensures stable orientation and prevents unintended rotation

- **Link Tread**
  - Return guide geometry aligns with the tread path to maintain smooth motion

- **Hydrodynamic Panels**
  - Operates within the hydrodynamic channel formed by the side and center panels

---

## Geometry Description

- The return guide follows the return path of the tread system
- Geometry is shaped to:
  - Encourage blade rotation into a low-drag orientation
  - Prevent blade oscillation or flutter
  - Maintain clearance between blades and structural elements

---

## Operating Role

- During the **return phase**, the return guide stabilizes blade orientation and minimizes hydrodynamic resistance
- During the **capture phase**, the return guide does not interact with the blades

---

## Design Notes

- Passive geometry minimizes mechanical complexity and failure points
- Smooth guide surfaces reduce wear and hydrodynamic losses
- Geometry may be tuned to balance guidance and friction
- Return guide design is symmetric across both sides of the system

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/return_guide/`

- Production implementation (v1.0):
  `models/1.0/parts/return_guide/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
