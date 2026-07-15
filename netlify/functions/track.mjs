import { getStore } from "@netlify/blobs";
export default async (req) => {
  const url = new URL(req.url);
  let p = (url.searchParams.get("p") || "/").slice(0, 200);
  if (p.indexOf("/admin") === 0) return new Response(null, { status: 204 });
  const kst = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
  const store = getStore({ name: "stats", consistency: "strong" });
  for (const key of ["T:" + kst, "P:" + p]) {
    const cur = parseInt((await store.get(key)) || "0", 10) + 1;
    await store.set(key, String(cur));
  }
  return new Response(null, { status: 204 });
};
export const config = { path: "/api/track" };
