# Simple Context Coach

A minimal [OpenAI App SDK](https://platform.openai.com/docs/apps) project that
shows how to power a ChatGPT App with your **own MCP server** instead of the
OpenAI API. Everything runs on your infrastructure, so end-users never need your
OpenAI API key.

## What is included?

- `app/mcp_server.py` – a FastAPI server that exposes two MCP-style tools
  (`project_notes` and `roadmap_status`) backed by a local knowledge base.
- `app/app_definition.py` – the App manifest that tells ChatGPT how to call your
  server. The manifest is generated via the CLI and is used when *you*, the App
  owner, register the experience inside ChatGPT.
- `app/cli.py` – Typer commands for running the server, generating the manifest,
  and printing the environment variables required for CI/CD.
- `.github/workflows/deploy.yml` – a GitHub Actions workflow that builds the
  manifest and uploads it as an artifact.

The flow mirrors how you would run a "bring-your-own-MCP" App: deploy your
server wherever you like, describe it with the App SDK, and share the manifest
with ChatGPT users.

## Prerequisites

- Python 3.11+
- (Optional) a public URL or tunnel for your MCP server so ChatGPT can reach it
- Access to the [ChatGPT Apps UI](https://chat.openai.com/)

## Local setup

1. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e .
   ```

2. **Configure the server settings**

   ```bash
   cp .env.example .env
   # tweak APP_HOST/APP_PORT for the local server and APP_PUBLIC_URL for the
   # URL that ChatGPT should call (e.g., your tunnel or production hostname)
   ```

3. **Boot the MCP server**

   ```bash
   appsdk run-server
   ```

   The server exposes:

   - `GET /health` for readiness probes
   - `GET /mcp/tools` to list available tools
   - `POST /mcp/tools/invoke` to run a tool (`project_notes` or `roadmap_status`)

   Because the server only reads local data, no OpenAI API key is required.

## Generating the App manifest

Use the CLI to materialize the manifest that ChatGPT will ingest during the
**developer registration** step:

```bash
appsdk generate-manifest --output build/app.json
```

The resulting file contains:

- App metadata and instructions
- Tool schemas for `project_notes` and `roadmap_status`
- The MCP server descriptor that points to `APP_PUBLIC_URL`

Upload `build/app.json` via **ChatGPT → Apps → Import** under your developer
account. This single import registers the App with ChatGPT so you can test it
and, later, share it with end-users. ChatGPT will connect to your MCP server and
start calling the tools while you chat with the App.

## Deploying with GitHub Actions

The workflow defined in [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)
performs the following on every push to `main`:

1. checks out the repository and installs dependencies,
2. runs a lightweight smoke test (`python -m compileall app`), and
3. executes `scripts/deploy.sh` to generate `build/app.json`.

Finally, the manifest is uploaded as an artifact called `app-manifest`. Download
it from the workflow run and import it into ChatGPT just like the local build.
No repository secrets are required because the project never touches the OpenAI
API.

## Manual deployment checklist

1. Run `appsdk env` to verify the CLI is reading your `.env` values.
2. Start the server in your hosting environment (`appsdk run-server`).
3. Generate a manifest (`appsdk generate-manifest`) that references the public
   URL of that deployment.
4. Import `build/app.json` into ChatGPT **once** under the developer account to
   register the App and obtain a share link for testers.

### Example: deploying to `openaiapp.blockchain.nz`

If you want to host the MCP server at `https://openaiapp.blockchain.nz`, follow
this concrete checklist:

1. **Point DNS at your server.** Create an `A` or `CNAME` record for
   `openaiapp.blockchain.nz` that resolves to the machine that will run the
   FastAPI process.
2. **Set the environment variables.** Your production `.env` should include:

   ```bash
   APP_HOST=0.0.0.0
   APP_PORT=8000
   APP_PUBLIC_URL=https://openaiapp.blockchain.nz
   ```

   The `APP_PUBLIC_URL` value is what lands in the manifest so ChatGPT knows
   where to send MCP calls.
3. **Run the server under a process manager.** On the host, install the
   dependencies (`pip install -e .`) and start the service with either the Typer
   command or a uvicorn invocation:

   ```bash
   # Typer helper
   appsdk run-server

   # or explicit uvicorn command
   uvicorn app.mcp_server:app --host 0.0.0.0 --port 8000
   ```

   Use systemd, supervisord, or another daemon manager so the process stays
   running.
4. **Expose HTTPS.** Terminate TLS with your proxy of choice (Caddy, nginx,
   Cloudflare Tunnel, etc.) and forward traffic to `127.0.0.1:8000` so the
   public hostname serves the FastAPI endpoints.
5. **Generate the manifest for registration.** From a workstation, run
   `appsdk generate-manifest --output build/app.json`. Confirm that the `server`
   entry inside the JSON points to `https://openaiapp.blockchain.nz` before
   uploading it to ChatGPT under your developer account. After the import,
   capture the share link so end-users can add the App without handling JSON.

With those steps complete, any ChatGPT session that imports your manifest will
call the MCP server hosted at `openaiapp.blockchain.nz`.

## Registering and sharing the App

Only the developer needs to interact with the manifest file. The lifecycle is:

1. **Generate `build/app.json`.** Run `appsdk generate-manifest --output
   build/app.json` so the App SDK can describe your MCP server.
2. **Register the App once.** In ChatGPT, go to **Apps → Import** and upload the
   manifest under your developer account. This step creates the App entry inside
   ChatGPT and gives you the normal App management UI (rename, edit, delete,
   etc.).
3. **Share the App link.** In the Apps list, click the three-dot menu next to
   your new App and choose **Share**. Copy the generated link.
4. **End-users add the App from the link.** Anyone with access to ChatGPT Apps
   simply opens the link. ChatGPT walks them through adding the App to their
   account—no manifest upload required on their end.

### Can end-users discover it another way?

Right now, the App SDK does **not** expose a public directory or domain-based
lookup for third-party Apps. ChatGPT users either:

- open the share link you generated in step 3 above, or
- accept an invitation if OpenAI grants you access to an experimental App
  distribution program.

They cannot install the App just by knowing your server hostname
(`https://openaiapp.blockchain.nz`) or by browsing a registry. If OpenAI adds a
directory/registry flow in the future, you would still register the App with
your manifest first, then opt into whatever distribution channel they provide.

Because the MCP server never asks for an OpenAI API key, there are no secrets to
share—end-users only need the App link and network access to
`https://openaiapp.blockchain.nz`.

## Extending the server

`app/mcp_server.py` keeps the example intentionally small, but you can:

- replace the in-memory dictionaries with calls to databases or third-party APIs,
- add new endpoints under `/mcp/tools/...` for every capability you want to
  expose, and
- update the manifest to describe each new tool.

This approach lets you keep sensitive integrations on your infrastructure while
ChatGPT users enjoy a native App experience.
