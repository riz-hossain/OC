const fs = require("fs");
const http = require("http");
const path = require("path");

const rootDir = __dirname;
const port = Number.parseInt(process.env.PORT || "5177", 10);
const host = process.env.HOST || "127.0.0.1";

const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".map": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".txt": "text/plain; charset=utf-8",
  ".webmanifest": "application/manifest+json; charset=utf-8"
};

const allowedFiles = new Set(["orange_circle_platformer.html"]);
const allowedDirectories = new Set(["assets", "public"]);

function resolveRequestPath(requestUrl) {
  const url = new URL(requestUrl, `http://${host}:${port}`);
  const pathname = decodeURIComponent(url.pathname);
  const requestedPath = pathname === "/" ? "/orange_circle_platformer.html" : pathname;
  const normalized = path.normalize(requestedPath).replace(/^([/\\])+/, "");
  const filePath = path.join(rootDir, normalized);
  const relativePath = path.relative(rootDir, filePath);

  if (relativePath.startsWith("..") || path.isAbsolute(relativePath)) {
    return null;
  }

  const topLevel = relativePath.split(path.sep)[0];
  const isAllowed =
    allowedFiles.has(relativePath) || allowedDirectories.has(topLevel);

  return isAllowed ? filePath : null;
}

function send(res, statusCode, body, headers = {}) {
  res.writeHead(statusCode, {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "Referrer-Policy": "no-referrer",
    ...headers
  });
  res.end(body);
}

const server = http.createServer((req, res) => {
  if (!req.url || (req.method !== "GET" && req.method !== "HEAD")) {
    send(res, 405, "Method not allowed", { Allow: "GET, HEAD" });
    return;
  }

  const filePath = resolveRequestPath(req.url);

  if (!filePath) {
    send(res, 403, "Forbidden");
    return;
  }

  fs.stat(filePath, (statError, stats) => {
    if (statError || !stats.isFile()) {
      send(res, 404, "Not found");
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const headers = {
      "Content-Length": stats.size,
      "Content-Type": contentTypes[ext] || "application/octet-stream"
    };

    res.writeHead(200, {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "SAMEORIGIN",
      "Referrer-Policy": "no-referrer",
      ...headers
    });

    if (req.method === "HEAD") {
      res.end();
      return;
    }

    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(port, host, () => {
  console.log(`Orange Circle web server running at http://${host}:${port}/`);
});
