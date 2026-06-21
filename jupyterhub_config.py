import os

c = get_config()  # noqa: F821 (provided by JupyterHub)

# --- Auth: DummyAuthenticator for local/dev — any username + the shared password
# below; no signup. Swap to NativeAuthenticator or OAuth (GitHub/Google) for a team.
c.JupyterHub.authenticator_class = "dummy"
c.Authenticator.admin_users = {os.environ.get("JUPYTERHUB_ADMIN", "admin")}
c.DummyAuthenticator.password = os.environ.get("JUPYTERHUB_PASSWORD", "atlas")

# --- Spawner: one notebook container per user from the single-user image.
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.DockerSpawner.image = os.environ.get("SINGLEUSER_IMAGE", "integer-atlas-singleuser")
c.DockerSpawner.network_name = os.environ.get("DOCKER_NETWORK_NAME", "ui_default")
c.DockerSpawner.remove = True
c.DockerSpawner.notebook_dir = "/home/jovyan/work"

# Hub must be reachable from spawned containers by its service name on the network.
c.JupyterHub.hub_connect_ip = os.environ.get("HUB_CONNECT_IP", "hub")
c.JupyterHub.bind_url = "http://:8000"

# --- Data: mount the CLI workspace READ-ONLY at the SAME absolute path, so the
# absolute parquet paths inside atlas.duckdb's `numbers` view resolve in-container.
ws = os.environ.get("INTEGER_ATLAS_HOME", "/data/integer-atlas")
c.DockerSpawner.read_only_volumes = {ws: ws}
c.DockerSpawner.environment = {"INTEGER_ATLAS_HOME": ws}

# Optional: bind-mount local notebooks for live editing (set NOTEBOOKS_DIR to an
# absolute host path). Unset → use the notebooks baked into the single-user image.
_nb = os.environ.get("NOTEBOOKS_DIR")
if _nb:
    c.DockerSpawner.volumes = {_nb: "/home/jovyan/work"}

# --- Hub state (kept in the hub-data volume).
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"