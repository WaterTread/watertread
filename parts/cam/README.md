# Cam

## Function

The cam is a fixed, passive control element that defines the blade capture geometry and timing.
It engages with the cam followers during the capture phase to rotate and hold each blade in its high-drag orientation while it traverses the active energy capture region.

The cam operates without actuators or active control, relying solely on its geometric profile.

---

## Quantity

2 pcs per system (one per side)

---

## Interfaces

- **Cam Follower**
  - Cam followers ride along the cam profile during the capture phase
  - The cam profile determines blade orientation angle, timing, and dwell

- **Hydrodynamic Side Panel**
  - The cam is mounted to the inner surface of the hydrodynamic side panel
  - Side panel provides structural support and precise alignment

- **Frame**
  - Cam position is fixed relative to the frame to ensure repeatable blade motion

---

## Geometry Description

- The cam is a **partial cam rail**, active only along the capture path
- Outside the capture region, cam followers disengage freely
- Cam geometry is shaped to:
  - Rotate blades smoothly into vertical orientation
  - Maintain blade angle during peak loading
  - Release blades cleanly into the return phase

---

## Operating Role

- During the **capture phase**, the cam enforces blade orientation against hydrodynamic loads
- During the **transition phase**, the cam profile allows controlled release
- During the **return phase**, the cam does not interact with the cam follower

---

## Design Notes

- Cam profile is optimized to minimize impact loads and wear
- Passive geometry ensures inherent synchronization across all blades
- Fixed cam eliminates the need for sensors, controls, or actuators
- Cam shape may evolve between system versions while maintaining the same functional role

---

## Implementations

- Prototype implementation:
  `models/prototype/parts/cam/`

- Production implementation (v1.0):
  `models/1.0/parts/cam/`

---

## Licensing

This part is provided for non-commercial use under the
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0) license.

Commercial use requires a separate license.
See the repository root `COMMERCIAL.md` for details.
