
import re
import os

def final_fix(apib_path, log_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # Get warnings
    warnings = re.findall(r'Warning at line (\d+): (.*)', log_content)
    warnings = sorted(list(set([(int(m[0]), m[1]) for m in warnings])), reverse=True, key=lambda x: x[0])

    for line_num, msg in warnings:
        idx = line_num - 1
        if idx >= len(lines): continue
        
        # indent check
        indent_match = re.match(r'^(\s*)', lines[idx])
        curr_indent = indent_match.group(1) if indent_match else ""

        # 1. object with value definition
        if "object\" with value definition" in msg:
            lines[idx] = re.sub(r':\s*([^\s(]+)\s*\(object\)', r' (object) - \1', lines[idx])

        # 2. sub-types of primitive types
        elif "sub-types of primitive types" in msg:
            # We already fixed (enum), so the issue is likely the stray child blocks
            # We will handle this by deleting the children if they are erroneously placed
            pass

        # 3. ignoring unrecognized block
        elif "ignoring unrecognized block" in msg:
            # Delete stray members like "- MALE"
            if lines[idx].strip().startswith('-'):
                lines[idx] = "\n"

    # Second cleanup: Remove orphan MALE/FEMALE lines
    # And fix indentation of real ones to be parent+8
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        line_s = line.strip()
        
        if line_s in ["- MALE", "- FEMALE", "- ACTIVE", "- INACTIVE"]:
            # Check previous line
            prev = fixed_lines[-1] if fixed_lines else ""
            if "(enum" in prev:
                # Keep it and indent correctly (parent indent + 8)
                p_indent = re.match(r'^(\s*)', prev).group(1)
                fixed_lines.append(p_indent + "        " + line_s + "\n")
            else:
                # Orphaned, toss it
                pass
        else:
            fixed_lines.append(line)
        i += 1

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

if __name__ == "__main__":
    final_fix('esoz-blueprint.apib', 'audit_v6.log')
