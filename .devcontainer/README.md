# Dev container

Node 22 + the project's tooling, matching CI. Two ways to use it.

## On the host (plain Docker)

Open the repo in VS Code and run **Dev Containers: Reopen in Container**.

## Inside a Docker sandbox, from host VS Code

The container runs on the sandbox's Docker daemon and exposes SSH on port 2222; host VS Code connects with the
**Remote - SSH** extension.

1. Put your host's SSH public key in `.devcontainer/authorized_keys` (gitignored). In direct mode the repo is
   shared with the host, so copy it there from the host, e.g. `~/.ssh/id_ed25519.pub`.
2. In the sandbox, from the repo root: `.devcontainer/up.sh`. Rerun it after a sandbox restart. The first build
   takes a few minutes.
3. On the host, publish the port: `sbx ports <sandbox-name> --publish 2222:2222` (the sandbox name is
   `$SANDBOX_NAME` inside the sandbox).
4. Add to the host's `~/.ssh/config`:

   ```text
   Host gol2-dev
     HostName localhost
     Port 2222
     User node
     IdentityFile ~/.ssh/id_ed25519
   ```

5. In VS Code: **Remote-SSH: Connect to Host… → gol2-dev**, then open `/workspaces/gol2`.

VS Code forwards ports (e.g. Vite on 5173) over the SSH connection, so `npm run dev` needs no extra `sbx ports`.

### Sandbox prerequisites

Nested containers don't inherit the sandbox proxy. `~/.docker/config.json` in the sandbox needs:

```json
{
  "proxies": {
    "default": {
      "httpProxy": "http://gateway.docker.internal:3128",
      "httpsProxy": "http://gateway.docker.internal:3128",
      "noProxy": "localhost,127.0.0.1,::1"
    }
  }
}
```

The sandbox blocks plain HTTP, so the `Dockerfile` switches apt to HTTPS mirrors.
