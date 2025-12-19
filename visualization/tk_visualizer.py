from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ai.cube_ai_state import CubeAIState
from core.constants import DEFAULT_FACE_COLOR, FACE_NAMES
from core.cube_state import CubeState
from core.move_engine import CubeMoveEngine
from utils.scramble import generate_scramble


_COLOR_CODE_TO_TK = {
    1: 'white',
    2: 'yellow',
    3: 'green',
    4: 'blue',
    5: 'orange',
    6: 'red',
}

_COLOR_NAME_BY_CODE = {
    1: 'white',
    2: 'yellow',
    3: 'green',
    4: 'blue',
    5: 'orange',
    6: 'red',
}


def _face_label(face: int) -> str:
    face_letter = FACE_NAMES[face]
    color_code = int(DEFAULT_FACE_COLOR[face])
    return f"{face_letter}({_COLOR_NAME_BY_CODE.get(color_code, str(color_code))})"


def _parse_moves(text: str) -> list[str]:
    text = (text or '').replace(',', ' ').strip()
    if not text:
        return []
    return [t for t in text.split() if t]


class CubeVisualizerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title('Cube Visualizer')

        self.cube = CubeState.solved()
        self.engine = CubeMoveEngine(self.cube)

        self.sticker_size = 26
        self.margin = 12
        self._build_ui()
        self._redraw()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=10)
        outer.grid(row=0, column=0, sticky='nsew')

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=0)
        outer.rowconfigure(0, weight=1)

        canvas_w, canvas_h = self._canvas_size()
        self.canvas = tk.Canvas(outer, width=canvas_w, height=canvas_h, highlightthickness=1)
        self.canvas.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

        controls = ttk.Frame(outer)
        controls.grid(row=0, column=1, sticky='ns')

        moves_frame = ttk.LabelFrame(controls, text='Moves')
        moves_frame.grid(row=0, column=0, sticky='ew')

        tokens = self._supported_move_tokens()
        cols = 9
        for idx, tok in enumerate(tokens):
            r, c = divmod(idx, cols)
            b = ttk.Button(moves_frame, text=tok, width=4, command=lambda t=tok: self.apply_move(t))
            b.grid(row=r, column=c, padx=2, pady=2, sticky='ew')

        scramble_frame = ttk.LabelFrame(controls, text='Scramble')
        scramble_frame.grid(row=1, column=0, sticky='ew', pady=(10, 0))
        scramble_frame.columnconfigure(0, weight=1)

        self.scramble_var = tk.StringVar()
        self.scramble_entry = ttk.Entry(scramble_frame, textvariable=self.scramble_var, width=38)
        self.scramble_entry.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        ttk.Button(scramble_frame, text='Apply', command=self.apply_scramble).grid(
            row=1, column=0, sticky='ew', padx=5, pady=(0, 5)
        )
        ttk.Button(scramble_frame, text='Random(20)', command=self.apply_random_scramble_20).grid(
            row=1, column=1, sticky='ew', padx=5, pady=(0, 5)
        )

        ttk.Button(scramble_frame, text='Reset', command=self.reset_cube).grid(
            row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=(0, 5)
        )

        cross_frame = ttk.LabelFrame(controls, text='Cross Solution')
        cross_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        cross_frame.columnconfigure(0, weight=1)

        ttk.Button(cross_frame, text='Compute', command=self.compute_cross).grid(
            row=0, column=0, sticky='ew', padx=5, pady=5
        )

        self.cross_text = tk.Text(cross_frame, width=40, height=12, wrap='word')
        self.cross_text.grid(row=1, column=0, sticky='nsew', padx=5, pady=(0, 5))
        self.cross_text.configure(state='disabled')

        self.status_var = tk.StringVar(value='Ready')
        status = ttk.Label(controls, textvariable=self.status_var)
        status.grid(row=3, column=0, sticky='ew', pady=(10, 0))

    def _supported_move_tokens(self) -> list[str]:
        # Keep this list in sync with CubeMoveEngine.apply().
        return [
            'U', "U'", 'U2',
            'D', "D'", 'D2',
            'F', "F'", 'F2',
            'B', "B'", 'B2',
            'L', "L'", 'L2',
            'R', "R'", 'R2',
            'x', "x'", 'x2',
            'y', "y'", 'y2',
            'z', "z'", 'z2',
            'M', "M'", 'M2',
            'E', "E'", 'E2',
            'S', "S'", 'S2',
            'r', "r'", 'r2',
            'l', "l'", 'l2',
            'u', "u'", 'u2',
            'd', "d'", 'd2',
            'f', "f'", 'f2',
            'b', "b'", 'b2',
        ]

    def _canvas_size(self) -> tuple[int, int]:
        s = self.sticker_size
        m = self.margin
        face = 3 * s
        width = 4 * face + 5 * m
        height = 3 * face + 4 * m
        return width, height

    def _face_top_left(self) -> dict[int, tuple[int, int]]:
        # Layout matches visualization.renderer.render_cube_flat
        # U on top, then L F R B, then D at bottom.
        s = self.sticker_size
        m = self.margin
        face = 3 * s

        x0 = m
        y0 = m
        return {
            0: (x0 + (face + m), y0),  # U
            4: (x0, y0 + (face + m)),  # L
            2: (x0 + (face + m), y0 + (face + m)),  # F
            5: (x0 + 2 * (face + m), y0 + (face + m)),  # R
            3: (x0 + 3 * (face + m), y0 + (face + m)),  # B
            1: (x0 + (face + m), y0 + 2 * (face + m)),  # D
        }

    def _redraw(self) -> None:
        self.canvas.delete('all')
        pos = self._face_top_left()
        s = self.sticker_size

        for face_id, (fx, fy) in pos.items():
            for r in range(3):
                for c in range(3):
                    code = int(self.cube.stickers[face_id, r, c])
                    color = _COLOR_CODE_TO_TK.get(code, 'gray')
                    x1 = fx + c * s
                    y1 = fy + r * s
                    x2 = x1 + s
                    y2 = y1 + s
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black')

    def _set_cross_text(self, text: str) -> None:
        self.cross_text.configure(state='normal')
        self.cross_text.delete('1.0', 'end')
        self.cross_text.insert('1.0', text)
        self.cross_text.configure(state='disabled')

    def apply_move(self, token: str) -> None:
        try:
            self.engine.apply(token)
        except Exception as e:
            self.status_var.set(f'Invalid move: {token} ({e})')
            return
        self.status_var.set(f'Applied move: {token}')
        self._redraw()

    def apply_scramble(self) -> None:
        tokens = _parse_moves(self.scramble_var.get())
        if not tokens:
            self.status_var.set('No scramble input')
            return

        try:
            for t in tokens:
                self.engine.apply(t)
        except Exception as e:
            self.status_var.set(f'Scramble error: {e}')
            return

        self.status_var.set(f'Applied scramble ({len(tokens)} moves)')
        self._redraw()
        self.compute_cross()

    def apply_random_scramble_20(self) -> None:
        self._reset_cube_state()
        tokens = generate_scramble(length=20)
        self.scramble_var.set(' '.join(tokens))
        self.apply_scramble()

    def _reset_cube_state(self) -> None:
        self.cube = CubeState.solved()
        self.engine = CubeMoveEngine(self.cube)
        self._redraw()

    def reset_cube(self) -> None:
        self._reset_cube_state()
        self.scramble_var.set('')
        self.status_var.set('Reset to solved')
        self._set_cross_text('')

    def compute_cross(self) -> None:
        try:
            best_len, best = CubeAIState.find_best_cross_solutions(
                cube_state=self.cube,
                max_depth=None,
                include_white=True,
            )
        except Exception as e:
            self._set_cross_text(f'Error computing cross: {e}')
            self.status_var.set('Cross compute failed')
            return

        if not best:
            self._set_cross_text('No cross solution found.')
            self.status_var.set('No cross solution')
            return

        lines: list[str] = []
        lines.append(f'Best cross length: {best_len}')
        for face, solution in best:
            moves = ' '.join(solution)
            lines.append(f'- Face: {_face_label(face)} | len={len(solution)} | {moves}')
        self._set_cross_text('\n'.join(lines))
        self.status_var.set('Cross computed')


def main() -> None:
    root = tk.Tk()
    CubeVisualizerApp(root)
    root.mainloop()
