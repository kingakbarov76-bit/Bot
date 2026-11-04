"""Sort a messy folder (e.g. Downloads) into subfolders by file type. Safe: dry-run first, undo log.
Usage:
  python organize.py "C:/Users/Me/Downloads" --dry-run   # show what would happen
  python organize.py "C:/Users/Me/Downloads"             # do it
  python organize.py "C:/Users/Me/Downloads" --undo      # put everything back
"""
import argparse, json, pathlib, shutil

TYPES = {
    "Rasmlar": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".svg"},
    "Videolar": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Musiqa": {".mp3", ".wav", ".m4a", ".ogg", ".flac"},
    "Hujjatlar": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".ppt", ".pptx"},
    "Jadvallar": {".xls", ".xlsx", ".csv", ".ods"},
    "Arxivlar": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Dasturlar": {".exe", ".msi", ".apk", ".dmg", ".deb"},
    "Kod": {".py", ".js", ".html", ".css", ".json", ".php", ".java", ".sql"},
}
LOG = ".organize_log.json"


def category(p):
    ext = p.suffix.lower()
    return next((name for name, exts in TYPES.items() if ext in exts), "Boshqa")


def unique(dst):
    if not dst.exists():
        return dst
    i = 1
    while True:
        cand = dst.with_name(f"{dst.stem} ({i}){dst.suffix}")
        if not cand.exists():
            return cand
        i += 1


def organize(folder, dry):
    moves = []
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.name != LOG and not p.name.startswith("."):
            dst = unique(folder / category(p) / p.name)
            moves.append((str(p), str(dst)))
            print(("[sinov] " if dry else "") + f"{p.name}  →  {dst.parent.name}/")
            if not dry:
                dst.parent.mkdir(exist_ok=True)
                shutil.move(str(p), str(dst))
    if not dry and moves:
        (folder / LOG).write_text(json.dumps(moves, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Jami: {len(moves)} ta fayl" + (" (hech narsa ko'chirilmadi, bu sinov)" if dry else ""))
    return moves


def undo(folder):
    log = folder / LOG
    if not log.exists():
        print("Qaytarish uchun yozuv topilmadi."); return 0
    moves = json.loads(log.read_text(encoding="utf-8"))
    for src, dst in reversed(moves):
        if pathlib.Path(dst).exists():
            shutil.move(dst, unique(pathlib.Path(src)))
    for d in TYPES.keys() | {"Boshqa"}:
        sub = folder / d
        if sub.is_dir() and not any(sub.iterdir()):
            sub.rmdir()
    log.unlink(); print(f"Qaytarildi: {len(moves)} ta fayl")
    return len(moves)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--undo", action="store_true")
    a = ap.parse_args()
    f = pathlib.Path(a.folder).expanduser()
    undo(f) if a.undo else organize(f, a.dry_run)
