const { spawn } = require("node:child_process");
const { once } = require("node:events");
const { test } = require("node:test");
const assert = require("node:assert/strict");

test("web server serves the Orange Circle game", async () => {
  const port = "5188";
  const server = spawn(process.execPath, ["server.js"], {
    env: {
      ...process.env,
      HOST: "127.0.0.1",
      PORT: port
    },
    stdio: ["ignore", "pipe", "pipe"]
  });

  try {
    await once(server.stdout, "data");
    const response = await fetch(`http://127.0.0.1:${port}/`);
    const html = await response.text();

    assert.equal(response.status, 200);
    assert.match(response.headers.get("content-type") || "", /text\/html/);
    assert.match(html, /Orange Circle Platformer/);
    assert.match(html, /gameCanvas/);
  } finally {
    server.kill();
    await once(server, "exit");
  }
});
