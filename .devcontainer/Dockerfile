FROM mcr.microsoft.com/devcontainers/typescript-node:22

# Fetch Debian packages over HTTPS. Docker sandboxes block plain HTTP (port 80) by default; HTTPS works everywhere.
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources
