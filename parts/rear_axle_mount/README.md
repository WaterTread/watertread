# Rear Axle Mount

## Function

The rear axle mount supports the rear axle while allowing controlled axial movement to maintain proper tread tension.
It incorporates a spring-loaded mechanism that compensates for wear, thermal expansion, and load variations, ensuring consistent tread engagement and smooth operation.

Unlike the front axle mount, the rear axle mount is intentionally compliant.

---

## LEGO Technic reference part

- [Technic Shock Absorber 18L (Extended)](https://library.ldraw.org/parts/26093)

---

## Quantity

2 pcs per system (one per side)

---

## Interfaces

- **Axle**
  - Supports the rear axle shaft
  - Allows limited axial displacement for tension adjustment

- **Frame**
  - Mount is connected to the frame via spring housings
  - Frame defines the allowable movement range

- **Gear**
  - Maintains correct gear meshing under varying load and tension conditions

- **Link Tread**
  - Indirectly maintains proper tread tension and alignment

---

## Reference Configuration

- Implemented as a spring-loaded pillow block bearing assembly
- Consists of:
  - A bearing block supporting the axle shaft
  - Integrated coil springs housed in tubular guides
- Springs bias the axle outward to maintain tread tension

---

## Operating Role

- Maintains consistent tread tension during operation
- Compensates for manufacturing tolerances and wear
- Reduces shock loads on the drivetrain during transient conditions

---

## Design Notes

- Spring stiffness should be selected to balance tension stability and mechanical losses
- Axial travel range is limited to prevent misalignment
- Bearing selection should consider submerged or splash-zone operation
- Symmetric mounts on both sides ensure even load distribution

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/rear_axle_mount/`

- Production implementation (v1.0):
  `models/1.0/parts/rear_axle_mount/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
