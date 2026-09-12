"""Fetch the UniVAD assets with Python's OpenSSL TLS stack (schannel/curl fails through the proxy).

Known-good configuration on this machine (see project memory): the local proxy at
127.0.0.1:7897 only completes a handshake when TLS is capped at 1.2 and the client uses
OpenSSL rather than Windows schannel. Python's ssl module is OpenSSL, so this works where
curl.exe (schannel) fails with 'schannel: failed to receive handshake'.

Resumable: partial files are kept as <name>.part and resumed with a Range request.
"""
from __future__ import annotations

import os
import ssl
import sys
import time
import urllib.request
from pathlib import Path

PROJ = Path(r"D:\STUDY\My_github\sci_project")
CKPT = PROJ / "methods" / "univad_official" / "pretrained_ckpts"
HUB = Path(os.environ["USERPROFILE"]) / ".cache" / "torch" / "hub" / "checkpoints"
PROXY = "http://127.0.0.1:7897"

ASSETS = [
    ("dino_deitsmall8_300ep_pretrain.pth", HUB,
     "https://dl.fbaipublicfiles.com/dino/dino_deitsmall8_300ep_pretrain/dino_deitsmall8_300ep_pretrain.pth"),
    ("groundingdino_swint_ogc.pth", CKPT,
     "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"),
    ("sam_hq_vit_h.pth", CKPT,
     "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_h.pth"),
    ("dinov2_vitg14_pretrain.pth", HUB,
     "https://dl.fbaipublicfiles.com/dinov2/dinov2_vitg14/dinov2_vitg14_pretrain.pth"),
]


def make_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE          # proxy re-signs; mirrors the known-good git -c http.sslVerify settings
    if hasattr(ctx, "maximum_version"):
        ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    return ctx


def fetch(name: str, dest_dir: Path, url: str, attempts: int = 15) -> bool:
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / name
    if out.exists() and out.stat().st_size > 0:
        print(f"[skip] {out} ({out.stat().st_size:,} bytes)", flush=True)
        return True
    part = dest_dir / (name + ".part")
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}),
        urllib.request.HTTPSHandler(context=make_ctx()),
    )
    for attempt in range(1, attempts + 1):
        have = part.stat().st_size if part.exists() else 0
        # Always send a Range header: a short-lived 206 stream survives this proxy far
        # better than a 200 with a multi-GB Content-Length, and it makes resume trivial.
        req = urllib.request.Request(url)
        req.add_header("Range", f"bytes={have}-")
        try:
            with opener.open(req, timeout=60) as resp:
                total = resp.headers.get("Content-Length")
                total = (int(total) + have) if total and resp.status == 206 else (
                    int(total) if total else None)
                print(f"[{attempt}] {name}: resuming from {have:,} / {total:,}"
                      if total else f"[{attempt}] {name}: start", flush=True)
                mode = "ab" if resp.status == 206 else "wb"
                if mode == "wb":
                    have = 0
                done = have
                t0 = time.time()
                with part.open(mode) as fh:
                    while True:
                        chunk = resp.read(1 << 20)
                        if not chunk:
                            break
                        fh.write(chunk)
                        done += len(chunk)
                        if total and done % (64 << 20) < (1 << 20):
                            pct = 100.0 * done / total
                            rate = done / max(time.time() - t0, 1e-6) / 1e6
                            print(f"    {pct:5.1f}%  {done/1e6:8.1f}/{total/1e6:.1f} MB  {rate:5.2f} MB/s",
                                  flush=True)
            if total is None or part.stat().st_size >= total:
                part.replace(out)
                print(f"[ok] {out} {out.stat().st_size:,} bytes", flush=True)
                return True
            print(f"[short] {part.stat().st_size:,} of {total:,}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[fail {attempt}] {name}: {type(exc).__name__}: {exc}", flush=True)
        time.sleep(4)
    print(f"[GIVEUP] {name}", flush=True)
    return False


if __name__ == "__main__":
    want = sys.argv[1:] or [a[0] for a in ASSETS]
    results = {}
    for name, dest, url in ASSETS:
        if name not in want:
            continue
        results[name] = fetch(name, dest, url)
    print("=== summary ===", flush=True)
    for k, v in results.items():
        print(f"{'OK  ' if v else 'FAIL'} {k}", flush=True)
