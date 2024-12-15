import logging
import argparse
import csv
import json
from typing import List, Optional

import requests
from utils import parse_phrase_inventory, CrewChiefAudioFile

logging.basicConfig(level=logging.INFO)

# Usage:
# 1) Choose a capable multilingual LLM (such as qwen2.5:32B), install and start
# the Ollama API server locally on all ip addresses (0.0.0.0)
#
#   $ OLLAMA_HOST=0.0.0.0:11434 ollama serve
#
#   (from another terminal window)
#   $ ollama list
#      NAME           ID              SIZE     MODIFIED
#      qwen2.5:32b    9f13ba1299af    19 GB    7 weeks ago
#
# 2) Start the crew-chief-autovoicepack Docker container with params enabling
# access to the host machine's network, ie:
#
#   $ docker run --rm -it --gpus all --add-host=host.docker.internal:host-gateway \
#     --name crew-chief-autovoicepack \
#     -v ~/crew-chief-autovoicepack/output:/app/output \
#     -v ~/crew-chief-autovoicepack/my_recordings:/app/baseline \
#     -v ./translated:/app/translated \
#     ghcr.io/cktlco/crew-chief-autovoicepack:latest
#
#       ^^^ note the new 'translated' directory
#
#   # (optional) confirm the Ollama host is reachable
#   $ telnet host.docker.internal 11434
#   Trying X.X.X.X...
#   Connected to host.docker.internal.
#   Escape character is '^]'.  (Ctrl-C to exit)
#
# 3) At the `crew-chief-autovoicepack >` command line, run this translation script with the name of the target language and the path to the new phrase inventory CSV file the script will create:
#
#  python3 translate_phrases.py --target_language Portuguese --translated_phrase_inventory translated/phrase_inventory_pt.csv
#
#  ^^^ note the new 'xxx_pt.csv' file above where 'pt' is the language code for Portuguese
#      this is not required, but helpful to keep things tidy with multiple languages
#
#    ... (example output)
#    INFO:root:Translation 1: okay -> tá bom (is good)
#    INFO:root:Translation 2: acknowledged -> confirmado (confirmed)
#    INFO:root:Translation 3: acknowledged -> reconhecido (recognized)
#    INFO:root:Translation 4: understood -> compreendido (understood)
#    INFO:root:Translation 5: acknowledged -> reconhecido (recognized) ...

# 4) After the translation script completes, you can find your new `phrase_inventory_XXX.csv` file in the `translated` directory on the host machine.
#
# 5) Manually review and edit the new CSV file if needed.
#
# 6) Create the voicepack using the normal instructions, making sure to reference the new
#    phrase_inventory_XXX.csv file you created.
#    - After translation, you may need to stop the Ollama server (ollama stop) to free up GPU RAM
#    - Use a baseline recording voice in the target language for best results, although it will still work
#      fine with the English baseline voices (ie, Luis)
#
#    python3 generate_voice_pack.py --your_name 'Ricardo' --voice_name 'Luis' --voice_name_tts 'Looees' --phrase_inventory translated/phrase_inventory_pt.csv --variation_count 1
#
#     [INFO] Starting...
#     [INFO] Attribution file written to ./output/Luis/CREATED_BY.txt for voicepack 'Luis' version 20241215'.
#     [INFO] Installation instructions written to ./output/Luis/INSTALLATION_INSTRUCTIONS.txt.
#     [INFO] Considering phrase 2 - 'reconhecido' -> 'reconhecido'
#     [INFO] Audio file created: ./output/Luis/voice/acknowledge/OK/5-a.wav
#     [INFO] xtts_integrity validity check passed for ./output/Luis/voice/acknowledge/OK/5-a.wav with score 0.99
#     ...

def translate_phrase_ollama(
    input_phrase: str,
    source_language_name: str,
    target_language_name: str,
    ollama_host: str = "host.docker.internal:11434",
) -> Optional[str]:
    """
    Translate an input phrase using a locally accessible Ollama API instance.
    See https://ollama.com/ to learn how to configure with the language model of your choice.
    """
    prompt = (
        'Respond with JSON only using this format: { "translation": "" }.'
        "DO NOT include any notes or comments or other human-readable text. JSON only."
        f"Translate all Arabic numerals like 1, 2, 3 to their equivalent word form in {target_language_name}."
        "Note that these phrases are related to the status of a race car on track, so use comparable terms.\n\n"
        f"Translate this phrase from {source_language_name} to {target_language_name}:\n\n{input_phrase}"
    )

    options = {
        "temperature": 0.4,
        #'max_tokens': 50,
        #'top_p': 1.0,
        #'num_predict': len(input_phrase) * 3
    }

    try:
        response = requests.post(
            f"http://{ollama_host}/api/generate",
            json={
                "model": "qwen2.5:32b",
                "prompt": prompt,
                "options": options,
                "stream": False,
            },
            timeout=20,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with Ollama API: {e}")
        return None

    # Attempt to parse the response as JSON
    try:
        data = response.json().get("response", {})
        json_payload = json.loads(data)

        if "translation" not in json_payload:
            raise json.JSONDecodeError(
                "Invalid LLM response, missing 'translation' key in JSON output."
            )

        translated_phrase = json_payload.get("translation", "").strip()

    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON response: {response.text}")
        return None

    return translated_phrase


def main():
    parser = argparse.ArgumentParser(
        description="Translate crew-chief-autovoicepack phrase text from English to the language of your choosing, using a local LLM API, with initial support for Ollama. Expect this process to take at least several hours, since it's not at all optimized for speed or efficiency (slow model, no batching, no caching, slow sanity check, etc)."
    )
    parser.add_argument(
        "--target_language",
        default="German",
        help="The English name of the target language to translate to, i.e. 'German', 'Spanish', 'Japanese'. Feel free to experiment if there is a certain dialect or other nuance that you think would help, this wording is being fed directly to the LLM as part of the translation request.",
    )
    parser.add_argument(
        "--phrase_inventory",
        help="Path to the input CSV file containing phrases to translate.",
        default="phrase_inventory.csv",
    )
    parser.add_argument(
        "--translated_phrase_inventory",
        help="Path to the output CSV file to save translated phrases, i.e. you may want 'phrase_inventory_de.csv' for German",
        default="phrase_inventory_translated.csv",
    )
    parser.add_argument(
        "--max_retries",
        help="Maximum number of retries to attempt for each phrase translation. Used when the LLM returns an incompatible response.",
        default=100,
    )
    parser.add_argument(
        "--sanity_check",
        help="If True, translate the LLM response back to English and display the result in the logs. This will help an observer gain confidence that the translation is accurate, but will slow down the process by approximately half since it requires an extra call to the LLM.",
        default=True,
    )
    args = parser.parse_args()

    entries: List[CrewChiefAudioFile] = parse_phrase_inventory(
        args.phrase_inventory, convert_slashes=False
    )

    if not entries:
        logging.error("No entries found in the phrase inventory. Exiting.")
        return

    # Open output CSV file for writing
    with open(
        args.translated_phrase_inventory, "w", newline="", encoding="utf-8"
    ) as csvfile_out:
        csvwriter = csv.writer(csvfile_out)

        # Write header row
        csvwriter.writerow(
            [
                "audio_path",
                "audio_filename",
                "subtitle",
                "text_for_tts",
                "original_english",
            ]
        )

        for entry_idx, entry in enumerate(entries, 1):
            english_phrase = entry.subtitle

            logging.debug(
                f"Translating input phrase {entry_idx} - '{english_phrase}'..."
            )

            # run translate in a loop until it returns a valid value (or reach max retries)
            translated_phrase: Optional[str] = None
            num_retries = 0
            while translated_phrase is None and num_retries < args.max_retries:
                translated_phrase = translate_phrase_ollama(
                    english_phrase,
                    source_language_name="English",
                    target_language_name=args.target_language,
                )
                if translated_phrase is None:
                    logging.error(
                        f"Failed to translate input phrase '{english_phrase}'. Retrying (#{num_retries}/{args.max_retries})."
                    )
                    num_retries += 1

            translated_phrase = translated_phrase or "TRANSLATION_FAILED"

            # sanity check by translating it back to English
            retranslated_phrase = (
                (
                    translate_phrase_ollama(
                        translated_phrase,
                        source_language_name=args.target_language,
                        target_language_name="English",
                    )
                    or "[Sanity check LLM call failed]"
                )
                if args.sanity_check
                else "..."
            )

            logging.info(
                f"Translation {entry_idx}: {entry.subtitle} -> {translated_phrase} ({retranslated_phrase})\n"
            )

            # Write the translated entry to the output CSV
            csvwriter.writerow(
                [
                    entry.audio_path,
                    f"{entry.audio_filename}.wav",
                    translated_phrase,  # subtitle field
                    translated_phrase,  # text_for_tts field
                    english_phrase,  # not used, for comparison only, original English subtitle
                ]
            )

    logging.info(
        f"All entries in {args.phrase_inventory} have been translated. Translation is available at {args.translated_phrase_inventory}"
    )


if __name__ == "__main__":
    main()
