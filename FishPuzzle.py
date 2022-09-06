import copy
import time
from enum import Enum
from typing import List, Optional

from tqdm import tqdm

PIECE_FILE_PATH = "pieces.txt"
BOARD_WIDTH = 3
BOARD_HEIGHT = 3


class Side(Enum):
    HEAD = 1
    TAIL = 2

    def __str__(self):
        if self == Side.HEAD:
            return '>'
        else:
            return '<'


class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class Connection:
    def __init__(self, name: str, side: Side):
        self.name = name
        self.side = side

    def is_compat(self, other: 'Connection') -> bool:
        return self.name == other.name and self.side != other.side

    def __eq__(self, other: 'Connection') -> bool:
        return self.name == other.name and self.side == other.side

    def __ne__(self, other: 'Connection') -> bool:
        return not self.__eq__(other)


class Piece:
    def __init__(self, left: Connection, right: Connection, up: Connection, down: Connection):
        self.left = left
        self.right = right
        self.up = up
        self.down = down

    def is_compat(self, other: 'Piece', direction: Direction) -> bool:
        if direction == Direction.LEFT:
            return self.left.is_compat(other.right)
        if direction == Direction.RIGHT:
            return self.right.is_compat(other.left)
        if direction == Direction.UP:
            return self.up.is_compat(other.down)
        return self.down.is_compat(other.up)

    def rotated_clockwise(self, rotations: int) -> 'Piece':
        rotations = rotations % 4
        if rotations == 0:
            return Piece(self.left, self.right, self.up, self.down)
        if rotations == 1:
            return Piece(self.down, self.up, self.left, self.right)
        if rotations == 2:
            return Piece(self.right, self.left, self.down, self.up)
        if rotations == 3:
            return Piece(self.up, self.down, self.right, self.left)

    def to_output_string(self, max_piece_name_length: int = None) -> str:
        if max_piece_name_length is None:
            max_piece_name_length = max(
                [len(self.left.name), len(self.right.name), len(self.up.name), len(self.down.name)]) + 2
        middle_section_length = 2 * max_piece_name_length + 3
        top_border = '+' + ('-' * middle_section_length) + '+\n'
        middle_section_start = '|' + (' ' * int(middle_section_length / 2))
        middle_section_end = (' ' * int(middle_section_length / 2)) + '|\n'

        out_string = top_border
        up_string = str(self.up.side) + self.up.name
        down_string = self.down.name + str(self.down.side)
        left_string = str(self.left.side) + self.left.name
        right_string = self.right.name + str(self.right.side)

        for char in up_string:
            out_string += middle_section_start + char + middle_section_end

        for i in range(max_piece_name_length + 1 - len(up_string)):
            out_string += middle_section_start + ' ' + middle_section_end

        out_string += '|' + left_string + (
                ' ' * (middle_section_length - len(left_string) - len(right_string))) + right_string + '|\n'

        for i in range(max_piece_name_length + 1 - len(down_string)):
            out_string += middle_section_start + ' ' + middle_section_end

        for char in down_string:
            out_string += middle_section_start + char + middle_section_end

        out_string += top_border

        return out_string[:-1]

    def __repr__(self) -> str:
        return self.to_output_string()

    def __str__(self) -> str:
        return self.to_output_string()


def _get_empty_piece_string(max_piece_name_length: int) -> str:
    middle_section_length = 2 * max_piece_name_length + 3
    top_border = '+' + ('-' * middle_section_length) + '+\n'
    middle_section = '|' + (' ' * middle_section_length) + '|\n'
    out_string = top_border + middle_section * middle_section_length + top_border
    return out_string[:-1]


class Board:
    def __init__(self, pieces: List[List[Piece]] = None):
        if pieces is not None:
            if len(pieces) == BOARD_HEIGHT and len(pieces[0]) == BOARD_WIDTH:
                pieces = copy.deepcopy(pieces)
            else:
                print("WARNING: pieces passed in with invalid size, defaulting to empty board")

        if pieces is None:
            pieces = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

        self.pieces: List[List[Optional[Piece]]] = pieces

    def _get_max_piece_name_length(self) -> int:
        max_val = 0
        for row in self.pieces:
            for piece in row:
                if piece is not None:
                    for name in [piece.left.name, piece.right.name, piece.up.name, piece.down.name]:
                        if len(name) + 1 > max_val:
                            max_val = len(name) + 1
        return max_val

    def __repr__(self) -> str:
        max_piece_name_length = self._get_max_piece_name_length()
        board_strings = [[piece.to_output_string(max_piece_name_length).split(
            '\n') if piece is not None else _get_empty_piece_string(max_piece_name_length).split('\n') for piece in
                          board_row] for board_row in self.pieces]

        piece_str_list_length = len(board_strings[0][0])

        out_string = ''
        for i in range(len(self.pieces)):
            for line in range(piece_str_list_length):
                for j in range(len(self.pieces[i])):
                    out_string += board_strings[i][j][line]
                out_string += '\n'

        return out_string

    def __str__(self) -> str:
        return repr(self)

    def is_valid(self) -> bool:
        for piece_y in range(len(self.pieces)):
            for piece_x in range(len(self.pieces[piece_y])):
                piece = self.pieces[piece_y][piece_x]

                if piece is None:
                    continue

                if piece_y + 1 < len(self.pieces):
                    other_piece = self.pieces[piece_y + 1][piece_x]
                    if other_piece is not None and not piece.down.is_compat(other_piece.up):
                        return False

                if piece_x + 1 < len(self.pieces[piece_y]):
                    other_piece = self.pieces[piece_y][piece_x + 1]
                    if other_piece is not None and not piece.right.is_compat(other_piece.left):
                        return False
        return True

    def is_complete(self) -> bool:
        for i in range(len(self.pieces)):
            for j in range(len(self.pieces[i])):
                if self.pieces[i][j] is None:
                    return False
        return self.is_valid()

    def add_piece(self, piece: Piece) -> bool:
        for i in range(len(self.pieces)):
            for j in range(len(self.pieces[i])):
                if self.pieces[i][j] is None:
                    self.pieces[i][j] = piece
                    return True
        return False

    def remove_last_piece(self):
        for i in range(len(self.pieces) - 1, -1, -1):
            for j in range(len(self.pieces[i]) - 1, -1, -1):
                if self.pieces[i][j] is not None:
                    self.pieces[i][j] = None
                    return


def connection_from_str(string: str) -> Connection:
    if string.endswith('>'):
        side = Side.HEAD
    elif string.endswith('<'):
        side = Side.TAIL
    else:
        raise AssertionError(f'Invalid connection string: {string}')
    return Connection(string[:-1], side)


def do_recursive_descent(pieces: List[Piece], board: Board = None) -> List[Board]:
    if board is None:
        board = Board()
    else:
        board = Board(board.pieces)

    if board.is_complete():
        return [board]

    valid_boards = []

    for piece_idx in tqdm(range(len(pieces)), leave=False):
        piece = pieces[piece_idx]
        for rotation in range(4):
            rotated_piece = piece.rotated_clockwise(rotation)

            if not board.add_piece(rotated_piece):
                return valid_boards

            if not board.is_valid():
                board.remove_last_piece()
                continue

            new_pieces = pieces[:piece_idx] + pieces[piece_idx + 1:]
            valid_boards.extend(do_recursive_descent(new_pieces, board))
            board.remove_last_piece()

    return valid_boards


def main():
    pieces = []
    with open(PIECE_FILE_PATH, 'r') as file:
        for line in file:
            line = line.strip()

            parts = line.split()
            connections = list(map(connection_from_str, parts))
            piece = Piece(connections[0], connections[2], connections[1], connections[3])
            pieces.append(piece)

    start = time.time()
    solutions = do_recursive_descent(pieces)
    end = time.time()
    print(f'{len(solutions)} solutions found in {end - start:.2f} seconds')


if __name__ == '__main__':
    main()
