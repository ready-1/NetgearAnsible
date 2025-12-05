import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()  # Load .env file

COMMAND_LIST_FILE = 'command_list.txt'
CHUNKS_FILE = 'M4300_CLI_EN_chunks.jsonl'
OUTPUT_FILE = 'command_references.json'
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'openai/gpt-4o-mini'
API_KEY = os.getenv('OPENROUTER_API_KEY')  # Assumes key is OPENROUTER_API_KEY in .env

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

def load_commands(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")
    with open(file_path, 'r', encoding='utf-8') as f:
        commands = [line.strip().split(' (')[0].strip() for line in f if line.strip()]
    return set(commands)  # As set for fast lookup

def load_chunks(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")
    chunks = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def llm_extract(batch_texts, last_cmd=None):
    prompt = (
        "Extract all CLI commands from this batch of manual text. "
        "For each command found, output a JSON object where the key is the command name (exact, no extras), "
        "and the value is a dict with: "
        "'syntax': full command syntax including args/options (string), "
        "'summary': one-sentence purpose (string), "
        "'synopsis': full detailed description/synopsis (string, up to 300 chars). "
        "Output ONLY the JSON dict of {command: {...}}, no other text. "
        f"Batch text: {' '.join(batch_texts)}"
    )
    if last_cmd:
        prompt += f" Start extraction after the command '{last_cmd}' to avoid duplicates."

    response = requests.post(
        OPENROUTER_API_URL,
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': MODEL,
            'messages': [{'role': 'user', 'content': prompt}]
        }
    )
    response.raise_for_status()
    try:
        return json.loads(response.json()['choices'][0]['message']['content'])
    except (KeyError, json.JSONDecodeError) as e:
        print(f"LLM parse error: {e}")
        return {}

def merge_extracted(extracted, new_data):
    for cmd, info in new_data.items():
        if cmd in extracted:
            # Keep the one with longer synopsis
            if len(info.get('synopsis', '')) > len(extracted[cmd].get('synopsis', '')):
                extracted[cmd] = info
        else:
            extracted[cmd] = info

def main():
    master_cmds = load_commands(COMMAND_LIST_FILE)
    chunks = load_chunks(CHUNKS_FILE)
    extracted = {}
    last_cmd = None
    total_chunks = len(chunks)

    for i in range(total_chunks):
        batch = []
        if i > 0:
            batch.append(chunks[i-1])  # Prev
        batch.append(chunks[i])  # Current
        if i + 1 < total_chunks:
            batch.append(chunks[i+1])  # Next

        batch_texts = [c.get('text', '') + ' ' + c.get('summary', '') for c in batch]
        print(f"Processing chunk {i+1}/{total_chunks} (batch size: {len(batch)})...")

        new_extracted = llm_extract(batch_texts, last_cmd)
        merge_extracted(extracted, new_extracted)

        # Update last_cmd to the last command in this batch (alphabetical sort for consistency)
        if new_extracted:
            last_cmd = sorted(new_extracted.keys())[-1]

    # Post-process: Filter to master, add stubs for misses
    final_refs = {cmd: extracted[cmd] for cmd in extracted if cmd in master_cmds}
    misses = master_cmds - set(final_refs.keys())
    for miss in misses:
        final_refs[miss] = {
            'syntax': miss,
            'summary': 'No extraction found.',
            'synopsis': 'Manual review needed.'
        }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_refs, f, indent=4)
    print(f"Generated {len(final_refs)} references. Misses (stubbed): {len(misses)}")

if __name__ == "__main__":
    main()