const GL = {
  ZERO: 0,
  ONE: 1,
  SRC_COLOR: 0x0300,
  ONE_MINUS_SRC_COLOR: 0x0301,
  SRC_ALPHA: 0x0302,
  ONE_MINUS_SRC_ALPHA: 0x0303,
  DST_ALPHA: 0x0304,
  ONE_MINUS_DST_ALPHA: 0x0305,
  DST_COLOR: 0x0306,
  ONE_MINUS_DST_COLOR: 0x0307,
  SRC_ALPHA_SATURATE: 0x0308,
  CONSTANT_COLOR: 0x8001,
  ONE_MINUS_CONSTANT_COLOR: 0x8002,
  CONSTANT_ALPHA: 0x8003,
  DEPTH_TEST: 0x0b71,
  ONE_MINUS_CONSTANT_ALPHA: 0x8004,
  FUNC_ADD: 0x8006,
  BLEND: 0x0be2,
  FUNC_SUBTRACT: 0x800a,
  FUNC_REVERSE_SUBTRACT: 0x800b,
};

// https://github.com/uber/kepler.gl/blob/b6380f21fe8243db6bbf72e74762e3fc7224665b/src/constants/default-settings.js#L482
export function webGLInit(gl: WebGLRenderingContext) {
  if (!gl || !gl.disable) {
    console.warn("WebGL not supported in this environment");
    return;
  }

  gl.disable(GL.DEPTH_TEST); // @ts-ignore
  gl.getExtension("OES_element_index_uint");
  gl.enable(GL.BLEND);
  gl.blendFunc(GL.SRC_ALPHA, GL.DST_ALPHA);
  gl.blendEquation(GL.FUNC_ADD);
}

export default function blend(gl: WebGLRenderingContext) {
  webGLInit(gl);
}
