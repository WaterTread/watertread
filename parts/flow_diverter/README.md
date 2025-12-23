# Flow Diverter

## Function

The flow diverter is a fixed upstream structure that redirects incoming water toward the upper capture region of the tread system.
Its primary purpose is to prevent flow from entering the lower return path, where it would otherwise cause unnecessary hydrodynamic drag and energy loss.

By guiding water over the active blade region, the flow diverter improves overall system efficiency.

---

## Quantity

1 pc per system

---

## Interfaces

- **Frame**
  - Flow diverter is rigidly mounted to or integrated with the frame
  - Defines the upstream boundary of the hydrodynamic channel

- **Hydrodynamic Panels**
  - Works in conjunction with the side and center panels
  - Completes the upstream flow guidance geometry

- **Incoming Water Flow**
  - Positioned upstream of the tread system
  - Redirects flow vertically and laterally toward the blade capture zone

---

## Geometry Description

- Geometry is shaped to smoothly redirect incoming flow upward
- Leading surfaces are contoured to minimize turbulence and separation
- The diverter may take the form of:
  - A curved plate
  - A wedge-shaped guide
  - A cast or molded mass integrated into the structure

Exact geometry is implementation-specific and may vary with deployment conditions.

---

## Operating Role

- During operation, the flow diverter ensures that the majority of incoming water interacts with blades in the capture phase
- Prevents flow from impinging on blades in the return phase
- Reduces parasitic drag and improves net power output

---

## Design Notes

- Flow diverter is a static, non-moving component
- Structural robustness is prioritized over minimal mass
- Surface finish and curvature may be optimized to reduce losses
- In some deployments, the diverter may also serve a protective role against debris

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/flow_diverter/`

- Production implementation (v1.0):
  `models/1.0/parts/flow_diverter/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
