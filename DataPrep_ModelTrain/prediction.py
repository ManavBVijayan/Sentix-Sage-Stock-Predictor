import numpy as np


def prediction(next_five_days_close_prices,scaler):
    # Get the scaled predictions for the next five days
    next_n_days_exact = []  # List to store the exact values for the next five days

    # Loop through each predicted scaled value and inverse transform it
    for pred_scaled in next_five_days_close_prices:
        # Create a numpy array with the predicted scaled value and zeros for other features
        pred_scaled_array = np.array([[pred_scaled, 0, 0, 0, 0, 0]])
        # Inverse transform the scaled value to its exact value
        pred_exact = scaler.inverse_transform(pred_scaled_array)[0, 0]
        # Append the exact value to the list
        next_n_days_exact.append(pred_exact)
    return next_n_days_exact
