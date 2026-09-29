"""Step 5: sync the figure deck and the figure indices with the five-seed Figure S8.

Only new files are produced: the 2026-09-27 deck and the two index files under
`docs/paper_complete_review_20260920/` stay untouched.

Two slides (30 and 31) carry Figure S8 as a single full-slide image.  The 2026-09-27 deck
embeds the two archived PNG pages byte-for-byte (`ppt/media/image31.png`,
`ppt/media/image32.png`), and the new five-seed pages keep the same canvas size, so the sync
is a byte swap of those two parts plus the caption/notes text, not a re-layout:

    ppt/media/image31.png / image32.png   <- the new five-seed pages
    ppt/notesSlides/notesSlide30/31.xml   <- new caption, image path and source pointer

Usage:
    python scripts/five_seed_support_variance_20260928/step5_paper_revision.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import fsv_common as P  # noqa: E402

SOURCE_DECK = P.ROOT / "docs/FINAL_SUBMISSION_20260926/All_Figures_Complete_20260927.pptx"
REVISION_DIR = P.ROOT / "docs/paper_revision_five_seed_20260928"
OUT_DECK = REVISION_DIR / "All_Figures_Complete_20260929.pptx"
REVISION_CONFIG = P.ROOT / "scripts/paper_revision_five_seed_20260928/figures.json"
FROZEN_INDEX_JSON = P.ROOT / "docs/paper_complete_review_20260920/FIGURE_SLIDE_INDEX.json"
FROZEN_INDEX_MD = P.ROOT / "docs/paper_complete_review_20260920/图件与PPT页码索引.md"
ARCHIVED_FIGS = [P.ROOT / "docs/paper_complete_review_20260920/figures"
                 / f"figS8_support_seed_part{i}.png" for i in (1, 2)]
NEW_FIGS = [P.ROOT / "docs/five_seed_support_variance_20260928/figures"
            / f"figS8_five_seed_part{i}.png" for i in (1, 2)]
SLIDES = (30, 31)


def sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def replace_run(xml: str, index: int, value: str) -> str:
    """Replace the text of the index-th ``<a:t>`` run (the notes use one run per line)."""
    pattern = re.compile(r"(<a:t>)(.*?)(</a:t>)", re.S)

    def sub(match):
        sub.count += 1
        if sub.count - 1 == index:
            return match.group(1) + value + match.group(3)
        return match.group(0)

    sub.count = 0
    out = pattern.sub(sub, xml)
    if sub.count <= index:
        raise SystemExit(f"notes slide has only {sub.count} text runs; expected > {index}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    if not SOURCE_DECK.exists():
        raise SystemExit(f"deck missing: {SOURCE_DECK}")
    for path in ARCHIVED_FIGS + NEW_FIGS + [REVISION_CONFIG, FROZEN_INDEX_JSON,
                                            FROZEN_INDEX_MD]:
        if not path.exists():
            raise SystemExit(f"input missing: {path}")
    config = json.loads(REVISION_CONFIG.read_text(encoding="utf-8"))
    s8 = config["support_seed_sensitivity"]
    captions = [s8["caption"], s8.get("continuation_caption", s8["caption"])]
    new_images = [path.read_bytes() for path in NEW_FIGS]
    archived_hashes = {sha256_bytes(path.read_bytes()): i for i, path in enumerate(ARCHIVED_FIGS)}

    report: dict = {"kind": "five_seed_step5_deck_sync", "created_utc": P.utcnow(),
                    "source_deck": str(SOURCE_DECK.relative_to(P.ROOT)),
                    "output_deck": str(OUT_DECK.relative_to(P.ROOT)), "checks": {}}

    with zipfile.ZipFile(SOURCE_DECK) as zin:
        members = {name: zin.read(name) for name in zin.namelist()}

    swapped = []
    for name, data in members.items():
        if not name.startswith("ppt/media/"):
            continue
        index = archived_hashes.get(sha256_bytes(data))
        if index is None:
            continue
        members[name] = new_images[index]
        swapped.append({"part": name, "figure_part": index + 1,
                        "archived_sha256": sha256_bytes(data),
                        "new_sha256": sha256_bytes(new_images[index]),
                        "bytes": len(new_images[index])})
    if len(swapped) != 2:
        raise SystemExit(f"expected 2 archived Figure S8 media parts, found {len(swapped)}")
    report["media_parts_swapped"] = swapped

    notes_updated = []
    for slide in SLIDES:
        name = f"ppt/notesSlides/notesSlide{slide}.xml"
        xml = members[name].decode("utf-8")
        if f"Figure S8; part {slide - 29}" not in xml:
            raise SystemExit(f"{name}: unexpected notes content")
        part_index = slide - 30
        xml = replace_run(xml, 1, captions[part_index])
        xml = replace_run(xml, 2, "Image: " + str(NEW_FIGS[part_index]).replace("\\", "/"))
        xml = replace_run(xml, 3, "Reproducible sources: "
                                  "scripts/five_seed_support_variance_20260928/ "
                                  "(table, figure, audit) and "
                                  "scripts/paper_revision_five_seed_20260928/ "
                                  "(manuscript build)")
        members[name] = xml.encode("utf-8")
        notes_updated.append({"slide": slide, "notes": name,
                              "caption_sha256": sha256_bytes(captions[part_index].encode())})

    slides = [n for n in members if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
    report["slides"] = len(slides)
    if len(slides) != 67:
        raise SystemExit(f"deck has {len(slides)} slides, expected 67")
    report["checks"]["slide_count_unchanged"] = True

    if not args.check_only:
        REVISION_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(OUT_DECK, "w", compression=zipfile.ZIP_DEFLATED,
                            compresslevel=6) as zout:
            for name in sorted(members):
                info = zipfile.ZipInfo(name, date_time=(2026, 9, 29, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                zout.writestr(info, members[name])

        with zipfile.ZipFile(OUT_DECK) as zout:
            verify = {n: sha256_bytes(zout.read(n)) for n in
                      ("ppt/media/image31.png", "ppt/media/image32.png")}
        report["checks"]["media_replaced"] = all(
            verify[f"ppt/media/image{31 + i}.png"] == sha256_bytes(new_images[i])
            for i in range(2))
        report["notes_updated"] = notes_updated
        report["output_bytes"] = OUT_DECK.stat().st_size

        # figure/slide indices for the revision (the frozen copies are not touched)
        index = json.loads(FROZEN_INDEX_JSON.read_text(encoding="utf-8"))
        for entry in index:
            if str(entry.get("figure")) == "S8":
                part = int(entry.get("part", 1))
                entry["image"] = str(NEW_FIGS[part - 1].relative_to(P.ROOT)).replace("\\", "/")
                entry["caption"] = captions[part - 1]
        (REVISION_DIR / "FIGURE_SLIDE_INDEX.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
        md = FROZEN_INDEX_MD.read_text(encoding="utf-8")
        for part in (1, 2):
            md = md.replace(f"figS8_support_seed_part{part}.png",
                            f"figS8_five_seed_part{part}.png")
        md = md.replace("# 图件与 PPT 页码索引\n\n现役文件：All_Figures_Complete_20260925.pptx。",
                        "# 图件与 PPT 页码索引（五种子修订版）\n\n"
                        "现役文件：All_Figures_Complete_20260929.pptx（本次修订）；"
                        "All_Figures_Complete_20260925/20260927 为历史版本。")
        (REVISION_DIR / "图件与PPT页码索引.md").write_text(md, encoding="utf-8")
        report["indices_written"] = [str((REVISION_DIR / "FIGURE_SLIDE_INDEX.json")
                                         .relative_to(P.ROOT)),
                                     str((REVISION_DIR / "图件与PPT页码索引.md")
                                         .relative_to(P.ROOT))]
        report["checks"]["indices_s8_rows_updated"] = sum(
            1 for entry in index if str(entry.get("figure")) == "S8"
            and "five_seed" in str(entry.get("image"))) == 2

    report["all_pass"] = all(report["checks"].values())
    P.write_json(REVISION_DIR / "step5_deck_sync.json", report)
    print(json.dumps({k: report[k] for k in
                      ("slides", "checks", "output_bytes") if k in report},
                     ensure_ascii=False, indent=1))
    for item in report["media_parts_swapped"]:
        print(f"  swapped {item['part']} (S8 part {item['figure_part']}) "
              f"{item['bytes']} bytes")
    print(f"deck: {OUT_DECK if not args.check_only else '(check only)'}")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
