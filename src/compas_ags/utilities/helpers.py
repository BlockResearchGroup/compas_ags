import numpy as np
from compas_ags.exceptions import SolutionError


__all__ = [
    'check_solutions',
]


def check_solutions(A, rhs, eps=1e-7):
    """
    Compares the rank of the matrix A to the rank of the augmentet matrix [A rhs].
    """
    rank_j = np.linalg.matrix_rank(A, tol=eps)
    rank_aug = np.linalg.matrix_rank(
        np.hstack([A, rhs]), tol=eps)

    if rank_j < rank_aug:
        print("Rank of matrix: " + str(rank_j))
        print("Rank of augmented matrix: " + str(rank_aug))
        raise SolutionError('ERROR: No solutions!!!')
