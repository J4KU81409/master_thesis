import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import matplotlib.pyplot as plt


np.random.seed(42)  # For reproducibility

# True parameters
A_true = 0.5
B_true = 0.9
C_true = 1
D_true = 2
n_timesteps = 100

# Generate latent states and observations
x = np.zeros(n_timesteps)
y = np.zeros(n_timesteps)
x[0] = np.random.normal()

for t in range(1, n_timesteps):
    x[t] = A_true + B_true * x[t-1] + C_true * np.random.normal()
y = x + D_true * np.random.normal(size=n_timesteps)

# Define initial Kalman Filter with placeholders
kf = KalmanFilter(
    n_dim_obs=1,
    n_dim_state=1, 
     em_vars=['transition_matrices', 'transition_offsets', 
                    'transition_covariance', 'observation_covariance']
)

# Let EM estimate the parameters
kf = kf.em(y, n_iter=50)

# Use the fitted model to filter the data
(filtered_state_means, _) = kf.filter(y)

# Print learned parameters
print("Estimated transition offset (A):", kf.transition_offsets)
print("Estimated transition matrix (B):", kf.transition_matrices)
print("Estimated transition noise (C):", np.sqrt(kf.transition_covariance))
print("Estimated observation noise (D):", np.sqrt(kf.observation_covariance))



# Plot the results
plt.figure(figsize=(12, 6))
plt.plot(x, label="True state (x)", linewidth=2)
plt.plot(y, label="Observed (y)", alpha=0.5)
plt.plot(filtered_state_means, label="Filtered state (Kalman estimate)", linestyle='--')
plt.title("Kalman Filter Estimate vs True State")
plt.xlabel("Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
