import gc
import glob
import time

from src.decomposition.Adaptive_decomposition import *
from src.decomposition.QR_decomp import *
from src.evaluation.Clifford_Generator import Clifford_Generator
from src.evaluation.Evaluation_Graphs import *
from src.evaluation.Pauli import H, S, X
from src.evaluation.Verifier import Verifier

path_data = "/home/k3vn/Documents/Compiler/binq/data/"

# GENERATE LL CLIFFORD BEFORE TESTING
# Clifford_Generator.generate_all_3_5_7(path)

################################################

# CHOICE OF GRAPH FOR TESTING
dimension = 5
graph_combo = "g5_3"
graph_to_use = graph_5_3
nodes_to_use = nodes_5_3
nmap_to_use = nmap5_3
################################################


# GOES IN DATA FOLDER OF PROJECT AND PICKS UP MATRICES
files_to_read = glob.glob(path_data + "dim" + str(dimension) + "/*.csv")

for file in files_to_read:

    IDbin = [int(i) for i in file.split() if i.isdigit() and (i == '0' or i == '1')]
    IDbin = " ".join(str(x) for x in IDbin)

    print("####################################")
    print(IDbin)  # 1 STANDS FOR H 0 FOR S
    print("####################################")

    matrix_to_analyze = Clifford_Generator.load_from_csv(file)

    ##########################################################
    H1 = H(dimension)
    S1 = S(dimension)
    X1 = X(dimension)
    #########################################################

    operation = Custom_Unitary(matrix_to_analyze, dimension)
    # operation = X1
    #############################################################

    #                        EXECUTION

    #############################################################
    QR = QR_decomp(operation, graph_to_use)

    startqr = time.time()
    decomp, algorithmic_cost, total_cost = QR.execute()

    endqr = time.time()

    ###############################################################
    Adaptive = Adaptive_decomposition(operation, graph_to_use, (1.1 * algorithmic_cost, 1.1 * total_cost), dimension)

    start = time.time()
    matrices_decomposed, best_cost, final_graph = Adaptive.execute()
    end = time.time()
    ###################################################################

    print("QR elapsed time")
    QR_time = endqr - startqr
    print(QR_time, "\n")

    print("Adaptive elapsed time")
    Adaptive_time = end - start
    print(Adaptive_time, "\n")

    ###############################################################################################
    print("COST QR,   ", (algorithmic_cost, total_cost))
    print("BEST COST ADA,   ", best_cost, "\n")

    ###############################################################################################
    numRzQR = sum(isinstance(x, Rz) for x in decomp)
    numRzADA = sum(isinstance(x, Rz) for x in matrices_decomposed)
    print("numRz QR   ", numRzQR)
    print("numRz ADA  ", numRzADA, "\n")
    ################################################################################################

    ########  VERIFICATION  #########################

    final_map = final_graph.lpmap

    V1 = Verifier(decomp, operation, nodes_to_use, nmap_to_use, nmap_to_use, dimension)
    V2 = Verifier(matrices_decomposed, operation, nodes_to_use, nmap_to_use, final_map, dimension)
    V1r = V1.verify()
    V2r = V2.verify()

    print(V1r)
    print(V2r)

    if (V1r == False or V2r == False):
        raise Exception

    ### save results
    field_names = ['ID', 'graphcombo', 'timeQR', 'timeADA', 'algoCostQR', 'algoCostADA', 'decoCostQR', 'decoCostADA',
                   'numRzQR', 'numRzADA', 'succQR', 'succADA']

    # Dictionary
    ada_algo = best_cost[0]
    ada_cost = best_cost[1]
    record = {'ID': IDbin, 'graphcombo': graph_combo, 'timeQR': QR_time, 'timeADA': Adaptive_time,
              'algoCostQR': algorithmic_cost, 'algoCostADA': ada_algo, 'decoCostQR': total_cost,
              'decoCostADA': ada_cost, 'numRzQR': numRzQR, 'numRzADA': numRzADA, 'succQR': V1r, 'succADA': V2r}

    # with open("/evaluation_2/" + "dim" + str(dimension) + "/" + "eval" + str(graph_combo) + ".csv", 'a') as f_object:

    #    dictwriter_object = DictWriter(f_object, fieldnames=field_names)

    # Pass the dictionary as an argument to the Writerow()
    #    dictwriter_object.writerow(record)

    # Close the file object
    #    f_object.close()

    gc.collect()
##############################
