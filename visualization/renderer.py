from __future__ import annotations

from core.constants import COLOR_LETTER_TO_CODE
from core.cube_state import CubeState


_CODE_TO_LETTER = {v: k for k, v in COLOR_LETTER_TO_CODE.items()}


def render_cube_flat(cube: CubeState) -> str:
    s = cube.stickers
    lines: list[str] = []
    lines.append('')
    lines.append('전개도:')
    lines.append('')
    for row in s[0]:
        lines.append('      ' + ' '.join(_CODE_TO_LETTER[int(v)] for v in row))
    for i in range(3):
        line = []
        line.append(' '.join(_CODE_TO_LETTER[int(v)] for v in s[4][i]))
        line.append(' '.join(_CODE_TO_LETTER[int(v)] for v in s[2][i]))
        line.append(' '.join(_CODE_TO_LETTER[int(v)] for v in s[5][i]))
        line.append(' '.join(_CODE_TO_LETTER[int(v)] for v in s[3][i]))
        lines.append(' '.join(line))
    for idx, row in enumerate(s[1]):
        prefix = '      '
        lines.append(prefix + ' '.join(_CODE_TO_LETTER[int(v)] for v in row))
        if idx != 2:
            lines[-1] = prefix + lines[-1].lstrip()
    lines.append('')
    return '\n'.join(lines)
