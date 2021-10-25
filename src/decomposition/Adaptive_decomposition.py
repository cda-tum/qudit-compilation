
from binq.src.QC.Rotations import *
from binq.src.decomposition.tree_struct import N_ary_Tree

from binq.src.utils.costs_utils import *
from binq.src.utils.r_utils import *


class Adaptive_decomposition:


    def __init__(self, gate, graph_orig, cost_limit=0):
        U = gate.matrix
        graph = graph_orig
        cost_limit = cost_limit

        TREE = N_ary_Tree()

    def execute(self):
        self.TREE.add(0, custom_Unitary(np.identity(3, dtype='complex'), 3), self.U, self.graph, 0, self.cost_limit, [])

        self.BFS(self.TREE.root)
        decomp, best_cost = self.TREE.retrieve_decomposition(self.TREE.root)
        matrices_decomposed = self.Z_extraction(decomp)

        tree_print = self.TREE.print_tree(self.TREE.root, "TREE: ")
        print(tree_print)

        return matrices_decomposed

    def Z_extraction(self, decomposition):
        print("Z EXTRACTION INITIATED")
        ###########################################################################################################
        matrices = []

        for d in decomposition[1:]: #exclude the identity matrix coming from the root of the tree of solutions which is just for correctness
            matrices.append(d.rotation)


        U_ = decomposition[-1].U_of_level #take U of last elaboration which should be the diagonal matrix found
        ###########################################################################################################

        # check if close to diagonal
        Ucopy = U_.copy()

        # is the diagonal noisy?
        valid_diag = (abs(np.diag(Ucopy)) > 1.0e-4).sum()  # > 1.0e-4
        print("valid: " + str(valid_diag))

        # are the non diagonal entries zeroed-out
        filtered_Ucopy = abs(Ucopy) > 1.0e-4
        np.fill_diagonal(filtered_Ucopy, 0)

        not_diag = filtered_Ucopy.sum(axis=0).sum()
        print("not_diag: " + str(not_diag))
        #---------------------------------------------------------------------------------------------------------------------

        if ( not_diag or not valid_diag):  # if is diagonal enough then somehow signal end of algorithm
            raise Exception('Matrix isnt close to diagonal!')
        #@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=#@=
        else:
            diag_U = np.diag(U_)
            dimension = U_.shape[0]      # TODO eay fix

            for i in range(dimension):   #TODO take care of this variable because imported globally

                if( abs(np.mod(np.angle(diag_U[i]),1.0e-13))> 1.0e-4):
                    print("theta rotation :  ", np.angle(diag_U[i]))

                    print("U before phase rotation")
                    print(U_.round(4))
                    phase_gate = Rz( np.angle(diag_U[i]), i, dimension)

                    U_ = matmul( phase_gate.matrix, U_)

                    print('---')
                    print("U after phase rotation")
                    print(U_.round(4))

                    print('@@@@@@@')
                    print(phase_gate.matrix.round(4))
                    print('@@@@@@@')
                    print()
                    matrices.append( phase_gate )


            return matrices


    # GLOBAL TREE == U, cost_max,  current_cost
    # INITIAL PLACEMENT

    def BFS(self, current_root,   level = 0):

        #######################

        # check if close to diagonal
        Ucopy = current_root.U_of_level.copy()
        current_placement = current_root.graph


        #is the diagonal noisy?
        valid_diag = (abs(np.diag(Ucopy))> 1.0e-4).sum() #> 1.0e-4
        print("valid: "+ str(valid_diag))

        # are the non diagonal entries zeroed-out
        filtered_Ucopy = abs(Ucopy) > 1.0e-4
        np.fill_diagonal(filtered_Ucopy, 0)

        not_diag = filtered_Ucopy.sum(axis=0).sum()
        print("not_diag: "+ str(not_diag))
        ############################################

        if( (not not_diag) and valid_diag ):# if is diagonal enough then somehow signal end of algorithm
            print("condition 2")

            print(current_root.U_of_level)
            print(current_root.key)

            print("\n\n ARRIVATO\n\n")

            current_root.finished = True

            return
            # SALVO UN FLAG SUL FIGLIO


        #----------------------------------


        ## CHECKING FOR BEST CHOICE ON CERTAIN STEP
        U_ = current_root.U_of_level

        dimension = U_.shape[0]
        print("dimension is "+str(dimension))

        print("checking level")
        for c in range(dimension):

            for r in range(dimension):

                for r2 in range(r, dimension):

                    if( abs(U_[r,c])>1.0e-8 and abs(U_[r2,c])>1.0e-4 and r >= c and r2 > r):


                        print("-------------------------------------------------------------------------")
                        print(' r is '+str(r))
                        print(' r2 is '+str(r2))
                        print(' c is '+str(c))

                        theta = 2 * np.arctan( abs(U_[r2,c]/U_[r,c]))
                        phi = -(np.angle(U_[r,c]) - np.angle(U_[r2,c]))

                        print("theta  : "+str(theta))
                        print("phi  : "+str(phi))

                        rotation_involved = R(theta, phi,r, r2, dimension)

                        U_temp = matmul(  rotation_involved.matrix, U_ )
                        U_temp = U_temp.round(12)


                        non_zeros = np.count_nonzero(abs(U_temp)>1.0e-4)
                        print("number of non-zeros  :"+ str(non_zeros))


                        estimated_cost, pi_pulses_routing, new_placement  = cost_calculator(rotation_involved, current_placement, non_zeros)
                        print("estimated_cost   :"+str(estimated_cost))
                        print("-------------------------------------------------------------------------")

                        next_step_cost = (estimated_cost + current_root.current_cost)
                        branch_condition = current_root.max_cost - next_step_cost

                        if(  branch_condition > 0 or abs(branch_condition) < 1.0e-12): #if cost is better can be only candidate otherwise try them all
                            #seed(current_root.key)

                            new_key = current_root.key + (current_root.size + 1)
                            print(" LA NEW KEY IS : " + str(new_key))

                            #todo copy and modify placement
                            # new_placement = # method calculates what is the rotatino to be made and callculates the swap that has to be made, or the new conformation
                            # pi_pulses = # method returns a lit of pi pulses represemtative of the new conformation

                            current_root.add(new_key, rotation_involved, U_temp, next_step_cost, new_placement, current_root.max_cost, pi_pulses_routing)



        print("next level")
        #===================================================================================
        ## FOR LOOP


        for child in current_root.children:
            self.BFS(child, level+1)
        #===================================================================================

        return


