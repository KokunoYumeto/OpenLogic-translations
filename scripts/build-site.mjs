import { cp, mkdir, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const dist = resolve(root, "dist");

await rm(dist, { recursive: true, force: true });
await mkdir(resolve(dist, "catalogue"), { recursive: true });
await cp(resolve(root, "index.html"), resolve(dist, "index.html"));
await cp(resolve(root, "site.css"), resolve(dist, "site.css"));
await cp(resolve(root, "site.js"), resolve(dist, "site.js"));
await cp(resolve(root, "catalogue", "editions.json"), resolve(dist, "catalogue", "editions.json"));
await cp(resolve(root, "README.md"), resolve(dist, "README.md"));
await mkdir(resolve(dist, "evidence"), { recursive: true });
await cp(resolve(root, "evidence"), resolve(dist, "evidence"), { recursive: true });
// The canonical public reader stays on GitHub Pages. Its 504 MB source mirror
// exceeds Sites' 256 MiB archive cap; the hub links directly to that same reader.
// Preserve a useful fallback for the older relative reader entrypoint.
await mkdir(resolve(dist, "accessible", "en"), { recursive: true });
await writeFile(resolve(dist, "accessible", "en", "index.html"), '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Accessible Open Logic</title><meta http-equiv="refresh" content="0;url=https://kokunoyumeto.github.io/OpenLogic-translations/accessible/en/"><p><a href="https://kokunoyumeto.github.io/OpenLogic-translations/accessible/en/">Open the accessible English book</a></p></html>', "utf8");
await writeFile(resolve(dist, ".nojekyll"), "", "utf8");

console.log(JSON.stringify({ status: "built", output: "dist" }));
