# Cam Follower

## Function

The cam follower interfaces between the blade and the cam, translating the cam profile into controlled blade rotation.
It ensures that each blade is guided into and held in its high-drag capture orientation during the power stroke, and released for reorientation during the return phase.

Cam followers enable precise, repeatable blade motion without requiring active control or actuators.

---

## Quantity

28 pcs per system

---

## Interfaces

- **Blade**
  - Each blade is connected to two cam followers, one at each end
  - Provides a rotational interface allowing the blade to pivot between operating states

- **Cam**
  - The cam follower rides along the cam profile during the capture phase
  - Contact geometry determines blade orientation and timing

- **Link Tread with Connector**
  - Cam follower is mounted to the tread system via a low-friction pin connection
  - Allows free rotation while transmitting linear motion

---

## LEGO Reference Parts

- [**7329** Technic Angle Connector 3-Way 60/120 Degrees](https://library.ldraw.org/parts/45842)
- [**22961** Technic Axle with Perpendicular Pin Hole](https://library.ldraw.org/parts/2013) (2 pcs)

---

## Modifications

- Reference parts are combined to form a rigid cam follower arm
- Geometry is arranged to provide sufficient clearance for rotation without interference
- Contact surfaces are shaped to maintain stable engagement with the cam profile
- Low-friction pins are used at the tread interface to minimize mechanical losses

---

## Operating Role

- During the **capture phase**, the cam follower engages the cam and rotates the blade into its vertical, high-drag orientation
- While engaged, the cam follower maintains blade angle against hydrodynamic loads
- During the **return phase**, the cam follower disengages from the cam, allowing the blade to rotate freely into a low-drag configuration

---

## Design Notes

- Cam follower mass is minimized to reduce inertial losses
- Mechanical simplicity improves reliability in submerged operation
- Passive operation ensures synchronization across all blades

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/cam_follower/`

- Production implementation (v1.0):
  `models/1.0/parts/cam_follower/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
