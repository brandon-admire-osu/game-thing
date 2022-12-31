from ClassesAndObjects import *
from raw_input_parser import *

# Set sheet id as enviroment variable.
INTERFACE_ID = os.environ.get('INTERFACE')

if __name__ == "__main__":
    main_board = Map_Graph()
    main_board.initialize_board("./map_small.json")

    # Set up radiant home base
    main_board.nodes["W20"].owner = 1
    main_board.nodes["W20"].max_cap = 15
    main_board.radiant = main_board.nodes["W20"]

    # Set up dire home base
    main_board.nodes["E20"].owner = -1
    main_board.nodes["E20"].max_cap = 15
    main_board.radiant = main_board.nodes["E20"]

    main_board.build_unit_list(get_info(get_ids(INTERFACE_ID),INTERFACE_ID),get_unit_lib(INTERFACE_ID))

    # print(main_board.units)

    main_board.display_board()

