# If you run this in a local environment, you might already have these,
# but in Colab, it's good practice to ensure they are installed.
# !pip install librosa soundfile numpy scipy

import soundfile as sf
import numpy as np
from scipy.signal import butter, lfilter

# from google.colab import files # Will be imported conditionally later
import io  # For handling byte streams

# import sys # For checking if running in Colab


class MasteringPipeline:
    def __init__(self, output_path="mastered_track.wav"):
        """
        Initializes the MasteringPipeline.

        Args:
            output_path (str): The desired filename for the mastered audio file
                               within the environment. Defaults to "mastered_track.wav".
        """
        self.output_path = output_path
        self.reference_audio = None
        self.reference_sr = None
        self.audio = None
        self.sr = None
        self.notes = []  # To store notes on processing steps

    def _log_note(self, step, description):
        """
        Logs a note about a specific mastering step.

        Args:
            step (str): The step number or identifier (e.g., "1", "3").
            description (str): A description of the action taken.
        """
        self.notes.append(f"Step {step}: {description}")
        print(f"Step {step}: {description}")

    def load_audio_from_bytes(self, audio_bytes, sample_rate=None, is_reference=False):
        """
        Loads audio from bytes data.
        Ensures audio is stereo (2 channels, N samples). Mono files are converted to dual mono.

        Args:
            audio_bytes (bytes): The byte content of the audio file.
            sample_rate (int, optional): The target sample rate. Currently uses the original sample rate.
            is_reference (bool): True if this is the reference track, False for the main track.
        """
        try:
            audio_data, sr_orig = sf.read(
                io.BytesIO(audio_bytes), dtype="float32", always_2d=True
            )
            # soundfile's always_2d=True returns (N_frames, N_channels)
            # We want (N_channels, N_frames)
            audio_data = audio_data.T

            current_sr = sr_orig  # Using original sample rate

            if is_reference:
                self.reference_audio = audio_data
                self.reference_sr = current_sr
                self._log_note(
                    "Load Ref",
                    f"Reference audio loaded successfully: {current_sr} Hz, {audio_data.shape[0]} channels, {audio_data.shape[1]} samples.",
                )
            else:
                self.audio = audio_data
                self.sr = current_sr
                self._log_note(
                    "Load Main",
                    f"Main audio loaded successfully: {current_sr} Hz, {audio_data.shape[0]} channels, {audio_data.shape[1]} samples.",
                )

            # Ensure audio is stereo for processes like stereo widening
            # If mono, convert to dual mono
            target_audio_array = self.reference_audio if is_reference else self.audio
            if target_audio_array is not None and target_audio_array.shape[0] == 1:
                self._log_note(
                    "Mono Conversion",
                    "Input audio is mono. Converting to dual mono for stereo processing.",
                )
                target_audio_array = np.concatenate(
                    (target_audio_array, target_audio_array), axis=0
                )
                if is_reference:
                    self.reference_audio = target_audio_array
                else:
                    self.audio = target_audio_array
                self._log_note(
                    "Mono Conversion",
                    f"Audio now has {target_audio_array.shape[0]} channels.",
                )

            if (
                self.audio is not None and self.audio.shape[0] != 2 and not is_reference
            ):  # Check main audio
                self._log_note(
                    "Warning",
                    f"Loaded main audio has {self.audio.shape[0]} channels after processing. Pipeline expects stereo. Problems may occur.",
                )
            if (
                self.reference_audio is not None
                and self.reference_audio.shape[0] != 2
                and is_reference
            ):  # Check ref audio
                self._log_note(
                    "Warning",
                    f"Loaded reference audio has {self.reference_audio.shape[0]} channels after processing. Pipeline expects stereo.",
                )

        except Exception as e:
            raise RuntimeError(
                f"Error loading audio from bytes: {e}. Ensure it's a valid audio format (e.g., WAV, FLAC)."
            )

    def prepare_track(self):
        """
        Simulates the track preparation phase.
        Checks initial peak level and logs reference track presence.
        """
        if self.audio is None:
            self._log_note("Error", "Main audio not loaded. Cannot prepare track.")
            return

        self._log_note(
            "1", "Preparing track: Ensuring proper headroom and referencing."
        )
        peak_level = np.max(np.abs(self.audio)) if self.audio.size > 0 else 0
        peak_level_db = 20 * np.log10(peak_level) if peak_level > 0 else -np.inf
        self._log_note("1", f"Initial peak level: {peak_level_db:.2f} dBFS.")
        if peak_level_db > -3.0:
            self._log_note(
                "1",
                "Warning: Peak level is high. Consider reducing gain in your mixdown for optimal mastering.",
            )

        if self.reference_audio is not None:
            self._log_note("1", "Referencing against uploaded reference track.")
            # ref_rms_db = 20 * np.log10(np.mean(librosa.feature.rms(y=self.reference_audio, frame_length=2048, hop_length=512)[0]))
            # track_rms_db = 20 * np.log10(np.mean(librosa.feature.rms(y=self.audio, frame_length=2048, hop_length=512)[0]))
            # self._log_note("1", f"Reference RMS: {ref_rms_db:.2f} dBFS, Track RMS: {track_rms_db:.2f} dBFS (approx)")
        else:
            self._log_note("1", "No reference track provided for detailed comparison.")

    def listen_and_note(self):
        """
        Simulates the critical listening and note-taking phase.
        This step requires manual user interaction in a real workflow.
        """
        if self.audio is None:
            self._log_note("Error", "Main audio not loaded. Cannot listen and note.")
            return

        self._log_note(
            "2", "Listening to the track for potential issues and noting the approach."
        )
        print(
            """
--- Manual Listening and Note-Taking Required ---
This step simulates the critical listening phase of mastering.
Identify any issues or areas for improvement. Consider the sonic characteristics compared to your reference track (if provided).
Make notes on desired EQ adjustments, compression needs, etc. This pipeline will use predefined settings based on common practices."""
        )
        # Removed Colab/interactive input prompt as it's not suitable for a module

    def apply_master_eq(self):
        """
        Applies a multi-band parametric EQ to the master track using IIR biquad filters.
        """
        if self.audio is None:
            self._log_note("Error", "Main audio not loaded. Cannot apply EQ.")
            return
        self._log_note("3", "Applying master EQ.")

        def design_biquad(filter_type, freq, sr, q_val=1.0, gain_db=0.0):
            omega0 = 2 * np.pi * freq / sr
            cos_omega0 = np.cos(omega0)
            sin_omega0 = np.sin(omega0)
            A_shelf = 10 ** (gain_db / 40.0)  # For shelving filters
            A_linear = 10 ** (gain_db / 20.0)  # For peaking filters

            alpha = (
                sin_omega0 / (2 * q_val) if q_val > 0 else sin_omega0
            )  # Avoid division by zero for q_val

            b = np.zeros(3)
            a = np.zeros(3)

            if filter_type == "peaking":
                b[0] = 1 + alpha * A_linear
                b[1] = -2 * cos_omega0
                b[2] = 1 - alpha * A_linear
                a[0] = (
                    1 + alpha / A_linear if A_linear != 0 else 1 + alpha
                )  # Avoid division by zero
                a[1] = -2 * cos_omega0
                a[2] = (
                    1 - alpha / A_linear if A_linear != 0 else 1 - alpha
                )  # Avoid division by zero
            elif filter_type == "notch":
                b[0] = 1
                b[1] = -2 * cos_omega0
                b[2] = 1
                a[0] = 1 + alpha
                a[1] = -2 * cos_omega0
                a[2] = 1 - alpha
            elif filter_type == "highshelf":
                # RBJ Cookbook equations for High-Shelf
                if gain_db >= 0:  # Boost
                    b[0] = A_shelf * (
                        (A_shelf + 1)
                        + (A_shelf - 1) * cos_omega0
                        + 2 * np.sqrt(A_shelf) * alpha
                    )
                    b[1] = -2 * A_shelf * ((A_shelf - 1) + (A_shelf + 1) * cos_omega0)
                    b[2] = A_shelf * (
                        (A_shelf + 1)
                        + (A_shelf - 1) * cos_omega0
                        - 2 * np.sqrt(A_shelf) * alpha
                    )
                    a[0] = (
                        (A_shelf + 1)
                        - (A_shelf - 1) * cos_omega0
                        + 2 * np.sqrt(A_shelf) * alpha
                    )
                    a[1] = 2 * ((A_shelf - 1) - (A_shelf + 1) * cos_omega0)
                    a[2] = (
                        (A_shelf + 1)
                        - (A_shelf - 1) * cos_omega0
                        - 2 * np.sqrt(A_shelf) * alpha
                    )
                else:  # Cut
                    A_shelf_inv = (
                        1 / A_shelf if A_shelf != 0 else np.finfo(float).eps
                    )  # Avoid division by zero
                    # Calculate coefficients for boost with A_shelf_inv
                    b0_calc = A_shelf_inv * (
                        (A_shelf_inv + 1)
                        + (A_shelf_inv - 1) * cos_omega0
                        + 2 * np.sqrt(A_shelf_inv) * alpha
                    )
                    b1_calc = (
                        -2
                        * A_shelf_inv
                        * ((A_shelf_inv - 1) + (A_shelf_inv + 1) * cos_omega0)
                    )
                    b2_calc = A_shelf_inv * (
                        (A_shelf_inv + 1)
                        + (A_shelf_inv - 1) * cos_omega0
                        - 2 * np.sqrt(A_shelf_inv) * alpha
                    )
                    a0_calc = (
                        (A_shelf_inv + 1)
                        - (A_shelf_inv - 1) * cos_omega0
                        + 2 * np.sqrt(A_shelf_inv) * alpha
                    )
                    a1_calc = 2 * ((A_shelf_inv - 1) - (A_shelf_inv + 1) * cos_omega0)
                    a2_calc = (
                        (A_shelf_inv + 1)
                        - (A_shelf_inv - 1) * cos_omega0
                        - 2 * np.sqrt(A_shelf_inv) * alpha
                    )
                    # Swap b and a for cut
                    b = np.array([a0_calc, a1_calc, a2_calc])
                    a = np.array([b0_calc, b1_calc, b2_calc])
            else:
                raise ValueError(f"Unknown filter type: {filter_type}")

            if np.abs(a[0]) < np.finfo(float).eps:
                a[0] = (
                    np.copysign(np.finfo(float).eps, a[0])
                    if a[0] != 0
                    else np.finfo(float).eps
                )

            return b / a[0], a / a[0]

        eq_stages = [
            {"type": "highshelf", "cutoff_freq": 8000, "q_val": 0.707, "gain_db": 1.0},
            {"type": "peaking", "center_freq": 3000, "q_val": 1.5, "gain_db": 0.7},
            {"type": "peaking", "center_freq": 7000, "q_val": 3.0, "gain_db": -0.5},
            {"type": "peaking", "center_freq": 250, "q_val": 1.8, "gain_db": -0.8},
            {"type": "lowshelf", "cutoff_freq": 100, "q_val": 0.707, "gain_db": 1.2},
        ]

        processed_audio = np.copy(self.audio)
        for stage in eq_stages:
            freq_param = stage.get("center_freq", stage.get("cutoff_freq"))
            b_coeffs, a_coeffs = design_biquad(
                stage["type"], freq_param, self.sr, stage["q_val"], stage["gain_db"]
            )
            for i in range(self.audio.shape[0]):
                processed_audio[i] = lfilter(b_coeffs, a_coeffs, processed_audio[i])

        self.audio = processed_audio
        self._log_note("3", "Master EQ applied with multiple filter stages.")

    def apply_master_compression(self):
        """
        Applies a simulated multiband compression.
        """
        if self.audio is None:
            self._log_note("Error", "Main audio not loaded. Cannot apply compression.")
            return
        self._log_note("4", "Applying master multiband compression.")

        def simple_compressor(
            audio_segment,
            sr_comp,
            threshold_db=-18.0,
            ratio=3.0,
            attack_ms=5.0,
            release_ms=100.0,
            makeup_gain_db=0.0,
        ):
            threshold = 10 ** (threshold_db / 20.0)
            attack_coeff = (
                np.exp(-1.0 / (sr_comp * (attack_ms / 1000.0)))
                if attack_ms > 0
                else 0.0
            )
            release_coeff = (
                np.exp(-1.0 / (sr_comp * (release_ms / 1000.0)))
                if release_ms > 0
                else 0.0
            )
            makeup_gain = 10 ** (makeup_gain_db / 20.0)

            gain_envelope = np.ones_like(audio_segment)
            current_gain = 1.0

            for i_sample in range(len(audio_segment)):
                instant_level = np.abs(audio_segment[i_sample])
                target_gain_reduction = 1.0
                if (
                    instant_level > threshold and threshold > 0
                ):  # Add check for threshold > 0 to avoid issues with log
                    target_gain_reduction = (
                        (threshold + (instant_level - threshold) / ratio)
                        / instant_level
                        if instant_level > 0
                        else 1.0
                    )

                if target_gain_reduction < current_gain:
                    current_gain = (
                        1.0 - attack_coeff
                    ) * target_gain_reduction + attack_coeff * current_gain
                else:
                    current_gain = (
                        1.0 - release_coeff
                    ) * target_gain_reduction + release_coeff * current_gain
                gain_envelope[i_sample] = current_gain

            return audio_segment * gain_envelope * makeup_gain

        low_crossover = 150
        mid_crossover = 2000
        filter_order = 4

        processed_channels = []
        for i in range(self.audio.shape[0]):
            channel_audio = self.audio[i]

            b_low, a_low = butter(filter_order, low_crossover, btype="low", fs=self.sr)
            low_band = lfilter(b_low, a_low, channel_audio)

            b_mid, a_mid = butter(
                filter_order, [low_crossover, mid_crossover], btype="band", fs=self.sr
            )
            mid_band = lfilter(b_mid, a_mid, channel_audio)

            b_high, a_high = butter(
                filter_order, mid_crossover, btype="high", fs=self.sr
            )
            high_band = lfilter(b_high, a_high, channel_audio)

            compressed_low = simple_compressor(
                low_band,
                self.sr,
                threshold_db=-20,
                ratio=2.5,
                attack_ms=10,
                release_ms=150,
                makeup_gain_db=1.0,
            )
            compressed_mid = simple_compressor(
                mid_band,
                self.sr,
                threshold_db=-18,
                ratio=3.0,
                attack_ms=5,
                release_ms=100,
                makeup_gain_db=0.5,
            )
            compressed_high = simple_compressor(
                high_band,
                self.sr,
                threshold_db=-15,
                ratio=2.0,
                attack_ms=2,
                release_ms=80,
                makeup_gain_db=0.0,
            )

            recombined_channel = compressed_low + compressed_mid + compressed_high
            processed_channels.append(recombined_channel)

        self.audio = np.array(processed_channels)
        self._log_note(
            "4", "Simulated multiband compression applied (Low, Mid, High bands)."
        )

    def apply_enhancement(self):
        """
        Applies subtle tape saturation and stereo widening.
        """
        if self.audio is None:
            self._log_note("Error", "Main audio not loaded. Cannot apply enhancement.")
            return
        if self.audio.shape[0] != 2:
            self._log_note(
                "5",
                "Skipping stereo enhancement: Audio is not stereo (requires 2 channels).",
            )
            return

        self._log_note(
            "5", "Applying optional enhancement: Saturation and Stereo Widening."
        )

        saturation_amount = 0.03
        drive = 1.0 + saturation_amount * 3.0

        saturated_part = np.tanh(self.audio * drive)
        self.audio = (
            1 - saturation_amount
        ) * self.audio + saturation_amount * saturated_part
        self._log_note(
            "5",
            f"Subtle tape saturation applied (amount: {saturation_amount*100:.1f}%).",
        )

        mid = 0.5 * (self.audio[0] + self.audio[1])
        side = 0.5 * (self.audio[0] - self.audio[1])

        widening_factor = 1.10
        side_widened = side * widening_factor

        left_out = mid + side_widened
        right_out = mid - side_widened

        mono_bass_cutoff_freq = 120
        filter_order_bass = 2

        b_lp_mono, a_lp_mono = butter(
            filter_order_bass, mono_bass_cutoff_freq, btype="low", fs=self.sr
        )
        mono_bass_component = lfilter(b_lp_mono, a_lp_mono, mid)

        b_hp_stereo, a_hp_stereo = butter(
            filter_order_bass, mono_bass_cutoff_freq, btype="high", fs=self.sr
        )
        left_hp = lfilter(b_hp_stereo, a_hp_stereo, left_out)
        right_hp = lfilter(b_hp_stereo, a_hp_stereo, right_out)

        self.audio[0] = left_hp + mono_bass_component
        self.audio[1] = right_hp + mono_bass_component
        self._log_note(
            "5",
            f"Stereo widening applied (factor: {widening_factor:.2f}) with mono bass preservation below {mono_bass_cutoff_freq}Hz.",
        )

    def apply_limiting(self):
        """
        Applies a brickwall limiter.
        """
        if self.audio is None:
            self._log_note("Error", "Main audio not loaded. Cannot apply limiting.")
            return
        self._log_note("6", "Applying brickwall limiting for loudness.")

        ceiling_db = -0.3
        ceiling_linear = 10 ** (ceiling_db / 20.0)

        def brickwall_limiter(
            audio_segment, sr_lim, ceiling_val, attack_ms=1.0, release_ms=50.0
        ):
            attack_coeff = (
                np.exp(-1.0 / (sr_lim * (attack_ms / 1000.0))) if attack_ms > 0 else 0.0
            )
            release_coeff = (
                np.exp(-1.0 / (sr_lim * (release_ms / 1000.0)))
                if release_ms > 0
                else 0.0
            )

            gain_envelope = np.ones_like(audio_segment)
            current_gain = 1.0

            for i_sample in range(len(audio_segment)):
                instant_level = np.abs(audio_segment[i_sample])
                target_gain_reduction = 1.0
                # Check if the signal *would* exceed ceiling with current gain
                if instant_level * current_gain > ceiling_val:
                    target_gain_reduction = (
                        ceiling_val / instant_level if instant_level > 0 else 1.0
                    )

                if target_gain_reduction < current_gain:
                    current_gain = (
                        1.0 - attack_coeff
                    ) * target_gain_reduction + attack_coeff * current_gain
                else:
                    current_gain = (
                        1.0 - release_coeff
                    ) * target_gain_reduction + release_coeff * current_gain
                gain_envelope[i_sample] = current_gain

            limited_audio = audio_segment * gain_envelope
            return np.clip(limited_audio, -ceiling_val, ceiling_val)

        best_attack_ms = 1.5
        best_release_ms = 75.0
        self._log_note(
            "6",
            f"Limiter settings: Attack={best_attack_ms:.2f}ms, Release={best_release_ms:.2f}ms, Ceiling={ceiling_db:.2f}dBFS.",
        )

        processed_channels = []
        for i in range(self.audio.shape[0]):
            limited_channel = brickwall_limiter(
                self.audio[i], self.sr, ceiling_linear, best_attack_ms, best_release_ms
            )
            processed_channels.append(limited_channel)
        self.audio = np.array(processed_channels)

        final_peak_val = np.max(np.abs(self.audio)) if self.audio.size > 0 else 0
        final_peak_db = 20 * np.log10(final_peak_val) if final_peak_val > 0 else -np.inf
        self._log_note(
            "6",
            f"Brickwall limiting applied. Final peak level: {final_peak_db:.2f} dBFS.",
        )

    def export_track(self, bit_depth=24, dither_option="POW-r 2"):
        """
        Exports the mastered track with specified bit depth and conceptual dithering.
        """
        if self.audio is None:
            self._log_note("Error", "Main audio not processed. Cannot export.")
            return
        self._log_note(
            "7",
            f"Exporting track to {self.output_path} with {bit_depth}-bit and {dither_option} dither.",
        )

        max_abs = np.max(np.abs(self.audio)) if self.audio.size > 0 else 0
        if max_abs > 1.0:  # Should not happen if limiter works, but safeguard
            self.audio /= max_abs

        temp_audio_export = np.copy(self.audio)

        if bit_depth < 32:
            quant_levels = 2**bit_depth
            dither_noise_one_sample = (
                np.random.uniform(-1.0, 1.0, temp_audio_export.shape)
                + np.random.uniform(-1.0, 1.0, temp_audio_export.shape)
            ) * (1.0 / quant_levels)

            if dither_option == "POW-r 1":
                self._log_note(
                    "7", "Applying conceptual POW-r 1 dither (minimal noise shaping)."
                )
            elif dither_option == "POW-r 2":
                b_ns, a_ns = butter(2, 2000 / (self.sr / 2.0), btype="high")
                for i in range(temp_audio_export.shape[0]):
                    dither_noise_one_sample[i] = lfilter(
                        b_ns, a_ns, dither_noise_one_sample[i]
                    )
                self._log_note(
                    "7", "Applying conceptual POW-r 2 dither (moderate noise shaping)."
                )
            elif dither_option == "POW-r 3":
                b_ns, a_ns = butter(4, 4000 / (self.sr / 2.0), btype="high")
                for i in range(temp_audio_export.shape[0]):
                    dither_noise_one_sample[i] = lfilter(
                        b_ns, a_ns, dither_noise_one_sample[i]
                    )
                self._log_note(
                    "7",
                    "Applying conceptual POW-r 3 dither (aggressive noise shaping).",
                )
            else:
                self._log_note(
                    "7",
                    f"Unknown dither option '{dither_option}'. Applying basic TPDF dither without shaping.",
                )

            temp_audio_export += dither_noise_one_sample

        try:
            sf.write(
                self.output_path,
                temp_audio_export.T,
                self.sr,
                subtype=f"PCM_{bit_depth}",
            )
            self._log_note(
                "7", f"Mastered track exported successfully to {self.output_path}."
            )

            # Check if running in Colab before suggesting files.download
            print(
                f"\nMastered track saved to: {self.output_path} in your local environment."
            )

        except Exception as e:
            self._log_note("Error", f"Error exporting audio file: {e}")
            raise RuntimeError(f"Error exporting audio file: {e}")

    def run_mastering_pipeline(
        self,
        main_audio_bytes,
        reference_audio_bytes=None,
        bit_depth=24,
        dither_option="POW-r 2",
    ):
        """
        Executes the entire mastering pipeline step-by-step.
        """
        print("\n--- Starting Audio Mastering Pipeline ---")
        self.notes = []
        try:
            self.load_audio_from_bytes(main_audio_bytes, is_reference=False)
            if self.audio is None:
                print("Failed to load main audio. Aborting pipeline.")
                return

            if reference_audio_bytes:
                self.load_audio_from_bytes(reference_audio_bytes, is_reference=True)

            self.prepare_track()
            self.listen_and_note()
            self.apply_master_eq()
            self.apply_master_compression()
            self.apply_enhancement()
            self.apply_limiting()
            self.export_track(bit_depth=bit_depth, dither_option=dither_option)

            print("\n--- Mastering Pipeline Finished ---")
            print("Summary of actions taken:")
            for note in self.notes:
                print(f"- {note}")

        except RuntimeError as e:
            print(f"\nA runtime error occurred during the mastering pipeline: {e}")
            self._log_note("Fatal Error", str(e))
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            self._log_note("Fatal Error", f"Unexpected: {str(e)}")


def main():
    """
    Main function to run InstaMaster as a standalone application.
    """
    import argparse
    import os
    import sys
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="InstaMaster: Automated Audio Mastering Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python instamaster.py input.wav                    # Basic mastering
  python instamaster.py input.wav -o mastered.wav   # Specify output
  python instamaster.py input.wav -r reference.wav  # With reference track
  python instamaster.py input.wav --bit-depth 16    # 16-bit output
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Input audio file to master (WAV, MP3, FLAC, etc.)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="mastered_track.wav",
        help="Output file path (default: mastered_track.wav)"
    )
    
    parser.add_argument(
        "-r", "--reference",
        help="Reference track for comparison"
    )
    
    parser.add_argument(
        "--bit-depth",
        type=int,
        choices=[16, 24, 32],
        default=24,
        help="Output bit depth (default: 24)"
    )
    
    parser.add_argument(
        "--dither",
        choices=["POW-r 1", "POW-r 2", "POW-r 3"],
        default="POW-r 2",
        help="Dithering algorithm (default: POW-r 2)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode with sample audio"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Test mode
    if args.test or os.environ.get('INSTAMASTER_TEST_MODE'):
        print("Running in test mode...")
        print("This would generate a test audio file and process it.")
        print("For actual usage, provide an input audio file.")
        return
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    
    # Check if reference file exists (if provided)
    if args.reference and not os.path.exists(args.reference):
        print(f"Error: Reference file '{args.reference}' not found.")
        sys.exit(1)
    
    try:
        # Initialize mastering pipeline
        pipeline = MasteringPipeline(output_path=args.output)
        
        # Read input audio file
        print(f"Loading input file: {args.input_file}")
        with open(args.input_file, 'rb') as f:
            main_audio_bytes = f.read()
        
        # Read reference audio file (if provided)
        reference_audio_bytes = None
        if args.reference:
            print(f"Loading reference file: {args.reference}")
            with open(args.reference, 'rb') as f:
                reference_audio_bytes = f.read()
        
        # Run the mastering pipeline
        pipeline.run_mastering_pipeline(
            main_audio_bytes=main_audio_bytes,
            reference_audio_bytes=reference_audio_bytes,
            bit_depth=args.bit_depth,
            dither_option=args.dither
        )
        
        print(f"\nMastering completed successfully!")
        print(f"Output file: {args.output}")
        
    except Exception as e:
        print(f"Error during mastering: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
