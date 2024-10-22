import logging
import argparse
import csv
import json
from typing import List, Optional

import requests
from utils import parse_phrase_inventory, CrewChiefAudioFile

logging.basicConfig(level=logging.INFO)


def translate_phrase_ollama(
    input_phrase: str,
    source_language_name: str = "English",
    target_language_name: str = "German",
    ollama_host: str = "host.docker.internal:11434",
) -> Optional[str]:
    """
    Translate an input phrase using a locally accessible Ollama API instance.
    See https://ollama.com/ to learn how to configure with the language model of your choice.
    """
    prompt = (
        'Respond with JSON only using this format: { "translation": "" }.'
        "DO NOT include any notes or comments or other human-readable text. JSON only."
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

    if not sanity_check_llm_response(translated_phrase):
        logging.error("LLM response failed sanity check.")
        return None

    return translated_phrase


def sanity_check_llm_response(response: str) -> bool:
    """
    Check the response from the Ollama API to ensure it is only the translated
    phrase and not a longer comment, question, or result other than the translation.
    """
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Translate crew-chief-autovoicepack phrase text from English to the language of your choosing, using a local LLM API, with initial support for Ollama."
    )
    parser.add_argument(
        "--target_language",
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
        help="Maximum number of retries to attempt for each phrase translation. Used when the LLM returns an unusuable response.",
        default=100,
    )
    parser.add_argument(
        "--sanity_check",
        help="If True, translate the LLM response back to English and display the result in the logs. This will help an observer gain confidence that the translation is accurate, but will slow down the process by approximately half since it requires an extra call to the LLM.",
        default=False,
    )
    args = parser.parse_args()

    entries: List[CrewChiefAudioFile] = parse_phrase_inventory(args.phrase_inventory)

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
                translated_phrase = translate_phrase_ollama(english_phrase)
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
                        source_language_name="German",
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
                    entry.audio_filename,
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
