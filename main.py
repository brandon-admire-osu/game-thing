from ClassesAndObjects import *

if __name__ == "__main__":
    main_board = Map_Graph()
    main_board.initialize_board("./map_small.json")
    main_board.visualize_board()

    main_board.nodes["W20"].owner = 1
    main_board.nodes["W20"].max_cap = 15
    main_board.nodes["E20"].owner = -1
    main_board.nodes["E20"].max_cap = 15

    main_board.display_board()

