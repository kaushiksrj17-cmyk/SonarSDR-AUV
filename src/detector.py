# src/detector.py
import numpy as np

def cfar_detect(signal, guard_cells=8, training_cells=24, scale=4.5):
    """1D CA-CFAR detector."""
    magnitude = np.abs(signal)
    detections = []

    start = training_cells + guard_cells
    end = len(magnitude) - training_cells - guard_cells

    for i in range(start, end):
        left = magnitude[i - guard_cells - training_cells : i - guard_cells]
        right = magnitude[i + guard_cells + 1 : i + guard_cells + training_cells + 1]
        training = np.concatenate([left, right])

        noise_estimate = np.mean(training) + 1e-12
        threshold = scale * noise_estimate

        if magnitude[i] > threshold:
            detections.append({
                "index": i,
                "strength": float(magnitude[i]),
                "threshold": float(threshold)
            })

    if not detections:
        return None
    return max(detections, key=lambda x: x["strength"])

def cfar_2d_detect(rd_matrix, guard_r=2, train_r=4, guard_d=1, train_d=2, scale=5.0):
    """2D Cell-Averaging CFAR for Range-Doppler Maps."""
    rows, cols = rd_matrix.shape
    detections = []

    for r in range(train_d + guard_d, rows - (train_d + guard_d)):
        for c in range(train_r + guard_r, cols - (train_r + guard_r)):
            cut = rd_matrix[r, c]

            sub_matrix = rd_matrix[
                r - (train_d + guard_d) : r + train_d + guard_d + 1,
                c - (train_r + guard_r) : c + train_r + guard_r + 1
            ]

            guard_matrix = rd_matrix[
                r - guard_d : r + guard_d + 1,
                c - guard_r : c + guard_r + 1
            ]

            sum_all = np.sum(sub_matrix)
            sum_guard = np.sum(guard_matrix)
            num_training = sub_matrix.size - guard_matrix.size

            noise_floor = (sum_all - sum_guard) / max(num_training, 1)
            threshold = noise_floor * scale

            if cut > threshold:
                detections.append({
                    "doppler_idx": r,
                    "range_idx": c,
                    "strength": float(cut),
                    "threshold": float(threshold)
                })

    if not detections:
        return None
    return max(detections, key=lambda x: x["strength"])