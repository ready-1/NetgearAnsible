#!/usr/bin/env python3
"""
Script to convert cleaned_commands.json (JSON array) to JSONL format.
Outputs each JSON object on a separate line to command_ref.jsonl
"""

import json

def convert_json_to_jsonl(input_file, output_file):
    """Convert JSON array to JSONL format."""
    try:
        # Read the JSON array from input file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Write each object as a separate line in JSONL format
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')

        print(f"Successfully converted {len(data)} records from {input_file} to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file - {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_file = "cleaned_commands.json"
    output_file = "command_ref.jsonl"
    convert_json_to_jsonl(input_file, output_file)
