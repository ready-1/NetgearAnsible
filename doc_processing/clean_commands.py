import json
import re
from collections import defaultdict
from difflib import SequenceMatcher

def get_category(command_name):
    """Determine category based on command prefix."""
    category_mapping = {
        'passwords': 'Authentication',
        'aaa': 'Authentication',
        'auth': 'Authentication',
        'login': 'Authentication',
        'nopassword': 'Authentication',
        'unlock': 'Authentication',
        'users': 'Authentication',
        'aging': 'Authentication',
        'lock-out': 'Authentication',
        'strength': 'Authentication',
        'show': 'Display',
        'poe': 'Power',
        'power': 'Power',
        'green-mode': 'Power',
        'enable': 'Privileged',
        'configure': 'Privileged',
        'do': 'Privileged',
        'set': 'Configuration',
        'clear': 'Configuration',
        'copy': 'Configuration',
        'delete': 'Configuration',
        'save': 'Configuration',
        'erase': 'Configuration',
        'reload': 'Configuration',
        'hostname': 'System',
        'environment': 'System',
        'errdisable': 'System',
        'tech-support': 'System',
        'snapshot': 'System',
        'logging': 'Logging',
        'eventlog': 'Logging',
        'console': 'Logging',
        'buffered': 'Logging',
        'wrap': 'Logging',
        'cli-command': 'Logging',
        'ping': 'Diagnostics',
        'traceroute': 'Diagnostics',
        'debug': 'Diagnostics',
        'capture': 'Diagnostics'
    }

    for prefix, category in category_mapping.items():
        if command_name.startswith(prefix):
            return category
    return 'Other'

def find_related_commands(command_name, all_commands, max_related=5):
    """Find related commands based on prefix similarity."""
    related = []
    for cmd in all_commands:
        if cmd != command_name:
            # Check for common prefix
            common_prefix = ""
            for i in range(min(len(command_name), len(cmd))):
                if command_name[i] == cmd[i]:
                    common_prefix += command_name[i]
                else:
                    break
            if len(common_prefix) >= 3:  # At least 3 characters in common
                related.append(cmd)
                if len(related) >= max_related:
                    break

            # If not enough prefix matches, use string similarity
            if len(related) < max_related:
                similarity = SequenceMatcher(None, command_name, cmd).ratio()
                if similarity > 0.6:  # 60% similarity threshold
                    if cmd not in related:
                        related.append(cmd)
                        if len(related) >= max_related:
                            break

    return related[:max_related]

def clean_commands():
    # Load the JSON file
    with open('command_references.json', 'r') as f:
        data = json.load(f)

    # Get list of all command names for related commands
    all_command_names = list(data.keys())

    # Normalize smart quotes and clean data
    cleaned = {}
    for key, val in data.items():
        if isinstance(val, dict) and 'syntax' in val and 'summary' in val and 'synopsis' in val:
            val['syntax'] = re.sub(r'[“”]', '"', val['syntax'])
            val['summary'] = re.sub(r'[“”]', '"', val['summary'])
            val['synopsis'] = re.sub(r'[“”]', '"', val['synopsis'])

            # Filter out invalid entries
            if val['summary'] != "No extraction found." and val['synopsis'] != "Manual review needed.":
                # Flag truncations
                if '(truncated' in val['synopsis']:
                    val['synopsis'] += ' [TRUNCATED]'

                # Add category
                val['category'] = get_category(key)

                # Add related commands
                val['related_commands'] = find_related_commands(key, all_command_names)

                cleaned[key] = val

    # Convert to list and sort by key
    command_list = [cleaned[key] for key in sorted(cleaned.keys())]

    # Save cleaned data
    with open('cleaned_commands.json', 'w') as f:
        json.dump(command_list, f, indent=2)

    print(f"Processed {len(command_list)} commands")

    # Print sample output
    if command_list:
        print("\nSample entries:")
        for i in range(min(3, len(command_list))):
            cmd = command_list[i]
            print(f"Command: {cmd.get('syntax', 'N/A')[:50]}...")
            print(f"Category: {cmd.get('category', 'N/A')}")
            print(f"Related: {cmd.get('related_commands', [])[:3]}")
            print()

if __name__ == "__main__":
    clean_commands()
