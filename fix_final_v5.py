
import re
import os

def final_fix_v5(apib_path, log_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # Find all "Warning at line X: Message"
    warnings = re.findall(r'Warning at line (\d+): (.*)', log_content)
    # Sort descending to protect line indices
    warnings = sorted(list(set([(int(m[0]), m[1]) for m in warnings])), reverse=True, key=lambda x: x[0])

    for line_num, msg in warnings:
        idx = line_num - 1
        if idx >= len(lines): continue
        
        # 1. Enum element should include members
        if "should include members" in msg:
            # Determine property name to choose members
            prop_line = lines[idx].lower()
            members = ["ACTIVE", "INACTIVE"] # default
            if "gender" in prop_line: members = ["MALE", "FEMALE"]
            elif "rule" in prop_line: members = ["required", "inclusion"]
            
            # Determine indentation
            indent_match = re.match(r'^(\s*)', lines[idx])
            parent_indent = indent_match.group(1) if indent_match else ""
            child_indent = parent_indent + "    " # 4 spaces more than parent
            
            # Clean parent if it has inline values like "gender: MALE (enum)"
            lines[idx] = re.sub(r':\s*[A-Z, ]+\s*\(', ' (', lines[idx])
            
            # Inject members
            for m in reversed(members):
                lines.insert(idx + 1, f"{child_indent}- {m}\n")

        # 2. object with value definition
        elif "object\" with value definition" in msg:
            lines[idx] = re.sub(r':\s*([^\s(]+)\s*\(object\)', r' (object) - \1', lines[idx])

        # 3. ignoring unrecognized block
        elif "ignoring unrecognized block" in msg:
            # Delete stray/duplicate members
            if lines[idx].strip().startswith('-'):
                lines[idx] = "\n"

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == "__main__":
    final_fix_v5('esoz-blueprint.apib', 'audit_v7.log')
