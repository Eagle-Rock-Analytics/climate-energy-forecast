"""Run the Lumen pipeline notebooks in order.

Settings are read from the CONTROLS file at the repo root: boolean bypass switches as
KEY=0/1 (e.g. LOCALIZE, DETREND), and other settings as KEY=value (e.g. STATION=BAKERSFIELD).
Notebooks import CONTROLS from this module, so they honor the same settings whether run here
or directly.

    python updated_nbs/run_pipeline.py
"""
import os
from pathlib import Path

NB_DIR = os.path.dirname(os.path.abspath(__file__))
CONTROLS_PATH = Path(NB_DIR).parent / "CONTROLS"
PIPELINE = [
    "retrieve_and_localize.ipynb",
    "detrending.ipynb",
    "final_data_manipulation.ipynb",
]


def load_controls(path=CONTROLS_PATH):
    controls = {}
    for raw in Path(path).read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise ValueError(f"malformed line in {path}: {raw!r}")
        key = key.strip()
        value = value.strip()
        if not value:
            raise ValueError(f"{key} has no value in {path}")
        # 0/1 settings are bypass switches and become bool; anything else (e.g. STATION
        # names) is kept as its raw string value.
        controls[key] = bool(int(value)) if value in ("0", "1") else value
    return controls


CONTROLS = load_controls()


def control_tag(controls=CONTROLS):
    parts = (f"{key}{int(value) if isinstance(value, bool) else value}" for key, value in controls.items())
    return "_" + "_".join(parts)


def run_notebook(name):
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(os.path.join(NB_DIR, name), as_version=4)
    client = NotebookClient(
        nb,
        timeout=None,
        kernel_name="python3",
        resources={"metadata": {"path": NB_DIR}},
    )
    print(f"running {name}", flush=True)
    client.execute()


if __name__ == "__main__":
    print("controls:", CONTROLS, flush=True)
    for notebook in PIPELINE:
        run_notebook(notebook)
