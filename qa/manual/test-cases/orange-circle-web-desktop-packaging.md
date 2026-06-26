# Orange Circle Web And Desktop Packaging

## Evidence

- Source game: `orange_circle_platformer.html`
- Web host: `server.js`
- Desktop shell: `electron/main.cjs`
- Package scripts: `package.json`
- ZKME artifacts: `.zkme/kme_output/SYSTEM_OVERVIEW.md`, `.zkme/kme_output/ZKME_CHANGE_IMPACT.json`, `.zkme/kme_output/ZKME_CONTRACTS_INVARIANTS.json`

## Scope

Validate that Orange Circle remains playable as a browser page and can launch as a desktop Electron app without changing gameplay.

## Preconditions

- Node.js is installed.
- Dependencies have been installed with `npm install`.

## Manual Test Steps

1. Run `npm run web`.
2. Open `http://127.0.0.1:5177/`.
3. Verify the main menu displays `ORANGE CIRCLE`.
4. Select `NEW GAME`.
5. Verify the canvas appears and keyboard/mouse controls still operate.
6. Stop the web server.
7. Run `npm run desktop`.
8. Verify the desktop window opens with the same main menu.
9. Select `LEVEL CREATOR`.
10. Verify the level editor toolbar appears and the app can return to the main menu.
11. Run `docker compose up --build`.
12. Open `http://127.0.0.1:8080/`.
13. Verify the same browser game loads from the container.

## Negative And Boundary Checks

- Request an unknown path such as `/missing.html` and verify a `404` response.
- Request a traversal-like path such as `/../README.md` and verify protected files are not served.
- Resize the browser or Electron window and verify the canvas remains visible.

## Cleanup

- Stop local Node, Electron, and Docker processes.
- Remove local build artifacts only if no longer needed.

## Expected Artifacts

- Passing `npm test` output.
- Optional screenshot of the web main menu.
- Optional screenshot of the Electron main menu.
