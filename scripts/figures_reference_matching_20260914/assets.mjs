import fs from "node:fs/promises";
import { C } from "./style.mjs";

/** Place a raster panel. Rasters are only used for photographs and score fields. */
export async function image(slide, name, file, x, y, w, h, opts = {}) {
  const { fit = "contain", crop = null, alt = name } = opts;
  const blob = new Uint8Array(await fs.readFile(file));
  return slide.images.add({
    blob,
    contentType: "image/png",
    alt,
    fit,
    ...(crop ? { crop } : {}),
    position: { left: x, top: y, width: w, height: h },
  });
}

export function frame(slide, name, x, y, w, h, color = C.grayLine, lw = 1.2) {
  return slide.shapes.add({
    geometry: "rect",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: color, width: lw },
  });
}

/**
 * Predicted-contour panel: the real query photograph with the model-derived contour
 * polygons drawn as editable custom paths in the 448x448 evaluation space.
 * The polygons always come from the frozen score map, never from ground truth.
 */
export async function contourOverlay(slide, name, queryImage, polys, x, y, size) {
  await image(slide, name + "-query", queryImage, x, y, size, size, { fit: "cover" });
  const paths = polys.map((points) => ({
    width: 448,
    height: 448,
    commands: [
      { moveTo: { x: points[0][0], y: points[0][1] } },
      ...points.slice(1).map((p) => ({ lineTo: { x: p[0], y: p[1] } })),
      { close: {} },
    ],
  }));
  return slide.shapes.add({
    name: name + "-contour",
    geometry: "custom",
    position: { left: x, top: y, width: size, height: size },
    fill: "none",
    line: { fill: "#FF382E", width: 2.2 },
    customPaths: paths,
  });
}
