import gurobipy as gp
from gurobipy import GRB
# Create a Model instance
m = gp.Model()
# Add variables
X1 = m.addVar(vtype=GRB.CONTINUOUS, name="X1")
X2 = m.addVar(vtype=GRB.CONTINUOUS, name="X2")
X3 = m.addVar(vtype=GRB.CONTINUOUS, name="X3")
X4 = m.addVar(vtype=GRB.CONTINUOUS, name="X4")
# Providing the coefficients and the sense of the objective function
m.setObjective(2*X1 + X2 + 6*X3 - 4 * X4, GRB.MAXIMIZE)
# Adding the 3 constraints
c1 = m.addConstr(X1 + 2*X2 + 4*X3 - X4 <= 6)
c2 = m.addConstr(2*X1 + 3*X2 - 1*X3 + X4 <= 12)
c3 = m.addConstr(X1 + X3 + X4 <= 6)
# Solving the model
m.optimize()
m.printAttr('X') #This prints the non-zero solutions found
