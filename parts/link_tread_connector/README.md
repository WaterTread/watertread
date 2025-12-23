# Link Tread with Connector

## Function

The Link Tread with Connector is a modified tread element that provides a rigid, perpendicular attachment point for mounting blades to the tread system.
It enables controlled blade rotation while transmitting hydrodynamic forces from the blade into the linear tread motion.

This component forms the mechanical interface between the blade, cam follower, and the tread.

---

## Quantity

28 pcs per system

---

## Interfaces

- **Blade**
  - Blade mounts to the connector via the cam follower
  - Provides a fixed perpendicular axis for blade rotation

- **Cam Follower**
  - Connected using a low-friction pin, allowing free rotational movement
  - Transfers cam-controlled motion to blade orientation

- **Link Tread**
  - Integrated into the continuous tread chain
  - Maintains full compatibility with adjacent standard tread links

---

## LEGO Reference Parts

- [**3873** Technic Chain Tread 2.5 Wide](https://library.ldraw.org/parts/7308)  
- [**22961** Technic Axle with Perpendicular Pin Hole](https://library.ldraw.org/parts/2013)  
- [**3673** Technic Pin](https://library.ldraw.org/parts/6706)

---

## Modifications

- Link tread modified as described in the Link Tread specification
- The axle section of the perpendicular pin-hole element is removed
- The remaining pin-hole connector is repositioned and mounted on top of the tread’s top-plate surface
- This configuration forms a rigid, perpendicular blade attachment point while maintaining tread continuity

---

## Operating Role

- During the **capture phase**, the connector transmits blade-generated forces directly into the tread
- Allows the blade to rotate freely under cam control without binding
- Maintains consistent blade spacing and alignment along the tread path

---

## Design Notes

- Connector geometry prioritizes stiffness and precise alignment
- Low-friction interfaces reduce mechanical losses and wear
- Modular design allows connector links to be placed only where blades are required

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/link_tread_connector/`

- Production implementation (v1.0):
  `models/1.0/parts/link_tread_connector/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
