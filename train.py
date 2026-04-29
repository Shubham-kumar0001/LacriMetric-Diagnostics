import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from PIL import Image

def load_images_from_dir(directory, label, target_size=(64, 64)):
    """Load images directly from a directory and return arrays."""
    images = []
    labels = []
    if not os.path.exists(directory):
        return np.array([]), np.array([])
    
    for fname in sorted(os.listdir(directory)):
        fpath = os.path.join(directory, fname)
        try:
            img = Image.open(fpath).convert('RGB').resize(target_size)
            arr = np.array(img, dtype=np.float32) / 255.0
            images.append(arr)
            labels.append(label)
        except:
            continue
    
    return np.array(images), np.array(labels)

def build_model(input_shape=(64, 64, 3)):
    """
    Simplified CNN for tear film anomaly detection.
    Uses Global Average Pooling to reduce parameters and overfitting.
    """
    model = Sequential([
        # Block 1
        Conv2D(16, (3, 3), activation='relu', input_shape=input_shape, padding='same'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        
        # Block 2
        Conv2D(32, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        
        # Block 3
        Conv2D(64, (3, 3), activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        
        # Global Average Pooling instead of Flatten (reduces params massively)
        GlobalAveragePooling2D(),
        
        # Small classification head
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')  # 0 = Normal, 1 = Abnormal
    ])
    
    model.compile(
        loss='binary_crossentropy',
        optimizer=Adam(learning_rate=0.001),
        metrics=['accuracy']
    )
    return model

def train_pipeline():
    print("=" * 60)
    print("  LacriMetric CNN Training Pipeline")
    print("  Tear Film Anomaly Detection Model")
    print("=" * 60)
    
    base_dir = "dataset"
    
    # Load data directly (more reliable than generators for small datasets)
    print("\nLoading training data...")
    train_normal, train_normal_labels = load_images_from_dir(
        os.path.join(base_dir, "train", "normal"), label=0
    )
    train_abnormal, train_abnormal_labels = load_images_from_dir(
        os.path.join(base_dir, "train", "abnormal"), label=1
    )
    
    print("Loading test data...")
    test_normal, test_normal_labels = load_images_from_dir(
        os.path.join(base_dir, "test", "normal"), label=0
    )
    test_abnormal, test_abnormal_labels = load_images_from_dir(
        os.path.join(base_dir, "test", "abnormal"), label=1
    )
    
    # Combine
    X_train = np.concatenate([train_normal, train_abnormal], axis=0)
    y_train = np.concatenate([train_normal_labels, train_abnormal_labels], axis=0)
    X_test = np.concatenate([test_normal, test_abnormal], axis=0)
    y_test = np.concatenate([test_normal_labels, test_abnormal_labels], axis=0)
    
    # Shuffle training data
    indices = np.arange(len(X_train))
    np.random.shuffle(indices)
    X_train = X_train[indices]
    y_train = y_train[indices]
    
    print(f"\n  Train: {len(X_train)} images ({int(np.sum(y_train==0))} normal, {int(np.sum(y_train==1))} abnormal)")
    print(f"  Test:  {len(X_test)} images ({int(np.sum(y_test==0))} normal, {int(np.sum(y_test==1))} abnormal)")
    print(f"  Shape: {X_train.shape}, Range: [{X_train.min():.2f}, {X_train.max():.2f}]")
    print(f"  0 = Normal (smooth tear film)")
    print(f"  1 = Abnormal (irregular/dry tear film)")
    
    model = build_model()
    model.summary()
    
    # Early stopping
    early_stop = EarlyStopping(
        monitor='val_accuracy',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )
    
    print("\n" + "=" * 60)
    print("  Starting Model Training (30 epochs)")
    print("=" * 60)
    
    history = model.fit(
        X_train, y_train,
        epochs=30,
        batch_size=16,
        validation_split=0.2,
        callbacks=[early_stop],
        shuffle=True
    )
    
    model.save('model.h5')
    print("\n[OK] Model saved as model.h5")
    
    # Final evaluation on held-out test set
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"\nFinal Test Loss: {loss:.4f}")
    print(f"Final Test Accuracy: {accuracy:.4f}")
    
    # Test individual predictions
    print("\n--- Sample Predictions ---")
    for i in range(min(5, len(X_test))):
        pred = model.predict(X_test[i:i+1], verbose=0)[0][0]
        actual = "Abnormal" if y_test[i] == 1 else "Normal"
        predicted = "Abnormal" if pred > 0.5 else "Normal"
        status = "[OK]" if actual == predicted else "[WRONG]"
        print(f"  {status} Actual: {actual}, Predicted: {predicted} (prob: {pred:.4f})")
    
    # Print training summary
    best_val = max(history.history['val_accuracy'])
    print("\n" + "=" * 60)
    print("  Training Complete!")
    print(f"  Train Accuracy: {history.history['accuracy'][-1]:.4f}")
    print(f"  Val Accuracy:   {history.history['val_accuracy'][-1]:.4f}")
    print(f"  Best Val Accuracy: {best_val:.4f}")
    print(f"  Test Accuracy: {accuracy:.4f}")
    print(f"  Epochs trained: {len(history.history['accuracy'])}")
    print("=" * 60)

def predict_image(model_path, image_path):
    """Predict a single eye image."""
    print(f"\n--- Predicting: {image_path} ---")
    from tensorflow.keras.models import load_model
    
    if not os.path.exists(model_path):
        print(f"Error: Model {model_path} not found.")
        return
        
    model = load_model(model_path)
    
    img = Image.open(image_path).convert('RGB').resize((64, 64))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    prediction = model.predict(img_array, verbose=0)
    prob = prediction[0][0]
    
    if prob > 0.5:
        print(f"Result: ABNORMAL (probability: {prob:.4f})")
        return 1
    else:
        print(f"Result: NORMAL (probability: {prob:.4f})")
        return 0

if __name__ == "__main__":
    train_pipeline()
