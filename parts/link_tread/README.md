# Link Tread

[See 3D-model](./link_tread.stl)

## Function

The link tread forms the primary linear power transmission path of the WaterTread system.
It carries the blades around the closed-loop tread path and transfers the hydrodynamically generated forces to the drive gears.

The tread enables multiple blades to engage the water flow simultaneously, converting distributed hydrodynamic forces into continuous mechanical motion.

---

## Quantity

140 pcs per system

---

## Interfaces

- **Blade**
  - Blades are mounted to selected tread elements via Link Tread with Connector components
  - Provides a rigid mounting base while allowing controlled blade rotation

- **Drive Gears (40-Tooth)**
  - The tread engages with paired 40-tooth gears at the front and rear axles
  - Transfers linear tread motion into rotational motion

- **Frame and Guides**
  - The tread is guided along a defined path by the frame, side panels, and center panel
  - Maintains alignment and prevents lateral displacement under load

---

## LEGO Reference Part

- **3873** Technic Chain Tread 2.5 Wide

---

## Modifications

- Reduced tread width to **1L** to allow compact side-by-side spacing
- Added a continuous top-plate surface to form a smooth, closed tread surface when links are joined and aligned in the horizontal (capture) position
- The modified top plate reduces water leakage between adjacent blades during the capture phase
- Modified geometry improves hydrodynamic efficiency while maintaining mechanical engagement

---

## Operating Role

- During the **capture phase**, the tread transmits blade-generated forces to the drive gears
- During the **return phase**, the tread carries blades upstream through a protected, low-drag path
- Continuous motion of the tread provides smooth torque delivery to the generator

---

## Design Notes

- The tread is designed for submerged operation and continuous cyclic loading
- Link geometry prioritizes strength, alignment stability, and low friction
- Modularity allows tread length to be adjusted by changing link count

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/link_tread/`

- Production implementation (v1.0):
  `models/1.0/parts/link_tread/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
