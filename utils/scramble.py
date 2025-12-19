from __future__ import annotations

import random

from core.constants import MOVE_TOKENS


def generate_scramble(length: int = 20, rng: random.Random | None = None) -> list[str]:
    rng = rng or random.Random()
    last_face_group = None
    scramble: list[str] = []
    for _ in range(length):
        token = rng.choice(MOVE_TOKENS)
        face_group = token[0]
        while last_face_group == face_group:
            token = rng.choice(MOVE_TOKENS)
            face_group = token[0]
        scramble.append(token)
        last_face_group = face_group
    return scramble
