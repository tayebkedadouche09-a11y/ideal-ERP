import proxy from "./[...path].js";

export default function handler(req, res) {
  const tail = req.query?.path;
  req.query = { ...(req.query || {}), path: ["app", ...(Array.isArray(tail) ? tail : [])] };
  return proxy(req, res);
}
