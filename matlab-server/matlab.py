import matlab.engine
import random

E = matlab.double([
    [-1, -1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, -1, -1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, -1, -1, -1, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, -1, -1, 0, 0, 1],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, -1, -1, -1]
])

X = matlab.double([
    [1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0],
    [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1]
])

C_edge = matlab.double([
    [6, 1, 6, 6, 6, 1, 1, 1, 1, 1, 1, 1],
    [6, 1, 6, 6, 6, 1, 1, 1, 1, 1, 1, 1]
])

for i in range(len(C_edge)):
    for j in range(len(C_edge[i])):
        C_edge[i][j] += random.random() * 1e-3

print(C_edge)
edge_time_vec = matlab.double([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

start_vec = matlab.double([1, 1])
end_vec = matlab.double([1, 1])

distrib_vec = matlab.double([0, 4, 3, 4, 3])
capacity_vec = matlab.double([10, 10])

t_start_vec = matlab.double([0, 0, 0, 0, 0])
t_end_vec = matlab.double([10, 10, 10, 10, 10])
print("Build input matrices")
eng = matlab.engine.start_matlab()
R = eng.vrptw_solve(E, C_edge, edge_time_vec, start_vec, end_vec, distrib_vec, capacity_vec, t_start_vec, t_end_vec)
print(R)
eng.quit()