# Parts Overview

This section documents the mechanical and structural components of the WaterTread system.

The parts listed here describe the **concept-level design** and functional interfaces of each component.  
Concrete, version-specific implementations of these parts are located under the `models/` directory.

---

## How This Section Is Organized

- Each part has its own directory under `parts/`
- Each part directory contains a `README.md` describing:
  - The function of the part
  - Interfaces to other components
  - Quantities used in the system
  - Notes relevant across versions
- Version-specific geometry, dimensions, and manufacturing files are stored under:
  - `models/prototype/parts/`
  - `models/1.0/parts/`
  - future version directories as applicable

This separation keeps the conceptual design stable while allowing implementations to evolve between system versions.

---

## Parts Index

- [Blade](blade/)
- [Cam Follower](cam_follower/)
- [Link Tread](link_tread/)
- [Link Tread with Connector](link_tread_connector/)
- [Cam](cam/)
- [Return Guide](return_guide/)
- [40-Tooth Gear](gear_40t/)
- [8-Tooth Pinion](pinion_8t/)
- [Axle](axle/)
- [Frame](frame/)
- [Front Axle Mount](front_axle_mount/)
- [Rear Axle Mount](rear_axle_mount/)
- [Hydrodynamic Side Panel](side_panel/)
- [Hydrodynamic Center Panel](center_panel/)
- [Flow Diverter](flow_diverter/)

---

## Versioning Policy

Parts in this directory are **not individually versioned**.

Instead:
- The WaterTread system is versioned as a whole (e.g. Prototype, v1.0, v2.0)
- Any dimensional or structural change to a part is reflected by a new system version
- Concept-level descriptions in `parts/` remain valid across versions unless explicitly stated

See `models/` for version-specific implementations.

---

## Units and Conventions

- Linear dimensions may be expressed in LEGO units (L) for prototype reference
- Production models use metric units (mm)
- Coordinate systems and orientation are defined relative to the direction of water flow

Additional shared conventions may be documented in a future `COMMON.md` file.

---

## Licensing Note

The part descriptions and associated files are provided for non-commercial use under the CC BY-NC-SA 4.0 license.

Commercial use of any part or system implementation requires a separate license.  
See the repository root `COMMERCIAL.md` for details.
