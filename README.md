# Orange Circle

Orange Circle Platformer packaged for browser play, Docker hosting, and an installable Electron desktop app.

## Run On This Computer

Install dependencies once:

```bash
npm install
```

Start the web version:

```bash
npm run web
```

Then open:

```text
http://127.0.0.1:5177/
```

## Desktop App

Run the Electron app in development:

```bash
npm run desktop
```

Build an installable desktop package:

```bash
npm run dist
```

Build output is written to `dist/`.

## Docker Web App

Build and run the web version in Docker:

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8080/
```

## Access From A Webpage Outside The Home Network

The app is now ready to be hosted as a normal web page. Safer options:

1. Deploy the Docker image to a VPS or app host.
2. Use a Cloudflare Tunnel to expose the Docker container without router port forwarding.
3. Use router port forwarding only if you understand the network exposure and have firewall rules in place.

For a public container, the app listens on `HOST=0.0.0.0` and `PORT=8080`.

## Checks

```bash
npm run check
npm test
```
