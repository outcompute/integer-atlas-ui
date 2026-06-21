# Single-user notebook image: Jupyter + DuckDB + plotting + the atlas helper.
FROM quay.io/jupyter/scipy-notebook:latest

RUN pip install --no-cache-dir duckdb plotly pyarrow voila

# The atlas helper (import atlas) and the starter notebooks.
COPY --chown=${NB_UID}:${NB_GID} lib /opt/atlas/lib
COPY --chown=${NB_UID}:${NB_GID} notebooks /home/jovyan/work
ENV PYTHONPATH=/opt/atlas/lib

# 3D meshes/volumes: add pyvista + the headless VTK stack if you need them
# (heavier image): RUN pip install --no-cache-dir pyvista trame ipywidgets
