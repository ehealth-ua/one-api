
import re

def fix_blueprint_robustly(apib_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix "primitive types should not have nested members" by changing (string, enum) to (enum)
    # Pattern: (enum[string], required) or (string, enum, required)
    content = re.sub(r'\((?:string,\s*enum|enum\[string\])([^)]*)\)', r'(enum\1)', content)

    # 2. Fix "object with value definition"
    # Pattern: + key: value (object) -> + key (object) - value
    content = re.sub(r'(\+\s+[^:]+):\s*([^\s(]+)\s+\(object\)', r'\1 (object) - \2', content)

    # 3. Clean up malformed + Parameters sections
    # Ensure they have a blank line before them if preceded by text/headers
    content = re.sub(r'(###[^\n]+\n)\s*\+ Parameters', r'\1\n    + Parameters', content)

    # 4. Remove duplicate gender/status blocks that were inserted wrongly
    # (Checking for redundant MALE/FEMALE blocks without a parent)
    content = re.sub(r'(?m)^\s*- MALE\n\s*- FEMALE\n\s*(- MALE\n\s*- FEMALE\n)+', r'    - MALE\n    - FEMALE\n', content)

    # 5. Fix malformed URI templates where ?unique was added wrongly
    content = re.sub(r'\{([^}]+)\}\?unique_\d+', r'{\1,unique}', content)

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_blueprint_robustly('esoz-blueprint.apib')
