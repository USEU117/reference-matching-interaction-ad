from pathlib import Path
import json
import zipfile
from lxml import etree

ROOT = Path(__file__).resolve().parents[3] / ".tmp_complete_figures_20260920/methods"
SOURCE = ROOT / "candidate.pptx"
TARGET = ROOT / "methods.pptx"
NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

baselines = json.loads((ROOT / "math_baselines.json").read_text(encoding="utf-8"))
with zipfile.ZipFile(SOURCE) as archive:
    parts = {name: archive.read(name) for name in archive.namelist()}

patched = 0
for item in baselines:
    slide_path = f"ppt/slides/slide{item['slide']}.xml"
    root = etree.fromstring(parts[slide_path])
    named_shapes = {
        shape.find("p:nvSpPr/p:cNvPr", NS).get("name"): shape
        for shape in root.findall(".//p:sp", NS)
    }
    shape = named_shapes[item["shape"]]
    runs = shape.findall("p:txBody/a:p/a:r", NS)
    run = runs[item["run"]]
    properties = run.find("a:rPr", NS)
    if properties is None:
        properties = etree.SubElement(run, f"{{{NS['a']}}}rPr")
    properties.set("baseline", str(item["base"]))
    parts[slide_path] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    patched += 1

with zipfile.ZipFile(TARGET, "w", zipfile.ZIP_DEFLATED) as archive:
    for name, data in parts.items():
        archive.writestr(name, data)

print(f"Patched {patched} native subscript runs into {TARGET}")
