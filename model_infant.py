# -*- coding: utf-8 -*-
"""MODEL_INFANT.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fGG0krCcrabTydPAdOZEnlObY8qFjhBL

# MOUNT GOOGLE DRIVE
"""

from google.colab import drive
drive.mount('/content/drive')

"""# KODE MODEL"""

import numpy as np
import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize
import warnings
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, InputLayer
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

warnings.filterwarnings('ignore')

def add_noise(data, noise_factor=0.005):
    noise = np.random.randn(len(data))
    augmented_data = data + noise_factor * noise
    return augmented_data

def pitch_shift(data, sr, n_steps=2):
    """Apply pitch shift to the audio."""
    return librosa.effects.pitch_shift(data, sr=sr, n_steps=n_steps)


def time_stretch(data, rate=1.25):
    """Apply time stretch to the audio."""
    return librosa.effects.time_stretch(data, rate=rate)

def process_user_audio(audio_file, target_sample_rate=22050, fixed_length=66150):
    if not audio_file.endswith('.wav'):
        raise ValueError("Unsupported file format. Please provide WAV format.")
    y, sr = librosa.load(audio_file, sr=target_sample_rate)
    if len(y) < fixed_length:
        y = librosa.util.fix_length(y, size=fixed_length)
    return y, sr


def extract_features(audio_file, augment=False, n_mfcc=13, fixed_length=66150, augment_type=None):
    y, sr = process_user_audio(audio_file, fixed_length=fixed_length)  # Gunakan process_user_audio

    # Pilihan augmentasi
    if augment:
        if augment_type == 'noise':
            y = add_noise(y)
        elif augment_type == 'pitch_shift':
            y = pitch_shift(y, sr, n_steps=2)
        elif augment_type == 'time_stretch':
            y = time_stretch(y, rate=1.25)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)  # Extract MFCC with flexible n_mfcc
    mfcc = np.mean(mfcc, axis=1)  # Take the mean of each MFCC across time frames
    return mfcc


def visualize_audio_with_noise(audio_file, class_name, noise_factor=0.005, fixed_length=66150):
    y, sr = process_user_audio(audio_file, fixed_length=fixed_length)  # Gunakan process_user_audio
    y_noisy = add_noise(y, noise_factor=noise_factor)  # Add noise to the audio

    plt.figure(figsize=(15, 5))

    # Plot Original Audio and Noisy Audio stacked
    librosa.display.waveshow(y_noisy,color='blue', sr=sr, alpha=0.5, label="Noisy Audio")
    librosa.display.waveshow(y, sr=sr,color='orange', alpha=0.75, label="Original Audio")
    plt.title(f"Audio Visualization ({class_name})")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.tight_layout()
    plt.show()


def visualize_spectrogram(audio_file, class_name, fixed_length=66150):
    y, sr = process_user_audio(audio_file, fixed_length=fixed_length)  # Gunakan process_user_audio
    spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    log_spectrogram = librosa.power_to_db(spectrogram, ref=np.max)

    plt.figure(figsize=(15, 5))
    librosa.display.specshow(log_spectrogram, sr=sr, x_axis='time', y_axis='mel', cmap='coolwarm')
    plt.colorbar(format='%+2.0f dB')
    plt.title(f"Spectrogram ({class_name})")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.tight_layout()
    plt.show()

def visualize_audio_with_augmentation(audio_file, class_name, augment_type='pitch_shift', fixed_length=66150):
    y, sr = process_user_audio(audio_file, fixed_length=fixed_length)

    # Terapkan augmentasi yang dipilih
    if augment_type == 'pitch_shift':
        y_augmented = pitch_shift(y, sr, n_steps=2)
    elif augment_type == 'time_stretch':
        y_augmented = time_stretch(y, rate=1.25)
    else:
        raise ValueError(f"Unknown augment type: {augment_type}")

    plt.figure(figsize=(15, 5))
    librosa.display.waveshow(y_augmented, sr=sr, color='blue', alpha=0.5, label=f"{augment_type.capitalize()} Audio")
    librosa.display.waveshow(y, sr=sr, color='orange', alpha=0.75, label="Original Audio")
    plt.title(f"Audio Visualization ({class_name}) - {augment_type.capitalize()}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.tight_layout()
    plt.show()


def load_audio_from_path(path, label, augment=False, n_mfcc=13, fixed_length=66150):
    features = []
    labels = []
    augmentations = ['noise', 'pitch_shift', 'time_stretch']  # Tambahkan daftar augmentasi
    for file in os.listdir(path):
        if file.endswith('.wav'):  # Hanya mendukung file WAV
            audio_file = os.path.join(path, file)

            # Fitur asli tanpa augmentasi
            features.append(extract_features(audio_file, augment=False, n_mfcc=n_mfcc, fixed_length=fixed_length))
            labels.append(label)

            # Augmentasi jika diaktifkan
            if augment:
                for aug_type in augmentations:
                    features.append(extract_features(audio_file, augment=True, n_mfcc=n_mfcc, fixed_length=fixed_length, augment_type=aug_type))
                    labels.append(label)
    return features, labels


base_path = r'/content/drive/MyDrive/data suara psd'

x = []
y = []


classes = ['belly_pain', 'burping', 'discomfort', 'hungry', 'tired', 'not_baby']
augmentations = ['pitch_shift', 'time_stretch']
for idx, class_name in enumerate(classes):
    path = os.path.join(base_path, class_name)
    x_class, y_class = load_audio_from_path(path, idx, augment=True, n_mfcc=13, fixed_length=66150)
    x += x_class
    y += y_class

    audio_file = os.path.join(path, os.listdir(path)[0])
    visualize_audio_with_noise(audio_file, class_name, noise_factor=0.005, fixed_length=66150)
    visualize_spectrogram(audio_file, class_name, fixed_length=66150)
    for augment_type in augmentations:
        print(f"Visualizing {class_name} with {augment_type} augmentation...")
        visualize_audio_with_augmentation(audio_file, class_name, augment_type=augment_type)

x = np.array(x)
y = np.array(y)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)

x_train_norm = normalize(x_train)
x_test_norm = normalize(x_test)

y_train_encoded = to_categorical(y_train, num_classes=6)
y_test_encoded = to_categorical(y_test, num_classes=6)

model = Sequential([
    InputLayer(input_shape=(x_train_norm.shape[1],)),
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.4),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),
    Dense(6, activation='softmax')
])


model.compile(
    optimizer=Adam(learning_rate=0.05),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1, min_lr=0.00001)
early_stop = EarlyStopping(monitor='val_loss', patience=5, verbose=1, restore_best_weights=True)
history = model.fit(x_train_norm, y_train_encoded, validation_data=(x_test_norm, y_test_encoded),
                    epochs=50, batch_size=32, callbacks=[reduce_lr, early_stop])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
epochs = range(1, len(acc) + 1)

loss, accuracy = model.evaluate(x_test_norm, y_test_encoded, verbose=0)
print(f"Test Accuracy: {accuracy:.2f}")

plt.plot(epochs, acc, 'b-', label='Training Accuracy')
plt.plot(epochs, val_acc, 'r--', label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.show()

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.show()

from sklearn.metrics import classification_report

# Predict on train and test data
y_train_pred = model.predict(x_train_norm)
y_test_pred = model.predict(x_test_norm)

# Convert predicted probabilities to class labels
y_train_pred_classes = np.argmax(y_train_pred, axis=1)
y_test_pred_classes = np.argmax(y_test_pred, axis=1)

# Convert one-hot encoded labels back to class labels
y_train_true = np.argmax(y_train_encoded, axis=1)
y_test_true = np.argmax(y_test_encoded, axis=1)


# Print classification report for training data
print("Training Data Classification Report:")
print(classification_report(y_train_true, y_train_pred_classes))

# Print classification report for testing data
print("\nTesting Data Classification Report:")
print(classification_report(y_test_true, y_test_pred_classes))

import seaborn as sns
from sklearn.metrics import confusion_matrix

def plot_confusion_matrix(y_true, y_pred, title):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=classes, yticklabels=classes)
    plt.title(title)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.show()

# Plot confusion matrix for training data
plot_confusion_matrix(y_train_true, y_train_pred_classes, "Training Data Confusion Matrix")

# Plot confusion matrix for testing data
plot_confusion_matrix(y_test_true, y_test_pred_classes, "Testing Data Confusion Matrix")

for class_name in classes:
    class_path = os.path.join(base_path, class_name)
    file_count = 0
    for filename in os.listdir(class_path):
        if filename.endswith(".wav"):
            file_count += 1
    print(f"{class_name}' contains {file_count} audio files.")

"""# SIMPAN MODEL"""

model.save('baby_cry_model_akhir_banget.h5')