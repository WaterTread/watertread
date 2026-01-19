import React, { useEffect, useMemo, useRef, useState } from "react";

export default function App() {
  // -----------------------
  // SETTINGS
  // -----------------------
  const BAND = 12;
  const GAP = 12;
  const CENTER_WHITE = 24;
  const RINGS = 4;

  // Blade geometry
  const cutR = 18;
  const dotR = 6;

  // -----------------------
  // PARAMETRIC BLADE (CENTERED ON HINGE Y=0)
  // -----------------------
  const BLADE_Y_TRIM = 0;

  const bladeLocal = {
    white: {
      x: 1,
      y: -BAND / 2 + BLADE_Y_TRIM,
      w: 65,
      h: BAND,
      fill: "white",
    },
    black: {
      x: 6,
      y: +BAND / 2 + BLADE_Y_TRIM,
      w: 60,
      h: BAND,
      fill: "#212326",
    },
  };

  // -----------------------
  // PRECISE PITCH (hinge + arms)
  // -----------------------
  const BLADE_COUNT = 6;
  const OVERLAP = 1;

  const leftExtent = -cutR;
  const armEnd = bladeLocal.white.x + bladeLocal.white.w;
  const rightExtent = Math.max(cutR, armEnd);

  const bladeLengthAlongLane = rightExtent - leftExtent;
  const bladePitch = bladeLengthAlongLane - OVERLAP;

  // -----------------------
  // TRACK WIDTH FROM BLADES
  // -----------------------
  const Rtrack = CENTER_WHITE / 2;
  const Ptarget = BLADE_COUNT * bladePitch;

  const Lstraight = Math.max(0, (Ptarget - 2 * Math.PI * Rtrack) / 2);
  const trackW = 2 * Rtrack + Lstraight;
  const trackH = CENTER_WHITE;

  // -----------------------
  // OUTER GEOMETRY FROM TRACK
  // -----------------------
  const sideThickness = RINGS * BAND + (RINGS - 1) * GAP;
  const outerW = trackW + 2 * sideThickness;
  const outerH = trackH + 2 * sideThickness;

  // ✅ Responsive viewBox padding (keeps margins consistent)
  const PAD = 32;

  // ✅ Now we build everything at (0,0) + padding
  const x0 = PAD;
  const y0 = PAD;

  const trackX = x0 + sideThickness;
  const trackY = y0 + sideThickness;

  // ✅ viewBox fits content automatically
  const viewW = outerW + 2 * PAD;
  const viewH = outerH + 2 * PAD;

  // -----------------------
  // RINGS
  // -----------------------
  const rrPath = (x, y, w, h) => {
    const r = h / 2;
    const x2 = x + w;
    const y2 = y + h;
    return [
      `M ${x + r} ${y}`,
      `H ${x2 - r}`,
      `A ${r} ${r} 0 0 1 ${x2} ${y + r}`,
      `V ${y2 - r}`,
      `A ${r} ${r} 0 0 1 ${x2 - r} ${y2}`,
      `H ${x + r}`,
      `A ${r} ${r} 0 0 1 ${x} ${y2 - r}`,
      `V ${y + r}`,
      `A ${r} ${r} 0 0 1 ${x + r} ${y}`,
      "Z",
    ].join(" ");
  };

  const pitchRing = BAND + GAP;

  const rings = useMemo(() => {
    return Array.from({ length: RINGS }).map((_, i) => {
      const outerInset = i * pitchRing;
      const innerInset = outerInset + BAND;

      const ox = x0 + outerInset;
      const oy = y0 + outerInset;
      const ow = outerW - outerInset * 2;
      const oh = outerH - outerInset * 2;

      const ix = x0 + innerInset;
      const iy = y0 + innerInset;
      const iw = outerW - innerInset * 2;
      const ih = outerH - innerInset * 2;

      const d = `${rrPath(ox, oy, ow, oh)} ${rrPath(ix, iy, iw, ih)}`;

      return (
        <path
          key={i}
          d={d}
          fill="#212326"
          fillRule="evenodd"
          clipRule="evenodd"
        />
      );
    });
  }, [RINGS, x0, y0, outerW, outerH, BAND, pitchRing]);

  // -----------------------
  // TRACK PARAMS
  // -----------------------
  function pillMetrics(w, h) {
    const R = h / 2;
    const L = w - 2 * R;
    const P = 2 * L + 2 * Math.PI * R;
    return { R, L, P };
  }

  const { P: P0 } = useMemo(() => pillMetrics(trackW, trackH), [trackW, trackH]);

  // Returns boundary point (px,py) + outward normal (nx,ny) at arc-length s
  function pillBoundaryByArcLength(s, x, y, w, h) {
    const { R, L, P } = pillMetrics(w, h);

    let ss = s % P;
    if (ss < 0) ss += P;

    const topStartX = x + R;
    const topY = y;
    const rightCx = x + w - R;
    const cy = y + R;
    const bottomY = y + h;
    const leftCx = x + R;

    let px, py, nx, ny;

    if (ss <= L) {
      // top straight, left->right
      px = topStartX + ss;
      py = topY;
      nx = 0;
      ny = -1;
    } else if (ss <= L + Math.PI * R) {
      // right arc, top->bottom
      const a = (ss - L) / R;
      const ang = -Math.PI / 2 + a;
      px = rightCx + R * Math.cos(ang);
      py = cy + R * Math.sin(ang);
      nx = Math.cos(ang);
      ny = Math.sin(ang);
    } else if (ss <= L + Math.PI * R + L) {
      // bottom straight, right->left
      const t = ss - (L + Math.PI * R);
      px = topStartX + (L - t);
      py = bottomY;
      nx = 0;
      ny = 1;
    } else {
      // left arc, bottom->top
      const t = ss - (2 * L + Math.PI * R);
      const a = t / R;
      const ang = Math.PI / 2 + a;
      px = leftCx + R * Math.cos(ang);
      py = cy + R * Math.sin(ang);
      nx = Math.cos(ang);
      ny = Math.sin(ang);
    }

    return { px, py, nx, ny, P };
  }

  function hingeOnTrackByS(s) {
    const b = pillBoundaryByArcLength(s, trackX, trackY, trackW, trackH);
    return {
      x: b.px + b.nx * cutR,
      y: b.py + b.ny * cutR,
    };
  }

  // -----------------------
  // ANGLES (helpers)
  // -----------------------
  const clamp01 = (t) => Math.max(0, Math.min(1, t));
  const wrap180 = (deg) => ((((deg + 180) % 360) + 360) % 360) - 180;
  const lerpAngleShortest = (a, b, t) => a + wrap180(b - a) * t;

  const smoothstep = (e0, e1, x) => {
    const t = clamp01((x - e0) / (e1 - e0));
    return t * t * (3 - 2 * t);
  };

  // -----------------------
  // GEOMETRY-BASED TARGET ANGLE (VECTOR BLEND = NO WRAP JERKS)
  // -----------------------
  function desiredBladeAngleFromS(s) {
    const b = pillBoundaryByArcLength(s, trackX, trackY, trackW, trackH);

    const normalRad = Math.atan2(b.ny, b.nx);

    // A) follow normal
    const Ar = normalRad;

    // B) normal - 90deg
    const Br = normalRad - Math.PI / 2;

    const topY = trackY;
    const bottomY = trackY + trackH;
    const midY = (topY + bottomY) * 0.5;

    // You found 0.4 feels good -> keep it
    const band = trackH * 0.4;

    const w = smoothstep(midY - band, midY + band, b.py);

    // Vector blend (stable)
    const ax = Math.cos(Ar),
      ay = Math.sin(Ar);
    const bx = Math.cos(Br),
      by = Math.sin(Br);

    let vx = (1 - w) * ax + w * bx;
    let vy = (1 - w) * ay + w * by;

    const len = Math.hypot(vx, vy) || 1;
    vx /= len;
    vy /= len;

    return (Math.atan2(vy, vx) * 180) / Math.PI;
  }

  function Blade({ id, s, angle }) {
    const p = hingeOnTrackByS(s);
    return (
      <g id={id} transform={`translate(${p.x} ${p.y}) rotate(${angle})`}>
        <rect
          x={bladeLocal.white.x}
          y={bladeLocal.white.y}
          width={bladeLocal.white.w}
          height={bladeLocal.white.h}
          fill={bladeLocal.white.fill}
        />
        <rect
          x={bladeLocal.black.x}
          y={bladeLocal.black.y}
          width={bladeLocal.black.w}
          height={bladeLocal.black.h}
          fill={bladeLocal.black.fill}
        />
        <circle cx="0" cy="0" r={cutR} fill="white" />
        <circle cx="0" cy="0" r={dotR} fill="#212326" />
      </g>
    );
  }

  // -----------------------
  // ANIMATION
  // -----------------------
  const speed = 35;
  const angleResponse = 20;

  const bladesRef = useRef(
    Array.from({ length: BLADE_COUNT }).map((_, k) => ({
      id: `blade-${k}`,
      s: (k * bladePitch) % P0,
      angle: 0,
    }))
  );

  const [renderBlades, setRenderBlades] = useState(() => bladesRef.current);

  useEffect(() => {
    let raf = 0;
    let last = performance.now();

    const tick = (now) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;

      const alpha = 1 - Math.exp(-angleResponse * dt);

      const next = bladesRef.current.map((b) => {
        let s = (b.s + speed * dt) % P0;
        if (s < 0) s += P0;

        const targetAngle = desiredBladeAngleFromS(s);
        const angle = lerpAngleShortest(b.angle, targetAngle, alpha);

        return { ...b, s, angle };
      });

      bladesRef.current = next;
      setRenderBlades(next);
      raf = requestAnimationFrame(tick);
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [P0, speed, angleResponse, bladePitch]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-4xl p-8">
        <svg
          viewBox={`0 0 ${viewW} ${viewH}`}
          className="w-full h-auto"
          xmlns="http://www.w3.org/2000/svg"
          shapeRendering="geometricPrecision"
          preserveAspectRatio="xMidYMid meet"
        >
          {rings}
          {renderBlades.map((b) => (
            <Blade key={b.id} id={b.id} s={b.s} angle={b.angle} />
          ))}
        </svg>
      </div>
    </div>
  );
}
