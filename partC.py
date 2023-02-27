import gurobipy as gb
from gurobipy import GRB
import pandas as pd
import numpy as np
import sys

xl_file = pd.read_excel('berke.xlsx', index_col=None, na_values=['NA'], usecols="E:J")
productTable = xl_file[7:53].values.tolist()

# Parameters
Budget = xl_file[4:5].values.tolist()[0][1]
Distance_Limit = xl_file[63:64].values.tolist()[0][2]

for i in range(1, len(productTable)):
    productTable[i][4] = float(productTable[i][4][:-2])

p = np.zeros((45, 4), dtype='int')
A = np.zeros(45)
C = np.zeros(45)
S = np.zeros(45)
for i in range(0, len(productTable) - 1):
    t = 0
    if productTable[i + 1][5] == 'A':
        t = 0
    elif productTable[i + 1][5] == 'B':
        t = 1
    elif productTable[i + 1][5] == 'C':
        t = 2
    elif productTable[i + 1][5] == 'D':
        t = 3
    p[i][t] = 1
    A[i] = productTable[i + 1][4]
    C[i] = productTable[i + 1][2]
    S[i] = productTable[i + 1][3]
distanceTable = xl_file[55:61].values.tolist()
d = np.zeros((5, 5), dtype='int') #distances
D = xl_file[2:3].values.tolist()[0][1:5] #demands
for i in range(len(D)):
    D[i] = float(D[i][:-3])

for i in range(0, 5):
    for j in range(0, 5):
        d[i][j] = distanceTable[i + 1][j + 1]

# Create a Model instance
m = gb.Model()

################################################DECISION VARIABLES###################################
XVar = []
for i in range(45):
    XVar.append(m.addVar(vtype=GRB.INTEGER, name=("X" + str(i + 1))))

mij = []
for i in range(5):
    mij.append([])
    for j in range(5):
        mij[i].append(m.addVar(vtype=GRB.BINARY, name=("M" + str(i) + ',' + str(j))))

# Providing the coefficients and the sense of the objective function#############################OBJECTIVE FUNCTION
m.setObjective(
    gb.quicksum(S[i] * XVar[i] for i in range(45)) + (Budget - gb.quicksum(C[i] * XVar[i] for i in range(45))),
    GRB.MAXIMIZE)

#############################################SUCH THAT CONSTRAINTS##################################

# constraints for demands
c1 = m.addConstr(gb.quicksum([XVar[i] * A[i] for i in range(18)]) >= D[0])
c2 = m.addConstr(gb.quicksum([XVar[i] * A[i] for i in range(18, 29)]) >= D[1])
c3 = m.addConstr(gb.quicksum([XVar[i] * A[i] for i in range(29, 39)]) >= D[2])
c4 = m.addConstr(gb.quicksum([XVar[i] * A[i] for i in range(39, 45)]) >= D[3])

m.addConstr(gb.quicksum([XVar[i] * C[i] for i in range(45)]) <= Budget)

################################################################# TRAVEL CONSTRAINTS ###################################

m.addConstr((gb.quicksum(gb.quicksum(mij[i][j] * d[i][j] for i in range(5)) for j in range(5))) <= Distance_Limit)

# Σm0j = 1 j = {1,2,3,4} 
m.addConstr(gb.quicksum([mij[0][j] for j in range(1, 5)]) == 1)

# Σmi0 = 1 i={1,2,3,4} 
m.addConstr(gb.quicksum([mij[i][0] for i in range(1, 5)]) == 1)

# Σmij[i][k] (over i) = Σmij[k][j] (over j )  ensures that if a vehicle enters a node, it must leave the node.
for k in range(5):
    m.addConstr(gb.quicksum([mij[i][k] for i in range(5) if i != k]) == gb.quicksum([mij[k][j] for j in range(5) if j != k]))

# Σmij <= 1 (j=1..4), i ={1, 2, 3, 4} where i != j
for i in range(1,5):
    m.addConstr(gb.quicksum([mij[i][j] for j in range(1,5) if i != j]) <= 1)

for i in range(0,5):
    for j in range(0,5):
        if i != j:
            if i == 0 or j == 0:
                continue
            else:
                m.addConstr(mij[i][j] + mij[j][i] <= 1)


# (if (Σ (Xi * pij))  > 0, (i = 1..45), then ΣMkj = 1, (k = 1..4) ) where j = {1, 2, 3, 4}
# (if (Σ (Xi * pij))  = 0, (i = 1..45), then ΣMkj = 0, (k = 1..4) ) where j = {1, 2, 3, 4}

H = sys.maxsize # Assumably very large number
for j in range(4):
    m.addConstr(gb.quicksum([XVar[i] * p[i][j] for i in range(45)]) <= gb.quicksum([mij[k][j+1] for k in range(5) if k != j + 1])*H) 

partC = xl_file[68:69].values.tolist()[0][1]
ithProduct = int(partC[partC.find('=')+1:partC.find(',')])
jthProduct = int(partC[partC.rfind('=')+1:])

m.addConstr(XVar[ithProduct-1] <= XVar[jthProduct-1]*H)

################################################################SOLVER
# Solving the model
m.optimize()
m.printAttr('X')  # This prints the non-zero solutions found

