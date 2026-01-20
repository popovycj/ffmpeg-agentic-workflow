import argparse
import os
import sys
import json
import base64
import requests
from pathlib import Path

def text_to_speech(input_file, output_dir, voice_id="21m00Tcm4TlvDq8ikWAM"): # Default voice: Rachel
    """
    Converts text file to audio using ElevenLabs API.
    Also saves word timestamps to a JSON file for SRT generation.
    """
    input_path = Path(input_file)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable is not set.")
        # Attempt to check if user provided it as a manual check or proceed with error
        sys.exit(1)

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    if not text:
        print("Error: Input text file is empty.")
        sys.exit(1)

    print(f"Converting text from '{input_path.name}' to speech...")

    # ElevenLabs API Endpoint
    # Using 'stream' endpoint usually allows timestamps, but non-streaming is easier for file saving.
    # However, timestamps are often returned in the streaming response or specific endpoint.
    # We will use the standard endpoint with timestamp query param if supported, otherwise falling back.
    # Current best practice for alignment is enabling `with_timestamps` which returns a JSON response containing audio base64 + alignment.

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            try:
                json_response = response.json()
            except json.JSONDecodeError:
                print("Warning: Response was not JSON (Timestamps unavailable). Saving raw audio.")
                # Save raw audio directly
                output_filename = f"{input_path.stem}.mp3"
                output_file_path = output_path / output_filename
                with open(output_file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Success! Audio saved to: {output_file_path}")
                return # Exit successfully without saving JSON

            output_filename = f"{input_path.stem}.mp3"
            output_file_path = output_path / output_filename
            json_output_path = output_path / f"{input_path.stem}.json"

            if 'audio_base64' in json_response:
                audio_data = base64.b64decode(json_response['audio_base64'])
                with open(output_file_path, 'wb') as f:
                    f.write(audio_data)

                print(f"Success! Audio saved to: {output_file_path}")

                if 'alignment' in json_response:
                    with open(json_output_path, 'w', encoding='utf-8') as f:
                        json.dump(json_response['alignment'], f, indent=2)
                    print(f"Timestamps saved to: {json_output_path}")
            else:
                 # Fallback if streaming raw audio (shouldn't happen with json header+timestamps)
                 with open(output_file_path, 'wb') as f:
                    f.write(response.content)
                 print(f"Warning: Saved raw audio, no alignment data found. {output_file_path}")

        else:
            print(f"Error from ElevenLabs API: {response.status_code} - {response.text}")
            sys.exit(1)

    except Exception as e:
        print(f"Error during API request: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text to speech using ElevenLabs API.")
    parser.add_argument("--input", required=True, help="Input text file")
    parser.add_argument("--output", required=True, help="Output directory for audio")
    parser.add_argument("--voice_id", default="21m00Tcm4TlvDq8ikWAM", help="ElevenLabs Voice ID")

    args = parser.parse_args()

    text_to_speech(args.input, args.output, args.voice_id)
