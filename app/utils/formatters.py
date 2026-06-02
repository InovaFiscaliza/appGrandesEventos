import base64
import re
import unicodedata
from pathlib import Path
from typing import List, Optional


def _img_b64(path: str) -> Optional[str]:
    p = Path(path)
    if not p.exists():
        return None
    return base64.b64encode(p.read_bytes()).decode("utf-8")


def _normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.strip().lower()


def _valid_neg_coord(value: str) -> bool:
    if value is None:
        return True
    v = value.strip()
    if v == "":
        return True
    return re.match(r"^-\d+\.\d{6}$", v) is not None


def _first_col_match(columns, *preds):
    for c in columns:
        s = (c or "").strip().lower()
        for p in preds:
            if p(s):
                return c
    return None


def _col_to_index(letter: str) -> int:
    letter = (letter or "").upper()
    res = 0
    for ch in letter:
        if not ("A" <= ch <= "Z"):
            continue
        res = res * 26 + (ord(ch) - ord("A") + 1)
    return res


def _first_empty_row_in_block(aba, start_col_letter: str, end_col_letter: str) -> int:
    start_idx = _col_to_index(start_col_letter)
    end_idx = _col_to_index(end_col_letter)
    max_len = 1
    for idx in range(start_idx, end_idx + 1):
        try:
            vals = aba.col_values(idx)
            if len(vals) > max_len:
                max_len = len(vals)
        except Exception:
            pass
    return max_len + 1


def _first_row_where_col_empty(aba, col_letter: str, start_row: int = 2) -> int:
    col_idx = _col_to_index(col_letter)
    try:
        col_vals = aba.col_values(col_idx)
    except Exception:
        col_vals = []
    if len(col_vals) < start_row:
        return start_row
    for i in range(start_row - 1, len(col_vals)):
        if (col_vals[i] or "").strip() == "":
            return i + 1
    return len(col_vals) + 1


def _next_sequential_id(aba, col_letter: str = "H", start_row: int = 2) -> str:
    col_idx = _col_to_index(col_letter)
    try:
        col_vals = aba.col_values(col_idx)
    except Exception:
        col_vals = []

    max_num = 0
    for i, v in enumerate(col_vals, start=1):
        if i < start_row:
            continue
        s = (v or "").strip()
        if not s:
            continue
        match = re.search(r"Abo-(\d+)", s, re.IGNORECASE)
        if match:
            try:
                n = int(match.group(1))
                if n > max_num:
                    max_num = n
            except Exception:
                pass

    return f"Abo-{max_num + 1:02d}"
