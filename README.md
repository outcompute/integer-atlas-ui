# Integer Atlas — UI

The optional hosted layer for exploring the dataset, **assembled from existing
open-source tools**. It runs **JupyterHub**: notebooks, 2D **and 3D** plots (Plotly;
pyvista optional), notebook-as-dashboard publishing (Voilà), and team auth — one service.
See "Extending" below to add a BI tool (Superset/Metabase) for point-and-click dashboards.

## What's here

```
docker-compose.yml        the hub service (+ a build-only single-user image)
jupyterhub_config.py      DockerSpawner + simple multi-user auth + the read-only data mount
images/hub/Dockerfile     JupyterHub + dockerspawner + nativeauthenticator
images/singleuser/        Jupyter + duckdb + plotly + voila + the atlas helper
lib/atlas.py              connect() → a DuckDB connection over the CLI's data
notebooks/explore.ipynb   starter: 2D Ω(n) histogram + 3D popcount-vs-Ω(n)
.env.example              INTEGER_ATLAS_HOME + admin user
```

## How it reads the data (the important bit)

The UI reads the **same on-disk dataset the CLI populated**, read-only. `lib/atlas.py`
opens the CLI's `atlas.duckdb` in read-only mode and reuses its `numbers` view (same
column-group shards unioned across ranges, different groups FULL-joined on `n`); if that
DB or its paths aren't available, it falls back to a view over the parquet shards.

Two consequences, both handled by the config:
- **Same host / mounted workspace.** The notebook container mounts the CLI workspace
  read-only. (Remote UI? run `integer-atlas fetch` on that host, or share the volume.)
- **Same absolute path.** `atlas.duckdb`'s view references parquet by absolute path, so the
  workspace is mounted at the **same path** inside the container. Set `INTEGER_ATLAS_HOME`
  to one absolute path and use it for **both** the CLI and the UI.
- **No write contention.** DuckDB is single-writer across processes; the UI only ever opens
  read-only, so it never fights the CLI's `fetch`.

## Run it

```
cd ui
cp .env.example .env                      # set INTEGER_ATLAS_HOME to an absolute path
# populate data with the CLI using that same path:
INTEGER_ATLAS_HOME=$(grep INTEGER_ATLAS_HOME .env | cut -d= -f2) \
  integer-atlas fetch --start 1 --end 1000000 --columns omega_big,binary_popcount,is_prime

docker compose --profile build build      # build hub + single-user images
docker compose up -d                      # start the hub
# open http://localhost:8000, sign up as the admin user, then open notebooks/explore.ipynb
```

## Auth

The default is `DummyAuthenticator` — any username plus the shared `JUPYTERHUB_PASSWORD`,
with `JUPYTERHUB_ADMIN` as admin — which is convenient for local use. For a team, switch
to `NativeAuthenticator` (self-signup) or OAuth (GitHub/Google) in `jupyterhub_config.py`.

## Extending

Add a BI service (Metabase is light; Superset is richer but drags Postgres + Redis) for
point-and-click dashboards, and put everything behind a reverse proxy + `oauth2-proxy`
for single team sign-on. Both consume the same read-only DuckDB/parquet.

## License

MIT — see [LICENSE](LICENSE).
