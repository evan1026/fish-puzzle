import itertools
from math import factorial
import re
import copy
from joblib import Parallel, delayed

PIECE_FILE_PATH = "pieces.txt"
pieces = [] # will be a list of lists of configurations for each piece
regex = r'^(\s*)(((\w)1(?:\4)2|(\w)2(?:\5)1|\w1|\w2)($|\s+))*$'
pattern = re.compile(regex)
blank_board = [["  " for x in range(3*3)] for x in range(3*3)]
blank_piece = [["  " for x in range(3)] for x in range(3)]

def rotate_piece(piece, rot):
    rot = rot % 4
    new_piece = copy.deepcopy(piece)
    if rot == 1:
        new_piece[0][1] = piece[1][0]
        new_piece[1][0] = piece[2][1]
        new_piece[2][1] = piece[1][2]
        new_piece[1][2] = piece[0][1]
    elif rot == 2:
        new_piece[0][1] = piece[2][1]
        new_piece[1][0] = piece[1][2]
        new_piece[2][1] = piece[0][1]
        new_piece[1][2] = piece[1][0]
    elif rot == 3:
        new_piece[0][1] = piece[1][2]
        new_piece[1][0] = piece[0][1]
        new_piece[2][1] = piece[1][0]
        new_piece[1][2] = piece[2][1]
    elif rot == 0:
        new_piece = copy.deepcopy(piece)
    return new_piece

def print_board(board):
    for i in range(9):
        print(get_row_string(board, i))

def get_column_string(board, i):
    return ''.join([column[i] for column in board])

def get_row_string(board, i):
    return ''.join(board[i])

def is_board_valid(board, pattern, rows, cols):
    if (rows is None or cols is None):
        for i in range(3*3):
            if not pattern.match(get_row_string(board, i)):
                return False
            if not pattern.match(get_column_string(board,i)):
                return False
    else:
        for i in rows:
            if not pattern.match(get_row_string(board, i)):
                return False
        for i in cols:
            if not pattern.match(get_column_string(board,i)):
                return False
    return True

def make_board_from_piece_list(piece_list):
    new_board = [["  " for x in range(3*3)] for x in range(3*3)]
    for i in range(9):
        x_off = int(i/3) * 3
        y_off = (i % 3) * 3
        new_board[x_off + 1][y_off + 0] = piece_list[i][1][0]
        new_board[x_off + 0][y_off + 1] = piece_list[i][0][1]
        new_board[x_off + 2][y_off + 1] = piece_list[i][2][1]
        new_board[x_off + 1][y_off + 2] = piece_list[i][1][2]
    
    return new_board

def make_and_test_board(piece_list):
    new_board = [["  " for x in range(3*3)] for x in range(3*3)]
    for i in range(9):
        x_off = int(i/3) * 3
        y_off = (i % 3) * 3
        new_board[x_off + 1][y_off + 0] = piece_list[i][1][0]
        new_board[x_off + 0][y_off + 1] = piece_list[i][0][1]
        new_board[x_off + 2][y_off + 1] = piece_list[i][2][1]
        new_board[x_off + 1][y_off + 2] = piece_list[i][1][2]
        
        if i > 1 and not is_board_valid(new_board, pattern, [x_off + 0, x_off + 1, x_off + 2], [y_off + 0, y_off + 1, y_off + 2]):
            return None
    
    return new_board

def generate_rotations_for_perm(perm):
    rotations = []
    for piece in perm:
        rotations.append([rotate_piece(piece, i) for i in range(4)])

    return itertools.product(*rotations)

def get_valid_boards_from_perm(perm):
    valid_boards = []
    for piece_list in generate_rotations_for_perm(perm):
        board = make_and_test_board(piece_list)
        if (board is not None):
            valid_boards.append(board)
    return valid_boards

with open(PIECE_FILE_PATH, 'r') as file:
    for line in file:
        line = line.strip()
        print(line)
        piece = copy.deepcopy(blank_piece)
        elems = line.split(" ")
        print(elems)
        piece[0][1] = elems[0]
        piece[1][2] = elems[1]
        piece[2][1] = elems[2]
        piece[1][0] = elems[3]
        pieces.append(piece)

for piece in pieces:
    print(piece)

solns_tried = 0

if __name__ == '__main__':
    total_solns = factorial(9) * pow(4,9)

    print("About to try {} solutions in {} tasks!".format(total_solns, factorial(9)))

    if False:
        perms = itertools.permutations(pieces)
        perm = next(perms)
        print("----------------------")
        print(perm)
        print("----------------------")
        piece_list = next(generate_rotations_for_perm(perm))
        print(piece_list)
        print("----------------------")
        board = make_board_from_piece_list(piece_list)
        print(board)
        print("----------------------")
        print(is_board_valid(board, pattern, [i for i in range(9)], [i for i in range(9)]))
        print("----------------------")
        boards = get_valid_boards_from_perm(perm)
        print(len(boards))
        print("----------------------")
        print_board(boards[0])

    if True:
        results = Parallel(n_jobs=-1, verbose=10)(delayed(get_valid_boards_from_perm)(perm) for perm in itertools.permutations(pieces))
        filtered_results = list(filter(lambda l: len(l) > 0, results))
        print(filtered_results)
    
    if False:
        i = 0
        for perm in itertools.permutations(pieces):
            i += 1
            print(get_valid_boards_from_perm(perm))
            if i == 1:
                break
