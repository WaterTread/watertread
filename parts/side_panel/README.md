# Hydrodynamic Side Panel

[See 3D-model](./side_panel.stl)

## Function

The hydrodynamic side panel forms the lateral boundaries of the water flow channel around the blades.
It prevents lateral water escape, concentrates flow through the blade capture region, and improves overall hydrodynamic efficiency.

The side panels also serve as structural mounting surfaces for the cam elements.

---

## Quantity

2 pcs per system (left and right)

---

## Interfaces

- **Frame**

  - Side panels are rigidly mounted to the frame
  - Define the lateral geometry of the flow channel

- **Blades**

  - Blades operate within the channel formed between the side panels
  - Panels do not move with the blades, minimizing moving mass

- **Cam**

  - Cam elements are mounted to the inner surface of the side panels
  - Provides precise alignment for cam–follower interaction

- **Hydrodynamic Center Panel**
  - Side panels interface with the center panel to form a closed flow channel

---

## Geometry Description

- Panels follow the overall elliptical path of the tread system
- Geometry is shaped to:
  - Guide incoming flow toward the blade capture region
  - Minimize turbulence and leakage
  - Maintain consistent clearance to moving components

---

## Operating Role

- During the **capture phase**, side panels confine flow to maximize blade loading
- During the **return phase**, panels isolate the return path from incoming flow

---

## Design Notes

- Panels are fixed to reduce moving mass and inertial losses
- Structural stiffness is required to maintain cam alignment
- Panel geometry may evolve to optimize hydrodynamic performance
- Surface finish may influence flow behavior and efficiency

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/side_panel/`

- Production implementation (v1.0):
  `models/1.0/parts/side_panel/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
