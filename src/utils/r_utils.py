import numpy as np


###         UTILS


def matmul(f, s):
    dim = f.shape[1]
    rows_s = s.shape[0]
    if dim != rows_s:
        raise Exception("not matching dims")

    mat = [[] for x in range(dim)]

    for i in range(dim):
        for j in range(dim):
            mat[i].append(f[i, :].dot(s[:, j]))

    return np.array(mat)


def eurlerComplex(phi, A=1):
    return A * (np.cos(phi) + np.sin(phi) * 1j)


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ todo understand if to make it class method


def rotation_cost_calc(gate, placement):
    ## CALCULATES COST OF THE ROTATION GIVEN IN TERMS OF LOGIC INDEXES

    source = gate.original_lev_a
    target = gate.original_lev_b

    gate_cost = gate.cost

    if placement.is_irnode(source) or placement.is_irnode(target):
        SP_PENALTY = (
            min(
                placement.distance_nodes(placement._1stInode, source),
                placement.distance_nodes(placement._1stInode, target),
            )
            + 1
        )
        print(SP_PENALTY)
        # print(placement.distance_nodes(placement._1stInode, source), placement.distance_nodes(placement._1stInode, target) )
        # print(source, target)
        theta_on_units = gate.theta / np.pi
        # gate_cost = gate_cost - (( 1*abs(np.mod(abs(theta_on_units)+0.25, 0.5) - 0.25) )*10.0e-04)
        gate_cost = (
            SP_PENALTY
            * (
                4 * abs(theta_on_units)
                + abs(np.mod(abs(theta_on_units) + 0.25, 0.5) - 0.25)
            )
            * 1e-04
        )

    return gate_cost


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
