from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from .forms import AudioUploadForm  # Use the new form that accepts a file
from pydub import AudioSegment
from scipy.signal import lfilter, freqz
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
from pathlib import Path
import numpy as np
from django.core.files.storage import default_storage
import random
import tempfile
import os
from django.conf import settings

def pres_et(request):
    return render(request, 'pres_et.html', {'MEDIA_URL': settings.MEDIA_URL})


def getsong(request):
    if request.method == 'POST':
        difficulty = int(request.POST.get("difficulty", 25))
        uploaded_file = request.FILES.get("audio_file")

        if not uploaded_file:
            return HttpResponseBadRequest("No audio file uploaded.")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                media_dir = os.path.join(os.getcwd(), 'media', 'et_songs')
                os.makedirs(media_dir, exist_ok=True)

                i_name = 1
                files = [int(f.name[16:-4]) for f in Path(media_dir).glob("song_to_convert_*.mp3")]
                while i_name in files:
                    i_name = (i_name % 10) + 1
                    if all(i in files for i in range(1, 11)):
                        for f in Path(media_dir).iterdir():
                            if f.is_file():
                                f.unlink()
                        i_name = 1

                ext = Path(uploaded_file.name).suffix.lower()
                input_path = os.path.join(media_dir, f"song_to_convert_{i_name}{ext}")
                output_path = os.path.join(media_dir, f"song_to_convert_{i_name}.mp3")

                # Save the uploaded file
                with open(input_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Generate filter parameters
                nb_bands = (difficulty // 10) + 1
                freq_list = [round(10 ** random.uniform(np.log10(20), np.log10(20000)), 1) for _ in range(nb_bands)]
                Q_list = [round(random.uniform(0.7, 10), 1) for _ in range(nb_bands)]
                gain_list = [round(random.uniform(-12, 12), 1) for _ in range(nb_bands)]

                filter_list = [[freq_list[i], gain_list[i], Q_list[i]] for i in range(nb_bands)]

                fs = filter_mp3(input_path, output_path, filter_list)

                # Plot filter response
                w = np.geomspace(20, fs / 2, num=16000)
                sumh = np.zeros(len(w))
                color_list = ["cyan", "fuchsia", "yellow", "darkorange", "red", "darkblue"]

                plt.figure(figsize=(12, 5))
                for i, (freq, gain, Q) in enumerate(filter_list):
                    b, a = peaking_eq_coeffs(freq, Q, gain, fs)
                    _, h = freqz(b, a, worN=w, fs=fs)
                    icolor = color_list[i % len(color_list)]
                    db_response = -20 * np.log10(abs(h))
                    plt.semilogx(w, db_response, label=f'Freq: {freq} Hz, Gain: {gain} dB, Q: {Q}', color=icolor, linewidth=1)
                    plt.fill_between(w, db_response, color=icolor, alpha=0.3)
                    sumh += db_response

                plt.semilogx(w, sumh, linewidth=3, color='lime', label='Overall Response')
                plt.title('Frequency Response of the EQ', color='white')
                plt.xlabel('Frequency (Hz)', color='white')
                plt.ylabel('Gain (dB)', color='white')
                plt.xticks([20, 100, 1000, 5000, 10000, 20000], ['20 Hz','100 Hz', '1k', '5k', '10k','20k'])
                plt.yticks([-20,-10, 0, 10,20], ['-20 dB','-10 dB', '0 dB', '10 dB','-20 dB'])
                plt.tick_params(axis='x', colors='white') 
                plt.tick_params(axis='y', colors='white') 
                plt.legend(facecolor='black', labelcolor='white')
                plt.grid(True, color='white')
                plt.gca().set_facecolor('black')
                plt.gcf().set_facecolor('black')
                plt.savefig(os.path.join(media_dir, f'song_to_convert_{i_name}.png'))
                plt.close()

                audio_url = f"song_to_convert_{i_name}.mp3"
                image_url = f'song_to_convert_{i_name}.png'
                return render(request, 'download_files.html', {'MEDIA_URL': settings.MEDIA_URL,'audio_name': audio_url, 'image_name': image_url})

        except Exception as e:
            return HttpResponseBadRequest(f"Error processing file: {str(e)}")

    return render(request, "getsong.html")

# The download views remain largely unchanged:


def filter_mp3(input_file, output_file, filters):
    """Loads an MP3 file, applies a parametric EQ filter, and saves the output."""
    audio = AudioSegment.from_file(input_file)
    
    filtered_audio,fs = apply_multiband_eq(audio, filters) #[ frequency,gain, Q]

    filtered_audio.export(output_file, format="mp3")

    return fs

def peaking_eq_coeffs(freq,Q,gain_db,fs):
    # https://www.musicdsp.org/en/latest/_downloads/3e1dc886e7849251d6747b194d482272/Audio-EQ-Cookbook.txt
    w0 = 2*np.pi*freq/fs
    alpha= np.sin(w0)/(2*Q)
    A=10**(gain_db/40)

    b0 =   1 + alpha*A
    b1 =  -2*np.cos(w0)
    b2 =   1 - alpha*A
    a0 =   1 + alpha/A
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha/A

    a=[b0/a0,b1/a0,b2/a0]
    b=[1,a1/a0,a2/a0]

    return b, a



def apply_multiband_eq(audio_segment, bands):
    """
    Applies a multi-band EQ where each band is specified as (freq, gain_db, Q).
    
    :param audio_segment: The input audio segment.
    :param bands: A list of tuples [(freq, gain_db, Q), ...].
    :return: The filtered audio segment.
    """
    
    # Extract parameters
    fs = audio_segment.frame_rate
    sample_width = audio_segment.sample_width
    num_channels = audio_segment.channels

    # Convert audio to NumPy array
    samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)

    # Handle stereo audio properly
    if num_channels == 2:
        samples = samples.reshape((-1, 2))

    # Process each band using the Peaking EQ
    for freq, gain_db, Q in bands:
        if gain_db == 0:
            continue  # Skip if no change is needed

        b, a = peaking_eq_coeffs(freq, Q, gain_db, fs)
        samples = lfilter(b, a, samples, axis=0)

    # Normalize to prevent clipping
    max_val = np.max(np.abs(samples))
    if max_val > 1.0:
        samples /= max_val

    # Convert back to int16
    samples = (samples * (2**15 - 1)).astype(np.int16)

    # Convert back to AudioSegment properly
    filtered_audio = AudioSegment(
        samples.tobytes(),
        frame_rate=fs,
        sample_width=2,
        channels=num_channels
    )

    return filtered_audio,fs


def convert_m4a_to_mp3(input_file, output_file):
    # Load the .m4a file
    audio = AudioSegment.from_file(input_file, format="m4a")

    # Export the audio as .mp3
    audio.export(output_file, format="mp3")
    print(f"Conversion complete: {output_file}")

def smooth_response(h, window=50):
    return np.convolve(20 * np.log10(abs(h)), np.ones(window)/window, mode='same')