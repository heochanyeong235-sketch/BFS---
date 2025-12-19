from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .constants import DEFAULT_FACE_COLOR


@dataclass
class CubeState:
    stickers: np.ndarray  # shape (6,3,3), int codes

    @classmethod
    def solved(cls) -> CubeState:
        cube = np.empty((6, 3, 3), dtype=np.int8)
        for face, color_code in DEFAULT_FACE_COLOR.items():
            cube[face, :, :] = color_code
        return cls(cube)

    def copy(self) -> CubeState:
        return CubeState(self.stickers.copy())

    def as_numpy(self) -> np.ndarray:
        return self.stickers

    def validate(self) -> None:
        if not isinstance(self.stickers, np.ndarray):
            raise TypeError('stickers must be a numpy array')
        if self.stickers.shape != (6, 3, 3):
            raise ValueError(f'expected shape (6,3,3), got {self.stickers.shape}')
        if not np.issubdtype(self.stickers.dtype, np.integer):
            raise TypeError('stickers must be an integer array')
        values = self.stickers.reshape(-1)
        if values.min() < 1 or values.max() > 6:
            raise ValueError('sticker values must be in [1..6]')

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CubeState):
            return False
        return np.array_equal(self.stickers, other.stickers)
