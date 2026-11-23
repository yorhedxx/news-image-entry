// Entry for make.fun's "Sum up 23 November's world news in one image".
//
// The poster beside this file (entry.png) was drawn from the day's reporting
// by build_poster.py, which ships in this repository; this program's whole
// job is to place those exact bytes at /output/entry.png, the file the
// competition's gate checks and its judge sees. It reads nothing else and
// writes nothing else, so both grader runs produce identical bytes.
//
// Locally, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const MAX_BYTES = 1048576; // the gate's cap: a whole PNG or JPEG of at most 1 MiB

const source = new URL("./entry.png", import.meta.url);
const size = statSync(source).size;
if (size === 0 || size > MAX_BYTES) {
  throw new Error(`entry.png is ${size} bytes; the gate allows 1..${MAX_BYTES}`);
}

// The gate tells PNG from JPEG by the first bytes; check ours really is one
// of the two before copying, so a corrupt asset fails here, not at the gate.
const head = readFileSync(source).subarray(0, 8);
const isPng = head.equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
const isJpeg = head[0] === 0xff && head[1] === 0xd8 && head[2] === 0xff;
if (!isPng && !isJpeg) {
  throw new Error("entry.png starts with neither the PNG nor the JPEG signature");
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
copyFileSync(source, join(outDir, "entry.png"));
