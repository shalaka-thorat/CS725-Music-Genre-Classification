import librosa
import numpy as np
import tensorflow as tf
import streamlit as st
import os

model = tf.keras.models.load_model("./Exploring Mel-Spectograms/Genre-Classifier-Model.h5")
classes = ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']

def load_file(filepath, target_shape=(150, 150)):
    data = []
    audio_data, sample_rate = librosa.load(filepath, sr=None)
    chunk_duration = 4
    overlap_duration = 2
    chunk_samples = int(chunk_duration * sample_rate)
    overlap_samples = int(overlap_duration * sample_rate)
    num_chunks = int(np.ceil((len(audio_data) - chunk_samples) / (chunk_samples - overlap_samples))) + 1

    for i in range(num_chunks):
        start_sample = i * (chunk_samples - overlap_samples)
        end_sample = start_sample + chunk_samples
        chunk = audio_data[start_sample:end_sample]
        mel_spectrogram = librosa.feature.melspectrogram(y=chunk, sr=sample_rate)
        mel_spectrogram = tf.expand_dims(mel_spectrogram, axis=-1)
        mel_spectrogram = tf.image.resize(mel_spectrogram, target_shape)
        data.append(mel_spectrogram)

    return np.array(data)

def predict_genre(X_test):
    y_pred = model.predict(X_test)
    pred_cat = np.argmax(y_pred, axis=1)
    unique_cat, frequency = np.unique(pred_cat, return_counts=True)
    max_freq = np.max(frequency)
    for i in range(len(frequency)):
        if frequency[i] == max_freq:
            return classes[unique_cat[i]]

st.title("Music Genre Classifier")
st.write("Upload Audio File for Classfying its Music Genre")

test_audio_file = st.file_uploader("Choose an audio file", type=["wav", "mp3"])

if test_audio_file is not None:
    filepath = os.path.join("temp", test_audio_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(test_audio_file.getbuffer())

    if st.button("Play"):
        st.audio(test_audio_file)

    if st.button("Predict Genre"):
        with st.spinner("Prediction in Progress"):
            X_test = load_file(filepath)
            Predicted_Genre = predict_genre(X_test)
            st.write("Predicted Music Genre", Predicted_Genre)

    os.remove(filepath)

st.sidebar.title("CS725 PROJECT\n")
st.sidebar.write("Welcome to the Music Genre Clasffier!")
