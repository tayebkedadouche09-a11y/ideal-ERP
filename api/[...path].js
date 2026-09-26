const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
  "host",
  "content-length",
  "content-encoding",
]);

function getPath(req) {
  const value = req.query?.path;
  if (Array.isArray(value)) return value.join("/");
  if (typeof value === "string") return value;
  return "";
}

async function readBody(req) {
  if (req.method === "GET" || req.method === "HEAD") return undefined;
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return chunks.length ? Buffer.concat(chunks) : undefined;
}

export default async function handler(req, res) {
  const backend = process.env.FRAPPE_BACKEND_URL?.trim();

  if (!backend) {
    return res.status(503).json({
      ok: false,
      error: "FRAPPE_BACKEND_URL is not configured on Vercel.",
    });
  }

  let backendBase;
  try {
    backendBase = new URL(backend.endsWith("/") ? backend : backend + "/");
  } catch {
    return res.status(500).json({ ok: false, error: "FRAPPE_BACKEND_URL is invalid." });
  }

  const path = getPath(req);
  const target = new URL(path, backendBase);
  const incomingUrl = new URL(req.url || "/", "https://vercel.invalid");
  target.search = incomingUrl.search;

  const headers = new Headers();
  for (const [key, value] of Object.entries(req.headers || {})) {
    if (value == null || HOP_BY_HOP_HEADERS.has(key.toLowerCase())) continue;
    if (Array.isArray(value)) value.forEach((item) => headers.append(key, item));
    else headers.set(key, String(value));
  }
  headers.set("accept-encoding", "identity");

  const body = await readBody(req);

  let upstream;
  try {
    upstream = await fetch(target, {
      method: req.method,
      headers,
      body,
      redirect: "manual",
    });
  } catch (error) {
    return res.status(502).json({
      ok: false,
      error: "Unable to reach the Frappe backend.",
      detail: error instanceof Error ? error.message : String(error),
    });
  }

  for (const [key, value] of upstream.headers.entries()) {
    if (key === "set-cookie" || HOP_BY_HOP_HEADERS.has(key)) continue;

    if (key === "location" && value.startsWith(backendBase.origin)) {
      res.setHeader("location", value.slice(backendBase.origin.length) || "/");
      continue;
    }
    res.setHeader(key, value);
  }

  const setCookies = (upstream.headers.getSetCookie?.() || []).map((cookie) =>
    cookie
      .replace(/;\\s*Domain=[^;]*/gi, "")
      .replace(/;\\s*SameSite=None/gi, "; SameSite=Lax")
  );
  if (setCookies.length) res.setHeader("set-cookie", setCookies);

  res.status(upstream.status).send(Buffer.from(await upstream.arrayBuffer()));
}

export const config = {
  api: { bodyParser: false },
};
