export default function App() {
  // --- Visual rhythm ---
  const BAND = 12;
  const GAP = 12;
  const CENTER_WHITE = 24;
  const RINGS = 4;

  // --- Ribbon geometry ---
  const sideThickness = RINGS * BAND + (RINGS - 1) * GAP; // 84
  const outerH = CENTER_WHITE + 2 * sideThickness; // 192
  const outerW = 420;

  const viewW = 700;
  const viewH = 350;

  const x0 = (viewW - outerW) / 2;
  const y0 = (viewH - outerH) / 2;

  // --- Rounded rect ("pill") path helper ---
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

  // --- Rings ---
  const pitch = BAND + GAP; // 24
  const rings = Array.from({ length: RINGS }).map((_, i) => {
    const outerInset = i * pitch;
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
    return <path key={i} d={d} fill="#212326" fillRule="evenodd" clipRule="evenodd" />;
  });

  // --- Track = innermost opening pill ---
  const trackX = x0 + sideThickness;
  const trackY = y0 + sideThickness;
  const trackW = outerW - 2 * sideThickness;
  const trackH = CENTER_WHITE;

  // --- Blade geometry (LOCAL space) ---
  const cutR = 18; // hinge outer white radius
  const dotR = 6;

  // Local frame convention:
  // +X = outward normal direction (arms extend this way)
  // +Y = clockwise tangent direction (downwards along the perimeter)
  const bladeLocal = {
    white: { x: 1, y: 6, w: 65, h: BAND, fill: "white" },
    black: { x: 6, y: 18, w: 60, h: BAND, fill: "#212326" }, // x=6 matches your "follows track" feel
  };

  // -------------------------------
  // Track math (arc-length param)
  // -------------------------------
  function pillMetrics(w, h) {
    const R = h / 2;
    const L = w - 2 * R;
    const P = 2 * L + 2 * Math.PI * R;
    return { R, L, P };
  }

  const { R: R0, L: L0, P: P0 } = pillMetrics(trackW, trackH);

  /**
   * Arc-length parameter s in [0, P) clockwise starting at TOP-LEFT of top straight (x+R, y).
   * Returns boundary point B(s), outward normal n(s), tangent t(s), and track angle (normal angle).
   */
  function pillBoundaryByArcLength(s, x, y, w, h) {
    const { R, L, P } = pillMetrics(w, h);

    // Wrap s
    let ss = s % P;
    if (ss < 0) ss += P;

    const topStartX = x + R;
    const topY = y;
    const rightCx = x + w - R;
    const cy = y + R;
    const bottomY = y + h;
    const leftCx = x + R;

    let px, py, nx, ny, tx, ty;

    if (ss <= L) {
      // Top straight (moving right)
      px = topStartX + ss;
      py = topY;
      nx = 0; ny = -1;
      tx = 1; ty = 0;
    } else if (ss <= L + Math.PI * R) {
      // Right arc (clockwise): angle -90 -> +90
      const a = (ss - L) / R; // 0..PI
      const ang = -Math.PI / 2 + a;
      px = rightCx + R * Math.cos(ang);
      py = cy + R * Math.sin(ang);
      nx = Math.cos(ang); ny = Math.sin(ang);
      tx = -ny; ty = nx;
    } else if (ss <= L + Math.PI * R + L) {
      // Bottom straight (moving left)
      const t = ss - (L + Math.PI * R);
      px = topStartX + (L - t);
      py = bottomY;
      nx = 0; ny = 1;
      tx = -1; ty = 0;
    } else {
      // Left arc (clockwise): angle +90 -> +270
      const t = ss - (2 * L + Math.PI * R);
      const a = t / R; // 0..PI
      const ang = Math.PI / 2 + a;
      px = leftCx + R * Math.cos(ang);
      py = cy + R * Math.sin(ang);
      nx = Math.cos(ang); ny = Math.sin(ang);
      tx = -ny; ty = nx;
    }

    const normalDeg = (Math.atan2(ny, nx) * 180) / Math.PI;
    const tangentDeg = (Math.atan2(ty, tx) * 180) / Math.PI;

    return { px, py, nx, ny, tx, ty, normalDeg, tangentDeg, R, L, P };
  }

  function hingeOnTrackByS(s, cutRadius) {
    const b = pillBoundaryByArcLength(s, trackX, trackY, trackW, trackH);
    return {
      x: b.px + b.nx * cutRadius,
      y: b.py + b.ny * cutRadius,
      trackNormalDeg: b.normalDeg,
      trackTangentDeg: b.tangentDeg,
      P: b.P,
      L: b.L,
      R: b.R,
    };
  }

  // -------------------------------
  // Blade component (ONE)
  // -------------------------------
  function Blade({ id, s, spinDeg = 0 }) {
    const p = hingeOnTrackByS(s, cutR);

    // Core rule: blade points along outward normal, plus optional spin.
    const rot = p.trackNormalDeg + spinDeg;

    return (
      <g id={id} transform={`translate(${p.x} ${p.y}) rotate(${rot})`}>
        <circle cx="0" cy="0" r={cutR} fill="white" />
        <circle cx="0" cy="0" r={dotR} fill="#212326" />

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
      </g>
    );
  }

  // -------------------------------
  // Even spacing + top/bottom columns aligned
  // -------------------------------
  // We pick two columns on the TOP straight by choosing x-fractions.
  // Then we compute the matching BOTTOM arc-length s so the x is identical.
  //
  // Top straight s = f * L
  // Bottom straight begins at s = L + pi*R, and runs right->left. Matching x => use (1-f).
  //
  // This gives genuinely symmetric spacing and exact x-alignment.

  const f1 = 0.30;
  const f2 = 0.70;

  const sTop1 = f1 * L0;
  const sTop2 = f2 * L0;

  const sBottom1 = L0 + Math.PI * R0 + (1 - f1) * L0;
  const sBottom2 = L0 + Math.PI * R0 + (1 - f2) * L0;

  // Ends: midpoints of right/left arcs (for “end hinges”)
  const sRightEnd = L0 + (Math.PI / 2) * R0;
  const sLeftEnd = 2 * L0 + Math.PI * R0 + (Math.PI / 2) * R0;

  // -------------------------------
  // Optional: spin functions (for animation later)
  // -------------------------------
  // Example: spin depends on where you are, or time.
  // For now static defaults:
  const spinTop = 0;

  // Bottom in your static had different spins (45 and 0) relative to track normal (which is +90 on bottom).
  // Here we set those as "spinDeg" values:
  // - track normal at bottom straight is +90
  // - if you want absolute 45 => spin = 45 - 90 = -45
  // - if you want absolute 0  => spin = 0  - 90 = -90
  const spinBottom1 = -45;
  const spinBottom2 = -90;

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-4xl p-8">
        <svg
          viewBox={`0 0 ${viewW} ${viewH}`}
          className="w-full h-auto"
          xmlns="http://www.w3.org/2000/svg"
          shapeRendering="geometricPrecision"
        >
          {rings}

          {/* Ends (auto, locked to innermost track ends) */}
          <Blade id="blade-left-end" s={sLeftEnd} />
          <Blade id="blade-right-end" s={sRightEnd} />

          {/* 2 up (top straight) */}
          <Blade id="blade-top-1" s={sTop1} spinDeg={spinTop} />
          <Blade id="blade-top-2" s={sTop2} spinDeg={spinTop} />

          {/* 2 down (bottom straight), x-aligned with top */}
          <Blade id="blade-bottom-1" s={sBottom1} spinDeg={spinBottom1} />
          <Blade id="blade-bottom-2" s={sBottom2} spinDeg={spinBottom2} />
        </svg>

        <div className="mt-12 text-center text-neutral-800 text-sm tracking-widest font-medium">
          GEOMETRIC LOGO
        </div>
      </div>
    </div>
  );
}
