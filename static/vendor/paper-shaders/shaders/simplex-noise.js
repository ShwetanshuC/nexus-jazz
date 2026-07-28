/* * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                    Paper Shaders                    *
 *       https://github.com/paper-design/shaders       *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 * Not one of the pack's shipped components (the real `SimplexNoise` lives
 * in @paper-design/shaders-react, which isn't vendored here) — hand-rolled
 * to match its actual look from the reference: raw simplex noise (no fbm —
 * the real component doesn't layer octaves, which is what made the first
 * attempt at this read as smoky haze instead of bold contour blobs) posterized
 * into colour BANDS across a palette, `u_stepsPerColor` extra shades between
 * each base colour, `u_softness` switching between a hard contour-map edge
 * (0) and a smooth gradient (1) — same props as the real component. */

import {} from "../shader-sizing.js";
import { simplexNoise } from "../shader-utils.js";

const simplexNoiseMeta = {
  maxColorCount: 10
};

const simplexNoiseFragmentShader = `#version 300 es
precision mediump float;

uniform float u_time;

uniform vec4 u_colors[${simplexNoiseMeta.maxColorCount}];
uniform float u_colorsCount;
uniform float u_softness;
/* Named distinctly from the vertex shader's own u_scale/u_rotation (object
   fit/sizing) — reusing those names double-applies the transform (once in
   the vertex stage, once again here) and the two fights/cancel out, which
   is why changing "scale" first appeared to do nothing. */
uniform float u_noiseScale;
uniform float u_speed;

in vec2 v_objectUV;

out vec4 fragColor;

${simplexNoise}

/* 3D simplex noise (classic Ashima/McEwan-Gustavson webgl-noise, public
   domain) — GLSL overloads by parameter type, so this snoise() sits
   alongside the 2D one above without clashing. The 2D version plus a
   translation drift (two earlier passes here) could only ever SLIDE the
   pattern: same field, same shapes, moved around — which is why it kept
   reading as the whole frame panning left/right/up/down no matter how the
   drift vector was tuned (2026-07-27, user report, twice). Real "blobs
   growing into each other, merging, splitting" motion needs the noise
   FIELD itself to change over time, not just the sample window — that's
   what feeding time in as a genuine third dimension (z = time) gives you:
   every pixel's neighbourhood evolves independently, so band boundaries
   actually deform instead of translating in lockstep. */
vec4 permute(vec4 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }
vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
float snoise(vec3 v) {
  const vec2 C = vec2(1.0 / 6.0, 1.0 / 3.0);
  const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

  vec3 i  = floor(v + dot(v, C.yyy));
  vec3 x0 = v - i + dot(i, C.xxx);

  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min(g.xyz, l.zxy);
  vec3 i2 = max(g.xyz, l.zxy);

  vec3 x1 = x0 - i1 + 1.0 * C.xxx;
  vec3 x2 = x0 - i2 + 2.0 * C.xxx;
  vec3 x3 = x0 - 1.0 + 3.0 * C.xxx;

  i = mod(i, 289.0);
  vec4 p = permute(permute(permute(
              i.z + vec4(0.0, i1.z, i2.z, 1.0))
            + i.y + vec4(0.0, i1.y, i2.y, 1.0))
            + i.x + vec4(0.0, i1.x, i2.x, 1.0));

  float n_ = 1.0 / 7.0;
  vec3 ns = n_ * D.wyz - D.xzx;

  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);

  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_);

  vec4 x = x_ * ns.x + ns.yyyy;
  vec4 y = y_ * ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);

  vec4 b0 = vec4(x.xy, y.xy);
  vec4 b1 = vec4(x.zw, y.zw);

  vec4 s0 = floor(b0) * 2.0 + 1.0;
  vec4 s1 = floor(b1) * 2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));

  vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
  vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;

  vec3 p0 = vec3(a0.xy, h.x);
  vec3 p1 = vec3(a0.zw, h.y);
  vec3 p2 = vec3(a1.xy, h.z);
  vec3 p3 = vec3(a1.zw, h.w);

  vec4 norm = taylorInvSqrt(vec4(dot(p0, p0), dot(p1, p1), dot(p2, p2), dot(p3, p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;

  vec4 m = max(0.6 - vec4(dot(x0, x0), dot(x1, x1), dot(x2, x2), dot(x3, x3)), 0.0);
  m = m * m;
  return 42.0 * dot(m * m, vec4(dot(p0, x0), dot(p1, x1), dot(p2, x2), dot(p3, x3)));
}

void main() {
  vec2 uv = v_objectUV;
  float t = u_time * u_speed * 0.35;

  /* NO x/y offset added to the sample position anymore — that was the
     bug behind two straight reports of "it just slides/pans": ANY term
     added to uv before it's fed to the noise function shifts the whole
     field by the same amount at every pixel, which the eye reads as rigid
     translation no matter how small it's dialed relative to a z-morph
     mixed in alongside it (a subtle local deformation loses to an obvious
     global shift every time, even when the deformation is "technically"
     also happening). The z axis IS time, and it is now the ONLY input
     that changes — every pixel's neighbourhood evolves independently
     because x, y and z all feed the same 3D noise field jointly, so
     blobs genuinely grow, shrink, split and merge in place. There is no
     motion left in this shader that isn't that. */
  /* z-rate dropped hard (2.4 → 0.45): at the old rate the field cycled
     through a full noise period in ~1.2s, which reads as boiling/blurred
     rather than the slow "unhurried" drift the brand wants — and mixing
     that with an equally-fast second field (below) compounded into a
     genuinely blurry look, not just a fast one (2026-07-27, user report).
     Full slow cycle now takes closer to 25-30s, matching the pacing
     established for the (now-removed) xy drift version. */
  float n = snoise(vec3(uv * u_noiseScale, t * 0.45));

  /* A second, higher-frequency evolving field, blended in to add living
     texture inside the big contour rings — echoes the real component's
     spot variant. Zeroed out (2026-07-28, fourth pass): even a small blend
     was enough to nudge pixels across a ring boundary unpredictably,
     softening exactly the crisp edges the reference's clean rings need.
     Left wired in (mix amount 0.0) rather than deleted, in case a future
     pass wants a little texture back once the ring definition is solid. */
  float spots = snoise(vec3(uv * u_noiseScale * 2.4, t * 0.7 + 50.0));
  n = mix(n, spots, 0.0);

  n = n * 0.5 + 0.5; // 0..1

  float bands = max(u_colorsCount - 1.0, 1.0);
  float pos = clamp(n, 0.0, 0.9999) * bands;
  float idx = floor(pos);
  float frac = pos - idx;

  /* u_softness 0 = hard contour edge (snap to nearest band, like a
     topographic map); 1 = fully smooth gradient across the whole band. */
  float edge = mix(0.02, 0.5, u_softness);
  float mixAmt = smoothstep(0.5 - edge, 0.5 + edge, frac);

  int i0 = int(idx);
  int i1 = int(min(idx + 1.0, bands));
  vec3 color = mix(u_colors[i0].rgb, u_colors[i1].rgb, mixAmt);

  fragColor = vec4(color, 1.0);
}
`;

export {
  simplexNoiseFragmentShader,
  simplexNoiseMeta
};
