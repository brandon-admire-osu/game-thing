from ClassesAndObjects import *

if __name__ == "__main__":
    main_board = Map_Graph()
    main_board.initialize_grid(5)
    main_board.nodes[(0,0)].owner = 1
    main_board.nodes[(0,0)].max_cap = 15
    main_board.nodes[(4,4)].owner = -1
    main_board.nodes[(4,4)].max_cap = 15

    for team in [-1,1]:
        for tier in [5,4,3,2,1]:
            if team > 0:
                _ = Unit(tier,team)
                _.invade(main_board.nodes[(0,0)])
            else:
                _ = Unit(tier,team)
                _.invade(main_board.nodes[(4,4)])
    
    main_board.resolve_combat()

    

    main_board.display_board()

    # for team in [-1,1]:
    #     if team > 0:
    #         for unit in main_board.nodes[(0,0)].occupants:
    #             print(unit)
    #     else:
    #         for unit in main_board.nodes[(4,4)].occupants:
    #             print(unit)
