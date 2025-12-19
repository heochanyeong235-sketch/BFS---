from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .cube_state import CubeState
from .constants import FACE_U, FACE_D, FACE_F, FACE_B, FACE_L, FACE_R


@dataclass
class CubeMoveEngine:
    cube: CubeState

    def apply(self, move: str) -> None:
        move = move.strip()
        if not move:
            return
        token_to_method = {
            'R': self.R,
            "R'": self.R_prime,
            'R2': self.R2,
            'L': self.L,
            "L'": self.L_prime,
            'L2': self.L2,
            'U': self.U,
            "U'": self.U_prime,
            'U2': self.U2,
            'D': self.D,
            "D'": self.D_prime,
            'D2': self.D2,
            'F': self.F,
            "F'": self.F_prime,
            'F2': self.F2,
            'B': self.B,
            "B'": self.B_prime,
            'B2': self.B2,
            'x': self.x,
            "x'": self.x_prime,
            'x2': self.x2,
            'y': self.y,
            "y'": self.y_prime,
            'y2': self.y2,
            'z': self.z,
            "z'": self.z_prime,
            'z2': self.z2,
            'M': self.M,
            "M'": self.M_prime,
            'M2': self.M2,
            'E': self.E,
            "E'": self.E_prime,
            'E2': self.E2,
            'S': self.S,
            "S'": self.S_prime,
            'S2': self.S2,
            'r': self.r,
            "r'": self.r_prime,
            'r2': self.r2,
            'l': self.l,
            "l'": self.l_prime,
            'l2': self.l2,
            'u': self.u,
            "u'": self.u_prime,
            'u2': self.u2,
            'd': self.d,
            "d'": self.d_prime,
            'd2': self.d2,
            'f': self.f,
            "f'": self.f_prime,
            'f2': self.f2,
            'b': self.b,
            "b'": self.b_prime,
            'b2': self.b2,
        }
        fn = token_to_method.get(move)
        if fn is None:
            raise ValueError(f'unknown move token: {move!r}')
        fn()

    def apply_sequence(self, moves: list[str]) -> None:
        for m in moves:
            self.apply(m)

    @property
    def s(self) -> np.ndarray:
        return self.cube.stickers

    def _rot_cw(self, face: int) -> None:
        self.s[face] = np.rot90(self.s[face], -1)

    def R(self) -> None:
        self._rot_cw(FACE_R)
        temp = self.s[FACE_U][:, 2].copy()
        self.s[FACE_U][:, 2] = self.s[FACE_F][:, 2]
        self.s[FACE_F][:, 2] = self.s[FACE_D][:, 2]
        self.s[FACE_D][:, 2] = self.s[FACE_B][:, 0][::-1]
        self.s[FACE_B][:, 0] = temp[::-1]

    def R_prime(self) -> None:
        for _ in range(3):
            self.R()

    def R2(self) -> None:
        for _ in range(2):
            self.R()

    def L(self) -> None:
        self._rot_cw(FACE_L)
        temp = self.s[FACE_U][:, 0].copy()
        self.s[FACE_U][:, 0] = self.s[FACE_B][:, 2][::-1]
        self.s[FACE_B][:, 2] = self.s[FACE_D][:, 0][::-1]
        self.s[FACE_D][:, 0] = self.s[FACE_F][:, 0]
        self.s[FACE_F][:, 0] = temp

    def L_prime(self) -> None:
        for _ in range(3):
            self.L()

    def L2(self) -> None:
        for _ in range(2):
            self.L()

    def U(self) -> None:
        self._rot_cw(FACE_U)
        temp = self.s[FACE_L][0, :].copy()
        self.s[FACE_L][0, :] = self.s[FACE_F][0, :]
        self.s[FACE_F][0, :] = self.s[FACE_R][0, :]
        self.s[FACE_R][0, :] = self.s[FACE_B][0, :]
        self.s[FACE_B][0, :] = temp

    def U_prime(self) -> None:
        for _ in range(3):
            self.U()

    def U2(self) -> None:
        for _ in range(2):
            self.U()

    def F(self) -> None:
        self._rot_cw(FACE_F)
        temp = self.s[FACE_U][2, :].copy()
        self.s[FACE_U][2, :] = self.s[FACE_L][:, 2][::-1]
        self.s[FACE_L][:, 2] = self.s[FACE_D][0, :]
        self.s[FACE_D][0, :] = self.s[FACE_R][:, 0][::-1]
        self.s[FACE_R][:, 0] = temp

    def F_prime(self) -> None:
        for _ in range(3):
            self.F()

    def F2(self) -> None:
        for _ in range(2):
            self.F()

    def D(self) -> None:
        self._rot_cw(FACE_D)
        temp = self.s[FACE_L][2, :].copy()
        self.s[FACE_L][2, :] = self.s[FACE_B][2, :]
        self.s[FACE_B][2, :] = self.s[FACE_R][2, :]
        self.s[FACE_R][2, :] = self.s[FACE_F][2, :]
        self.s[FACE_F][2, :] = temp

    def D_prime(self) -> None:
        for _ in range(3):
            self.D()

    def D2(self) -> None:
        for _ in range(2):
            self.D()

    def B(self) -> None:
        self._rot_cw(FACE_B)
        temp = self.s[FACE_U][0, :].copy()
        self.s[FACE_U][0, :] = self.s[FACE_R][:, 2]
        self.s[FACE_R][:, 2] = self.s[FACE_D][2, :][::-1]
        self.s[FACE_D][2, :] = self.s[FACE_L][:, 0]
        self.s[FACE_L][:, 0] = temp[::-1]

    def B_prime(self) -> None:
        for _ in range(3):
            self.B()

    def B2(self) -> None:
        for _ in range(2):
            self.B()

    def x(self) -> None:
        self._rot_cw(FACE_R)
        self.s[FACE_L] = np.rot90(self.s[FACE_L], 1)
        temp = self.s[FACE_U].copy()
        self.s[FACE_U] = self.s[FACE_F]
        self.s[FACE_F] = self.s[FACE_D]
        self.s[FACE_D] = self.s[FACE_B]
        self.s[FACE_B] = temp

    def x_prime(self) -> None:
        for _ in range(3):
            self.x()

    def x2(self) -> None:
        for _ in range(2):
            self.x()

    def y(self) -> None:
        self._rot_cw(FACE_U)
        self.s[FACE_D] = np.rot90(self.s[FACE_D], 1)
        temp = self.s[FACE_L].copy()
        self.s[FACE_L] = self.s[FACE_F]
        self.s[FACE_F] = self.s[FACE_R]
        self.s[FACE_R] = self.s[FACE_B]
        self.s[FACE_B] = temp

    def y_prime(self) -> None:
        for _ in range(3):
            self.y()

    def y2(self) -> None:
        for _ in range(2):
            self.y()

    def z(self) -> None:
        self._rot_cw(FACE_F)
        self.s[FACE_B] = np.rot90(self.s[FACE_B], 1)
        temp = self.s[FACE_U].copy()
        self.s[FACE_U] = self.s[FACE_L][:, ::-1].T
        self.s[FACE_L] = self.s[FACE_D][:, ::-1].T
        self.s[FACE_D] = self.s[FACE_R][:, ::-1].T
        self.s[FACE_R] = temp.T

    def z_prime(self) -> None:
        for _ in range(3):
            self.z()

    def z2(self) -> None:
        for _ in range(2):
            self.z()

    def M(self) -> None:
        temp = self.s[FACE_U][:, 1].copy()
        self.s[FACE_U][:, 1] = self.s[FACE_B][:, 1][::-1]
        self.s[FACE_B][:, 1] = self.s[FACE_D][:, 1][::-1]
        self.s[FACE_D][:, 1] = self.s[FACE_F][:, 1]
        self.s[FACE_F][:, 1] = temp

    def M_prime(self) -> None:
        for _ in range(3):
            self.M()

    def M2(self) -> None:
        for _ in range(2):
            self.M()

    def E(self) -> None:
        temp = self.s[FACE_L][1, :].copy()
        self.s[FACE_L][1, :] = self.s[FACE_B][1, :]
        self.s[FACE_B][1, :] = self.s[FACE_R][1, :]
        self.s[FACE_R][1, :] = self.s[FACE_F][1, :]
        self.s[FACE_F][1, :] = temp

    def E_prime(self) -> None:
        for _ in range(3):
            self.E()

    def E2(self) -> None:
        for _ in range(2):
            self.E()

    def S(self) -> None:
        temp = self.s[FACE_U][1, :].copy()
        self.s[FACE_U][1, :] = self.s[FACE_L][:, 1][::-1]
        self.s[FACE_L][:, 1] = self.s[FACE_D][1, :]
        self.s[FACE_D][1, :] = self.s[FACE_R][:, 1][::-1]
        self.s[FACE_R][:, 1] = temp

    def S_prime(self) -> None:
        for _ in range(3):
            self.S()

    def S2(self) -> None:
        for _ in range(2):
            self.S()

    def r(self) -> None:
        self.R()
        self.M_prime()

    def r_prime(self) -> None:
        self.R_prime()
        self.M()

    def r2(self) -> None:
        self.R2()
        self.M2()

    def l(self) -> None:
        self.L()
        self.M()

    def l_prime(self) -> None:
        self.L_prime()
        self.M_prime()

    def l2(self) -> None:
        self.L2()
        self.M2()

    def u(self) -> None:
        self.U()
        self.E_prime()

    def u_prime(self) -> None:
        self.U_prime()
        self.E()

    def u2(self) -> None:
        self.U2()
        self.E2()

    def d(self) -> None:
        self.D()
        self.E()

    def d_prime(self) -> None:
        self.D_prime()
        self.E_prime()

    def d2(self) -> None:
        self.D2()
        self.E2()

    def f(self) -> None:
        self.F()
        self.S()

    def f_prime(self) -> None:
        self.F_prime()
        self.S_prime()

    def f2(self) -> None:
        self.F2()
        self.S2()

    def b(self) -> None:
        self.B()
        self.S_prime()

    def b_prime(self) -> None:
        self.B_prime()
        self.S()

    def b2(self) -> None:
        self.B2()
        self.S2()
