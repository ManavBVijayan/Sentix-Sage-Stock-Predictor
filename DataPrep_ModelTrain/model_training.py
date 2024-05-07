import numpy as np
import pandas as pd
from keras import Input
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping


def train_model(data):
    # Define the function for preprocessing data
    def preprocess_data(data, features, sequence_length=5, seed=42):
        data = data[features]

        # Normalize the data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        np.random.seed(seed)

        # Create sequences of data for input to LSTM
        def create_sequences(data, seq_length):
            X = []
            y = []
            for i in range(len(data) - seq_length - 5):
                X.append(data[i:i + seq_length])
                y.append(data[i + seq_length:i + seq_length + 5, -1])
            return np.array(X), np.array(y)

        # Create sequences
        X, y = create_sequences(scaled_data, sequence_length)

        # Split data into training and testing sets
        split = int(0.8 * len(X))
        X_train = X[:split]
        X_test = X[split:]
        y_train = y[:split]
        y_test = y[split:]

        return X_train, X_test, y_train, y_test, scaler

    # Define the function for building the LSTM model
    def build_bidirectional_lstm_model(input_shape):
        model = Sequential()
        model.add(Input(shape=input_shape))
        model.add(Bidirectional(LSTM(256, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(128, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(128)))
        model.add(Dense(5, activation='relu'))
        return model

    # Define the function for training and validating the model
    def train_validate_model(X_train, X_test, y_train, y_test, optimizer='adam', loss='mean_squared_error'):
        model = build_bidirectional_lstm_model(input_shape=(X_train.shape[1], X_train.shape[2]))
        model.compile(optimizer=optimizer, loss=loss)

        seed = 42
        np.random.seed(seed)

        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

        history = model.fit(X_train, y_train, epochs=200, batch_size=64, validation_data=(X_test, y_test),
                            verbose=0, callbacks=[early_stopping])
        predictions = model.predict(X_test)
        next_five_days_close_prices = model.predict(X_test)[-1]
        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        return history, mse, r2, next_five_days_close_prices

    # Define the features to be used in training
    features = ['open_price', 'high_price', 'low_price', 'sentiment_score', 'relevance_score', 'close_price']

    # Preprocess the data
    X_train, X_test, y_train, y_test, scaler = preprocess_data(data, features)

    # Train and validate the model
    history, mse, r2, next_five_days_close_prices = train_validate_model(X_train, X_test, y_train, y_test,
                                                                         optimizer='adam', loss='mean_squared_error')
    return mse, r2, next_five_days_close_prices, scaler
