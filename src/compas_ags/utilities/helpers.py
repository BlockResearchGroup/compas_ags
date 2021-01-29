import numpy as np

__all__ = [
    'get_independent_stress',
    'check_solutions',
    'rref'
]

from compas_ags.exceptions import SolutionError

def rref(A, tol=1e-7):
    pcolpos = []
    m, n = A.shape
    if tol is None:
        tol = np.max(A) * np.finfo(float).eps * np.linalg.norm(A, ord=np.inf)

    i = 0
    j = 0
    while i < m and j < n:
        p = np.max(abs(A[i:m, j]))

        if p <= tol:
            A[:, j] = 0.0  # Clear the column
            j = j + 1
        else:
            # remember column index..

            # Find row of p
            for l, s in enumerate(abs(A[i:m, j])):
                if s == p:
                    k = l + i
            # Swap i:th and k:th rows
            A[[i, k], :] = A[[k, i], :]

            # Divide the pivot row by the pivot element
            A[i, j:n] = A[i, j:n] / A[i, j]

            # Subtract multiples of the pivot row from all other rows
            for k in range(i + 1, m):
                A[k, j:n] = A[k, j:n] - A[k, j] * A[i, j:n]

            pcolpos.append((i, j))
            i += 1
            j += 1
    return A, pcolpos

def get_independent_stress(A):
    # Prescribe dof
    from copy import deepcopy
    B = rref(deepcopy(A))
    pivot_edges = []

    for p in B[1]:
        pivot_edges.append(p[1])

    nr_independent_edges = np.shape(
        A)[1] - np.linalg.matrix_rank(A, tol=1e-10)
    independent_dofs = list(range(nr_independent_edges))

    independent_dofs = list(range(A.shape[1]))
    independent_dofs = set(independent_dofs) - set(pivot_edges)
    independent_dofs = list(independent_dofs)

    # Build list for freeDofs and remove prescribed dofs
    # List all dofs = number columns in A
    dependent_dofs = list(range(np.shape(A)[1]))
    [dependent_dofs.remove(dof) for dof in independent_dofs]

    return nr_independent_edges, independent_dofs, dependent_dofs

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
