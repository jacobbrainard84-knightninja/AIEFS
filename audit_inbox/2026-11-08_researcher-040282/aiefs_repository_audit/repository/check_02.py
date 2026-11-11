import numpy as np

path = (
    "aief_1_4_frozen_driver_cocycle/"
    "frozen_cocycle_matrices.npz"
)

with np.load(path, allow_pickle=False) as data:
    matrices = np.asarray(data["K3_matrix_sequence"], dtype=float)

v = np.array([1.0, -1.0, -1.0]) / np.sqrt(3.0)
u = np.sqrt(3.0) / 2.0 * np.array([1.0, 0.0, -1.0])

for time_value in (200.0, 250.0, 319.99):
    step = int(round(time_value / 0.01))
    K = matrices[step]

    lam = float(u @ K @ v)

    right_residual = (
        np.linalg.norm(K @ v - lam * v)
        / np.linalg.norm(K @ v)
    )

    left_residual = (
        np.linalg.norm(K.T @ u - lam * u)
        / np.linalg.norm(K.T @ u)
    )

    d = float(np.mean(np.diag(K)))
    off_diagonal = np.array([K[0, 2], K[1, 0], K[2, 0]])
    a = float(-np.mean(off_diagonal))

    K_model = np.array([
        [d, 0.0, -a],
        [-a, d, 0.0],
        [-a, 0.0, d],
    ])

    structure_residual = (
        np.linalg.norm(K - K_model)
        / np.linalg.norm(K)
    )

    print(
        time_value,
        "lambda =", lam,
        "right =", right_residual,
        "left =", left_residual,
        "structure =", structure_residual,
    )
