from typing import List, Dict, Set

class SeatmapService:
    @staticmethod
    def build_seat_positions(
        total_seats: int,
        taken_seats: Set[str],
        selected_seats: Set[str],
        seats_per_row: int = 4,
    ) -> List[Dict]:
        seat_positions = []
        total_rows = total_seats // seats_per_row

        for r in range(1, total_rows + 1):
            row = {"left": [], "right": []}
            for s in range(1, seats_per_row + 1):
                seat_id = (r - 1) * seats_per_row + s
                
                pos = {
                    "seat_id": seat_id,
                    "top": 105 + (r - 1) * 25.10,
                    "left": (409 if s in [1, 2] else 380) + (0 if s % 2 == 1 else 24),
                    "occupied": str(seat_id) in taken_seats or str(seat_id) in selected_seats,
                }
                
                (row["left"] if s <= 2 else row["right"]).append(pos)
            seat_positions.append(row)

        return seat_positions