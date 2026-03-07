"""
jav db — query and export the local JAV metadata database.

Usage:
    jav db list
    jav db show MISM-410
    jav db search "Emma"
    jav db stats
    jav db export --format json
    jav db export --format csv
"""

from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path

from .config import open_db


def cmd_list(conn, limit: int = 50):
    rows = conn.execute("""
        SELECT v.jav_id, v.title, v.release_date, v.publisher,
               GROUP_CONCAT(a.name, ', ') AS actresses
        FROM videos v
        LEFT JOIN video_actresses va ON va.video_id = v.id
        LEFT JOIN actresses a ON a.id = va.actress_id
        GROUP BY v.id
        ORDER BY v.release_date DESC
        LIMIT ?
    """, (limit,)).fetchall()

    if not rows:
        print("No videos in database.")
        return

    print(f"\n{'ID':<12} {'Date':<12} {'Publisher':<18} {'Actresses':<28} Title")
    print("─" * 100)
    for r in rows:
        print(
            f"{r['jav_id']:<12} {(r['release_date'] or '—'):<12} "
            f"{(r['publisher'] or '—')[:16]:<18} "
            f"{(r['actresses'] or '—')[:26]:<28} "
            f"{(r['title'] or '—')[:48]}"
        )
    print(f"\n{len(rows)} record(s)")


def cmd_show(conn, jav_id: str):
    v = conn.execute("SELECT * FROM videos WHERE jav_id=?", (jav_id.upper(),)).fetchone()
    if not v:
        print(f"Not found: {jav_id}")
        return

    actresses = conn.execute("""
        SELECT a.name FROM actresses a
        JOIN video_actresses va ON va.actress_id = a.id
        WHERE va.video_id = ?
    """, (v["id"],)).fetchall()

    genres = conn.execute("""
        SELECT g.name FROM genres g
        JOIN video_genres vg ON vg.genre_id = g.id
        WHERE vg.video_id = ?
    """, (v["id"],)).fetchall()

    screenshots = json.loads(v["screenshots_json"] or "[]")

    print(f"\n{'═'*60}")
    for col in v.keys():
        if col in ("screenshots_json",):
            continue
        val = v[col]
        if col == "plot" and val and len(val) > 120:
            val = val[:120] + "…"
        print(f"  {col:<20}: {val}")
    print(f"  {'actresses':<20}: {', '.join(r['name'] for r in actresses) or '—'}")
    print(f"  {'genres':<20}: {', '.join(r['name'] for r in genres) or '—'}")
    print(f"  {'screenshots':<20}: {len(screenshots)} URL(s)")
    print(f"{'═'*60}\n")


def cmd_search(conn, query: str):
    q = f"%{query}%"
    rows = conn.execute("""
        SELECT DISTINCT v.jav_id, v.title, v.release_date, v.publisher
        FROM videos v
        LEFT JOIN video_actresses va ON va.video_id = v.id
        LEFT JOIN actresses a ON a.id = va.actress_id
        LEFT JOIN video_genres vg ON vg.video_id = v.id
        LEFT JOIN genres g ON g.id = vg.genre_id
        WHERE v.jav_id LIKE ? OR v.title LIKE ? OR v.plot LIKE ?
           OR a.name LIKE ? OR a.aliases_json LIKE ? OR g.name LIKE ? OR v.publisher LIKE ?
        ORDER BY v.release_date DESC
    """, (q,)*7).fetchall()

    if not rows:
        print(f'No results for "{query}"')
        return

    print(f'\n{len(rows)} result(s) for "{query}":')
    print(f"{'ID':<12} {'Date':<12} {'Publisher':<18} Title")
    print("─" * 80)
    for r in rows:
        print(
            f"{r['jav_id']:<12} {(r['release_date'] or '—'):<12} "
            f"{(r['publisher'] or '—')[:16]:<18} {(r['title'] or '—')[:50]}"
        )


def cmd_stats(conn):
    total    = conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
    act_cnt  = conn.execute("SELECT COUNT(*) FROM actresses").fetchone()[0]
    gen_cnt  = conn.execute("SELECT COUNT(*) FROM genres").fetchone()[0]
    has_post = conn.execute("SELECT COUNT(*) FROM videos WHERE poster_url IS NOT NULL").fetchone()[0]
    has_prev = conn.execute("SELECT COUNT(*) FROM videos WHERE preview_gif_url IS NOT NULL OR preview_mp4_url IS NOT NULL").fetchone()[0]

    top_pub = conn.execute("""
        SELECT publisher, COUNT(*) c FROM videos
        WHERE publisher IS NOT NULL GROUP BY publisher ORDER BY c DESC LIMIT 5
    """).fetchall()

    top_act = conn.execute("""
        SELECT a.name, COUNT(*) c FROM actresses a
        JOIN video_actresses va ON va.actress_id = a.id
        GROUP BY a.id ORDER BY c DESC LIMIT 5
    """).fetchall()

    print(f"\n{'─'*40}")
    print(f"  Videos          : {total}")
    print(f"  Actresses        : {act_cnt}")
    print(f"  Genres           : {gen_cnt}")
    print(f"  Has poster URL   : {has_post}")
    print(f"  Has preview      : {has_prev}")
    if top_pub:
        print(f"\n  Top publishers:")
        for r in top_pub:
            print(f"    {r['publisher']:<25} {r['c']}")
    if top_act:
        print(f"\n  Top actresses:")
        for r in top_act:
            print(f"    {r['name']:<25} {r['c']}")
    print(f"{'─'*40}\n")


def cmd_export(conn, fmt: str, db_path: str):
    rows = conn.execute("""
        SELECT v.*,
               GROUP_CONCAT(DISTINCT a.name) AS actresses,
               GROUP_CONCAT(DISTINCT g.name) AS genres
        FROM videos v
        LEFT JOIN video_actresses va ON va.video_id = v.id
        LEFT JOIN actresses a ON a.id = va.actress_id
        LEFT JOIN video_genres vg ON vg.video_id = v.id
        LEFT JOIN genres g ON g.id = vg.genre_id
        GROUP BY v.id
    """).fetchall()

    stem = Path(db_path).stem

    if fmt == "json":
        fname = f"{stem}_export.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump([dict(r) for r in rows], f, ensure_ascii=False, indent=2)
    else:
        fname = f"{stem}_export.csv"
        with open(fname, "w", newline="", encoding="utf-8") as f:
            if rows:
                w = csv.DictWriter(f, fieldnames=rows[0].keys())
                w.writeheader()
                w.writerows(dict(r) for r in rows)

    print(f"Exported {len(rows)} records → {fname}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None, prog: str = "jav db"):
    parser = argparse.ArgumentParser(prog=prog, description="Query the JAV database")
    parser.add_argument("--db", default="jav.db")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list")
    p_show = sub.add_parser("show");   p_show.add_argument("id")
    p_srch = sub.add_parser("search"); p_srch.add_argument("query")
    sub.add_parser("stats")
    p_exp  = sub.add_parser("export"); p_exp.add_argument("--format", choices=["json","csv"], default="json")

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help(); sys.exit(1)

    conn = open_db(args.db)
    match args.cmd:
        case "list":   cmd_list(conn)
        case "show":   cmd_show(conn, args.id)
        case "search": cmd_search(conn, args.query)
        case "stats":  cmd_stats(conn)
        case "export": cmd_export(conn, args.format, args.db)
    conn.close()


if __name__ == "__main__":
    main()
