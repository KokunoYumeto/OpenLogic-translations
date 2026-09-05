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
await writeFile(resolve(dist, ".nojekyll"), "", "utf8");

console.log(JSON.stringify({ status: "built", output: "dist" }));
