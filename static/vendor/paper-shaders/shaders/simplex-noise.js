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

void main() {
  vec2 uv = v_objectUV;
  float t = u_time * u_speed * 0.2;

  /* Domain-warped noise: the sample position is itself pushed around by a
     second, independently-evolving noise field (two more snoise lookups on
     different phases/directions) instead of just panning uv by a straight
     time vector. Plain "uv + t*dir" is a single linear drift — everything
     slides one way, which is what read as "right to left" — warping the
     coordinate makes the blobs swirl, stretch and fold into each other from
     no single direction, closer to the reference's organic movement. */
  vec2 warp = vec2(
    snoise(uv * u_noiseScale * 1.3 + vec2(t * 0.6, t * -0.35) + 11.3),
    snoise(uv * u_noiseScale * 1.3 + vec2(t * -0.45, t * 0.55) + 47.1)
  );

  float n = snoise(uv * u_noiseScale * 3.0 + warp * 0.9 + vec2(t * 0.25, t * -0.18));
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
