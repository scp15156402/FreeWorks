#!/usr/bin/env python3
"""Compare what FreeWorks pins (versions.json) with the newest upstream versions.

    python3 dev/check_updates.py            # report
    python3 dev/check_updates.py --json     # machine-readable report
    python3 dev/check_updates.py --apply    # write newer pins into versions.json
                                            # (FreeCAD only if all Windows/Linux assets exist)

Stdlib only. Uses `git ls-remote` (no GitHub API rate limits) and HTTP HEAD requests on
release asset URLs. SHA-256 digests come from the GitHub API when it is reachable.
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MANIFEST = os.path.join(ROOT, "versions.json")
UA = {"User-Agent": "FreeWorks-check-updates"}


def ls_remote(repo, pattern=None):
    args = ["git", "ls-remote", "https://github.com/%s.git" % repo]
    if pattern:
        args.append(pattern)
    out = subprocess.run(args, capture_output=True, text=True, timeout=90)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "git ls-remote failed")
    refs = {}
    for line in out.stdout.splitlines():
        sha, ref = line.split("\t")
        refs[ref] = sha
    return refs


def vkey(v):
    return tuple(int(x) for x in v.split("."))


def latest_freecad():
    """Highest plain numeric release tag (1.1.4, 26.3.0 …); skips rc/dev/weekly tags."""
    tags = ls_remote("FreeCAD/FreeCAD", "refs/tags/*")
    vers = set()
    for ref in tags:
        m = re.match(r"refs/tags/(\d+\.\d+(?:\.\d+)?)$", ref)
        if m:
            vers.add(m.group(1))
    return sorted(vers, key=vkey)[-1] if vers else None


def asset_names(fc, version):
    """Asset names for `version`, derived from the pinned names."""
    old = fc["version"]
    return {k: fc[k].replace(old, version) for k in ("windows_archive", "windows_installer", "linux_appimage")}


def url_exists(url):
    req = urllib.request.Request(url, method="HEAD", headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status < 400
    except Exception:
        return False


def api_digests(tag):
    try:
        req = urllib.request.Request("https://api.github.com/repos/FreeCAD/FreeCAD/releases/tags/%s" % tag, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            rel = json.load(r)
        return {a["name"]: (a.get("digest") or "").replace("sha256:", "") or None for a in rel.get("assets", [])}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    m = json.load(open(MANIFEST), object_pairs_hook=collections.OrderedDict)
    report = {"freecad": {}, "addons": [], "errors": []}

    fc = m["freecad"]
    try:
        newest = latest_freecad()
        r = {"pinned": fc["version"], "latest": newest, "update": bool(newest and vkey(newest) > vkey(fc["version"]))}
        if r["update"]:
            names = asset_names(fc, newest)
            base = "https://github.com/FreeCAD/FreeCAD/releases/download/%s/" % newest
            r["assets"] = {k: {"name": n, "exists": url_exists(base + n)} for k, n in names.items()}
            r["assets_ok"] = all(x["exists"] for x in r["assets"].values())
            r["digests"] = {k: api_digests(newest).get(n) for k, n in names.items()}
        report["freecad"] = r
    except Exception as e:
        report["errors"].append("FreeCAD: %s" % e)

    for ad in m["addons"] + m.get("optional_addons", []):
        try:
            head = ls_remote(ad["repo"], "refs/heads/%s" % ad["branch"]).get("refs/heads/%s" % ad["branch"])
            report["addons"].append({"name": ad["name"], "repo": ad["repo"], "pinned": ad["ref"], "latest": head,
                                     "update": bool(head and head != ad["ref"])})
        except Exception as e:
            report["errors"].append("%s: %s" % (ad["name"], e))

    if a.apply:
        changed = []
        r = report.get("freecad", {})
        if r.get("update") and r.get("assets_ok"):
            old = fc["version"]
            names = asset_names(fc, r["latest"])
            fc["version"] = fc["tag"] = r["latest"]
            fc.update(names)
            fc["sha256"] = {"windows_archive": r["digests"].get("windows_archive"),
                            "windows_installer": r["digests"].get("windows_installer")}
            fc["release_url"] = "https://github.com/FreeCAD/FreeCAD/releases/tag/%s" % r["latest"]
            changed.append("FreeCAD %s -> %s" % (old, r["latest"]))
        elif r.get("update"):
            report["errors"].append("FreeCAD %s found but not all expected assets exist - pin not changed" % r["latest"])
        for info in report["addons"]:
            if info["update"]:
                for ad in m["addons"] + m.get("optional_addons", []):
                    if ad["name"] == info["name"]:
                        ad["ref"] = info["latest"]
                        import datetime
                        ad["pinned"] = datetime.date.today().isoformat()
                        changed.append("%s -> %s" % (ad["name"], info["latest"][:10]))
        if changed:
            with open(MANIFEST, "w") as f:
                f.write(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
        report["applied"] = changed

    if a.json:
        print(json.dumps(report, indent=2))
        return
    r = report["freecad"]
    print("FreeCAD   pinned %-8s latest %-8s %s" % (r.get("pinned"), r.get("latest"),
                                                   "UPDATE AVAILABLE" if r.get("update") else "up to date"))
    if r.get("update"):
        for k, x in r["assets"].items():
            print("   %-18s %-55s %s" % (k, x["name"], "ok" if x["exists"] else "MISSING"))
    for ad in report["addons"]:
        print("%-9s pinned %s  latest %s  %s" % (ad["name"], ad["pinned"][:10], (ad["latest"] or "?")[:10],
                                                 "newer commits" if ad["update"] else "up to date"))
    for e in report["errors"]:
        print("ERROR:", e)
    if report.get("applied") is not None:
        print("applied:", ", ".join(report["applied"]) or "nothing to change")


if __name__ == "__main__":
    sys.exit(main())
