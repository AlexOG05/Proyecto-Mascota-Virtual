"""
BattleLogger — guarda y recupera el historial de batallas en CSV
"""

import csv
import time
from pathlib import Path

BASE_DIR  = Path(__file__).parent.parent
CSV_PATH  = BASE_DIR / "data" / "history" / "battles.csv"
HEADERS   = ["timestamp", "pet_name", "codepet", "zone", "enemy", "won", "xp_gained"]
MAX_ROWS  = 50


class BattleLogger:

    def log(self, pet_name: str, codepet: str, zone: str,
            enemy: str, won: bool, xp_gained: int):
        rows = self._read_all()
        rows.append({
            "timestamp": round(time.time()),
            "pet_name":  pet_name,
            "codepet":   codepet,
            "zone":      zone,
            "enemy":     enemy,
            "won":       "1" if won else "0",
            "xp_gained": xp_gained,
        })
        # Conservar solo las últimas MAX_ROWS filas
        rows = rows[-MAX_ROWS:]
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)

    def get_recent(self, limit: int = 20) -> list:
        rows = self._read_all()
        result = []
        for row in reversed(rows[-limit:]):
            result.append({
                "timestamp": int(row["timestamp"]),
                "pet_name":  row["pet_name"],
                "codepet":   row["codepet"],
                "zone":      row["zone"],
                "enemy":     row["enemy"],
                "won":       row["won"] == "1",
                "xp_gained": int(row["xp_gained"]),
            })
        return result

    def _read_all(self) -> list:
        if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
            return []
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
