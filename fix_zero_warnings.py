
import re
import os

def fix_blueprint_nuclear(apib_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 1. Strip corrupted URI markers: {?id}?unique_123 -> {?id}
        line = re.sub(r'(\{[^}]+\})\?unique_\d+', r'\1', line)
        line = re.sub(r'(\{[^}]+\})\?duplicate_src_\d+', r'\1', line)
        line = re.sub(r'(\{[^}]+\})\?duplicate_\d+', r'\1', line)
        # Handle multiple markers
        line = re.sub(r'(\?unique_\d+|\?duplicate_src_\d+)+', '', line)
        
        # 2. Deduplicate parameters within the SAME block
        if "+ Parameters" in line:
            new_lines.append(line)
            seen_params = set()
            j = i + 1
            while j < len(lines) and lines[j].startswith("        +"):
                p_line = lines[j]
                p_match = re.search(r'`([^`]+)`', p_line)
                if p_match:
                    p_name = p_match.group(1).split('_unique')[0].split('_duplicate')[0].strip()
                    if p_name not in seen_params:
                        # Re-normalize indentation and name
                        new_lines.append(f"        + `{p_name}` (string, required) - unique identifier\n")
                        seen_params.add(p_name)
                j += 1
            i = j
            continue

        # 3. Fix Object with Value
        if " (object) -" not in line: # Don't double fix
            line = re.sub(r'(\+\s+[^:]+):\s*([^\s(]+)\s+\(object\)', r'\1 (object) - \2', line)

        # 4. Remove orphan MALE/FEMALE blocks (no spaces)
        if line.strip() in ["- MALE", "- FEMALE", "- ACTIVE", "- INACTIVE"] and not line.startswith("    "):
            i += 1
            continue

        new_lines.append(line)
        i += 1

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    fix_blueprint_nuclear('esoz-blueprint.apib')
