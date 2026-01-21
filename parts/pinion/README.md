# Pinion

[See 3D-model](./pinion.stl)

## Function

The pinion is a small drive gear that interfaces with the primary gear to increase rotational speed for the generator.
It adapts the relatively slow, high-torque motion of the tread system into a higher-speed rotation suitable for efficient electrical generation.

The pinion enables flexible gear ratio selection without altering the primary tread geometry.

---

## Quantity

1 pc per system (minimum configuration)

Additional pinions or generators may be added depending on system scaling and power requirements.

---

## Interfaces

- **Gear**
  - Pinion meshes with the primary gear
  - Gear ratio determines output speed and torque characteristics

- **Generator**
  - Pinion is mounted directly to the generator shaft or via a coupling
  - Transfers rotational motion into the generator input

- **Axle / Bearing Mount**
  - Pinion alignment is maintained by the generator mount or dedicated bearing support

---

## Reference Geometry

- Tooth count, pitch, and diameter are implementation-specific
- Pinion size is selected to achieve the desired speed increase
- Multiple gear ratios may be evaluated across system versions

---

## LEGO Reference Part (Prototype)

- **3647** Technic Gear 8 Tooth

Reference parts are used for prototyping only and do not constrain production geometry.

---

## Operating Role

- Increases rotational speed relative to the tread drive gear
- Allows the generator to operate closer to its optimal efficiency range
- Enables system tuning for different flow conditions and generator types

---

## Design Notes

- Smaller pinions increase speed but reduce torque margin
- Gear ratio selection balances efficiency, durability, and generator requirements
- Pinion may be replaced by alternative transmission elements in future versions (e.g. multi-stage gearing)

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/pinion/`

- Production implementation (v1.0):
  `models/1.0/parts/pinion/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
