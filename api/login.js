import proxy from "./[...path].js";

export default function handler(req, res) {
  req.query = { ...(req.query || {}), path: ["login"] };
  return proxy(req, res);
}
