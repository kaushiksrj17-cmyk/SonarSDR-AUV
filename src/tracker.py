import numpy as np

class AlphaBetaTracker:
    """Alpha-Beta filter for target range and velocity tracking."""
    
    def __init__(self, alpha=0.85, beta=0.005, dt=0.1):
        self.alpha = alpha
        self.beta = beta
        self.dt = dt
        self.x_est = 0.0  # Estimated position/range (m)
        self.v_est = 0.0  # Estimated velocity (m/s)
        self.initialized = False

    def reset(self):
        """Resets the internal tracker states."""
        self.x_est = 0.0
        self.v_est = 0.0
        self.initialized = False

    def update(self, z_measured: float):
        """Updates range and velocity estimate with a new range measurement."""
        if not self.initialized:
            self.x_est = z_measured
            self.v_est = 0.0
            self.initialized = True
            return self.x_est, self.v_est

        # Prediction step
        x_pred = self.x_est + (self.v_est * self.dt)
        v_pred = self.v_est

        # Residual calculation
        residual = z_measured - x_pred

        # Correction step
        self.x_est = x_pred + (self.alpha * residual)
        self.v_est = v_pred + ((self.beta / self.dt) * residual)

        return self.x_est, self.v_est