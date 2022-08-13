import itertools
from math import factorial
import re
import copy
from joblib import Parallel, delayed

PIECE_FILE_PATH = "pieces.txt"
pieces = [] # will be a list of lists of configurations for each piece
regex = r'^( *)(((\w)1(?:\4)2|(\w)2(?:\5)1|\w1|\w2)($|\s))+$'
pattern = re.compile(regex)

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
    
    return new_piece


def get_column_string(board, i):
    return ''.join([column[i] for column in board])


def get_row_string(board, i):
    return ''.join(board[i])


def is_board_valid(board, pattern):
    for i in range(3*9):
        if not pattern.match(get_row_string(board, i)):
            return False
        if not pattern.match(get_column_string(board,i)):
            return False
    
    return True

def make_board_from_piece_list(piece_list):
    board = [[0 for x in range(3*3)] for x in range(3*3)]
    for i in range(9):
        x_off = int(i/3) * 3
        y_off = (i % 3) * 3
        board[x_off + 0][y_off + 0] = piece_list[i][0][0]
        board[x_off + 1][y_off + 0] = piece_list[i][1][0]
        board[x_off + 2][y_off + 0] = piece_list[i][2][0]
        board[x_off + 0][y_off + 1] = piece_list[i][0][1]
        board[x_off + 1][y_off + 1] = piece_list[i][1][1]
        board[x_off + 2][y_off + 1] = piece_list[i][2][1]
        board[x_off + 0][y_off + 2] = piece_list[i][0][2]
        board[x_off + 1][y_off + 2] = piece_list[i][1][2]
        board[x_off + 2][y_off + 2] = piece_list[i][2][2]
    
    return board

def generate_rotations_for_perm(perm):
    rotations = []
    for piece in perm:
        rotations.append([rotate_piece(piece, i) for i in range(4)])

    return itertools.product(*rotations)

def get_valid_boards_from_perm(perm):
    valid_boards = []
    for piece_list in generate_rotations_for_perm(perm):
        #solns_tried += 1
        board = make_board_from_piece_list(piece_list)
        if (is_board_valid(board, pattern)):
            valid_boards.append(board)
        #if (solns_tried % 10000 == 0):
        #    print(str((solns_tried / total_solns) * 100) + "% ...")
    return valid_boards

with open(PIECE_FILE_PATH, 'r') as file:
    for line in file:
        line = line.strip()
        print(line)
        piece = [[0 for x in range(3)] for x in range(3)]
        elems = line.split(" ")
        print(elems)
        piece[0][0] = " "
        piece[0][1] = elems[0]
        piece[0][2] = " "
        piece[1][0] = elems[1]
        piece[1][1] = " "
        piece[1][2] = elems[2]
        piece[2][0] = " "
        piece[2][1] = elems[3]
        piece[2][2] = " "
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
        print(is_board_valid(board, pattern))

    if True:
        Parallel(n_jobs=-1, verbose=10)(delayed(get_valid_boards_from_perm)(perm) for perm in itertools.permutations(pieces))
