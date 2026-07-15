import { getStore } from "@netlify/blobs";
const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json" } });
export default async (req) => {
  const url = new URL(req.url);
  if (url.searchParams.get("pw") !== "gamma") return json({ error: "unauthorized" }, 401);
  const store = getStore({ name: "stats", consistency: "strong" });
  const kst = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
  if (url.searchParams.get("reset") === "1") {
    for (const pre of ["T:", "P:"]) {
      const l = await store.list({ prefix: pre });
      for (const b of l.blobs) await store.delete(b.key);
    }
    return json({ reset: true });
  }
  const td = await store.list({ prefix: "T:" });
  const days = [];
  for (const b of td.blobs) days.push({ date: b.key.slice(2), count: parseInt((await store.get(b.key)) || "0", 10) });
  days.sort((a, b) => (a.date < b.date ? -1 : 1));
  const pd = await store.list({ prefix: "P:" });
  const posts = [];
  for (const b of pd.blobs) posts.push({ path: b.key.slice(2), count: parseInt((await store.get(b.key)) || "0", 10) });
  posts.sort((a, b) => b.count - a.count);
  const total = posts.reduce((s, x) => s + x.count, 0);
  const today = (days.find((d) => d.date === kst) || { count: 0 }).count;
  return json({ today, total, days, posts, date: kst });
};
export const config = { path: "/api/stats" };
