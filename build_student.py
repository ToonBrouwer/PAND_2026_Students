# %% Build PAND student version from the 2026 instructor repo
import json, re, shutil
from pathlib import Path

SRC = Path("/home/claude/src2026/PAND_2026-main")
DST = Path("/home/claude/out/PAND_Students")

def excluded(rel: Path) -> bool:
    name = rel.name.lower()
    if any(p in (".ipynb_checkpoints", "__pycache__", ".git") for p in rel.parts):
        return True
    return ("answer" in name or "solution" in name) and name.endswith(".ipynb")

if DST.exists():
    shutil.rmtree(DST)
for f in SRC.rglob("*"):
    rel = f.relative_to(SRC)
    if f.is_file() and not excluded(rel):
        (DST / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, DST / rel)

# %% Helpers
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def save(p, nb): p.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
def src(c): return "".join(c["source"])
def set_src(c, s): c["source"] = s.splitlines(keepends=True)
def clear(c):
    if c["cell_type"] == "code":
        c["outputs"], c["execution_count"] = [], None

# %% Spike notebook: blank the worked solutions
p = DST / "Spike_Analysis/SpikeNotebookNew.ipynb"
nb = load(p); cells = nb["cells"]
for c in cells: clear(c)
set_src(cells[4], "Answer: \n")
set_src(cells[6], "# Your code here\n")
set_src(cells[8], "# Your code here: design and apply a band-pass filter (300-5000 Hz)\n")
set_src(cells[10], "# Your code here: compute thresholds (mean +/- k*SD) and plot them on the filtered signal\n")
set_src(cells[12], "# Optional: try spike detection and waveform clustering yourself here\n")
set_src(cells[17], "# Your code here: build the neurons x timepoints x trials matrix (window -0.5 to 0.5 s)\n"
                   "window_start = -0.5   # seconds before stimulus\nwindow_end   =  0.5   # seconds after stimulus\n")
set_src(cells[19], "# Your code here: raster plot for one neuron\n")
set_src(cells[21], "# Your code here: PSTH (10 ms bins)\n")
set_src(cells[23], "# Your code here: pre- vs post-stimulus firing rates and t-test per neuron\n")
assert "spike_data.npy" in src(cells[13])
del cells[13]   # instructor cell that writes the spike_data files (they're provided)
save(p, nb)

# %% Imaging notebook: remove filled-in answer, written answer and all outputs
p = DST / "Imaging_notebook/CaseStudy_Imaging_Updated.ipynb"
nb = load(p); cells = nb["cells"]
for c in cells: clear(c)
assert "left_ios" in src(cells[12])
set_src(cells[12], src(cells[12]).replace("np.mean(ios['left'], axis=2)", "0")
        .replace("left_ios = 0\n", "left_ios = 0\ncentre_ios = 0\nright_ios = 0\n"))
assert src(cells[24]).startswith("80 indicates")
set_src(cells[24], "*Your answer here*\n")
save(p, nb)

# %% All other notebooks: clear outputs of empty / to-do code cells (an output there can only come from a solution)
TODO = re.compile(r"your code|implement the todo|notimplementederror|complete th", re.I)
for p in DST.rglob("*.ipynb"):
    nb = load(p); changed = False
    for c in nb["cells"]:
        if c["cell_type"] == "code" and c.get("outputs") and (not src(c).strip() or TODO.search(src(c))):
            clear(c); changed = True
    if changed:
        save(p, nb); print("cleared to-do outputs in", p.relative_to(DST))

# %% Ignore checkpoints at any depth (the old pattern only matched one folder deep)
(DST / ".gitignore").write_text(".ipynb_checkpoints/\n__pycache__/\n")

# %% Leak check
hits = []
for p in DST.rglob("*"):
    if p.is_file() and re.search(r"answer|solution|checkpoint|__pycache__", p.name, re.I):
        hits.append(str(p.relative_to(DST)))
print("Suspicious file names:", hits or "none")
