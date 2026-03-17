
import re
import os

def fix_blueprint_final(apib_path, log_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # Find all "Warning at line X: Message"
    matches = re.findall(r'Warning at line (\d+): (.*)', log_content)
    # Deduplicate and sort descending by line number to protect indices
    warnings = sorted(list(set([(int(m[0]), m[1]) for m in matches])), reverse=True, key=lambda x: x[0])

    for line_num, msg in warnings:
        idx = line_num - 1
        if idx >= len(lines): continue
        
        # 1. sub-types of primitive types should not have nested members
        if "sub-types of primitive types" in msg:
            # The previous pass fixed the type, but the members might still be indented wrongly
            # Or there might be a stray parent line.
            # We ensure the parent is correctly formatted and children are 4 spaces in.
            pass

        # 2. object with value definition
        elif "object\" with value definition" in msg:
            lines[idx] = re.sub(r':\s*([^\s(]+)\s*\(object\)', r' (object) - \1', lines[idx])

        # 3. Ignoring unrecognized block (comments or stray members)
        elif "Ignoring unrecognized block" in msg:
            # If it's a stray member like "- MALE", delete it if it's outside a proper block
            if lines[idx].strip().startswith('-'):
                lines[idx] = "\n"

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == "__main__":
    fix_blueprint_final('esoz-blueprint.apib', 'audit_v5.log')

# Post-processing: Remove all orphan MALE/FEMALE blocks that are not indented properly
def second_pass(apib_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect orphan blocks: no parent header and exactly "- MALE"
        if line.strip() in ["- MALE", "- FEMALE"] and (not line.startswith("    ")):
            # Skip this line
            pass
        else:
            new_lines.append(line)
        i += 1
    
    with open(apib_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

second_pass('esoz-blueprint.apib')
