import argparse
import os
import sys
import time
import requests
from pathlib import Path


def dub_voiceover(input_file, output_dir, source_lang="auto", target_lang="es"):
    """
    Dubs an audio file to a target language using ElevenLabs Dubbing API.
    Downloads the dubbed audio and saves it to output_dir.
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
        sys.exit(1)

    print(f"Dubbing '{input_path.name}' from {source_lang} to {target_lang}...")

    # Step 1: Create dubbing job
    create_url = "https://api.elevenlabs.io/v1/dubbing"
    headers = {
        "xi-api-key": api_key
    }

    with open(input_path, 'rb') as f:
        files = {
            'file': (input_path.name, f, 'audio/mpeg')
        }
        data = {
            'source_lang': source_lang,
            'target_lang': target_lang,
        }

        try:
            response = requests.post(create_url, headers=headers, files=files, data=data)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating dubbing job: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            sys.exit(1)

    dubbing_id = result.get('dubbing_id')
    expected_duration = result.get('expected_duration_sec', 0)

    if not dubbing_id:
        print(f"Error: No dubbing_id returned. Response: {result}")
        sys.exit(1)

    print(f"Dubbing job created: {dubbing_id}")
    print(f"Expected duration: {expected_duration:.1f}s")

    # Step 2: Poll for completion
    status_url = f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}"
    max_attempts = 120  # Max 20 minutes (120 * 10s)
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        time.sleep(10)  # Poll every 10 seconds

        try:
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking status: {e}")
            continue

        status = status_data.get('status', 'unknown')
        print(f"Status: {status} (attempt {attempt})")

        if status == 'dubbed':
            print("Dubbing completed!")
            break
        elif status == 'failed':
            error = status_data.get('error', 'Unknown error')
            print(f"Dubbing failed: {error}")
            sys.exit(1)
    else:
        print("Error: Dubbing timed out after 20 minutes.")
        sys.exit(1)

    # Step 3: Download dubbed audio
    download_url = f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}/audio/{target_lang}"

    try:
        download_response = requests.get(download_url, headers=headers)
        download_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading dubbed audio: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

    # Save dubbed audio
    output_filename = f"{input_path.stem}_{target_lang}.mp3"
    output_file_path = output_path / output_filename

    with open(output_file_path, 'wb') as f:
        f.write(download_response.content)

    print(f"Success! Dubbed audio saved to: {output_file_path}")

    # Step 4: Download dubbed transcript (SRT)
    print(f"Downloading transcript for {target_lang}...")
    transcript_url = f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}/transcript/{target_lang}"

    try:
        transcript_response = requests.get(transcript_url, headers=headers)
        transcript_response.raise_for_status()

        # Save dubbed transcript
        srt_filename = f"{input_path.stem}_{target_lang}.srt"
        srt_file_path = output_path / srt_filename

        with open(srt_file_path, 'wb') as f:
            f.write(transcript_response.content)

        print(f"Success! Dubbed transcript saved to: {srt_file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not download transcript: {e}")

    return str(output_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dub audio to another language using ElevenLabs API.")
    parser.add_argument("--input", required=True, help="Input audio file")
    parser.add_argument("--output", required=True, help="Output directory for dubbed audio")
    parser.add_argument("--source_lang", default="auto", help="Source language (ISO 639-1 code or 'auto')")
    parser.add_argument("--target_lang", default="es", help="Target language (ISO 639-1 code)")

    args = parser.parse_args()

    dub_voiceover(args.input, args.output, args.source_lang, args.target_lang)
