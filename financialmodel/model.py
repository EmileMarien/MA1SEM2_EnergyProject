import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gridcost import grid_cost




cost_grid=grid_cost()
batterycost=500

NPV=cost_grid+batterycost
    



