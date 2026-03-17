
import re
import os

COMMON_PARAMS = {
    'id': '`id` (string, required) - unique identifier',
    'patient_id': '`patient_id` (string, required) - unique identifier of the patient',
    'service_request_id': '`service_request_id` (string, required) - unique identifier of the service request',
    'composition_id': '`composition_id` (string, required) - unique identifier of the composition',
    'episode_id': '`episode_id` (string, required) - unique identifier of the episode',
    'person_id': '`person_id` (string, required) - unique identifier of the person',
    'parent_id': '`parent_id` (string, required) - unique identifier of the parent resource',
    'encounter_id': '`encounter_id` (string, required) - unique identifier of the encounter',
    'contract_type': '`contract_type` (string, required) - type of contract',
    'duplicate': '`duplicate` (string, optional) - duplicate marker',
    'duplicate_1': '`duplicate_1` (string, optional) - duplicate marker',
    'page': '`page` (number, optional) - page number',
    'page_size': '`page_size` (number, optional) - page size',
    'date': '`date` (string, optional) - date',
    'date_from': '`date_from` (string, optional) - start date',
    'date_to': '`date_to` (string, optional) - end date',
    'period_from': '`period_from` (string, optional) - start of period',
    'period_to': '`period_to` (string, optional) - end of period',
    'legal_entity_id': '`legal_entity_id` (string, required) - identifier of legal entity',
    'birth_place': '`birth_place` (string, optional) - place of birth',
    'context_episode_id': '`context_episode_id` (string, optional) - context episode id',
    'initial_episode_id': '`initial_episode_id` (string, optional) - initial episode id',
    'care_plan_id': '`care_plan_id` (string, required) - identifier of care plan',
    'diagnostic_report_id': '`diagnostic_report_id` (string, required) - identifier of diagnostic report',
}

def fix_from_warnings(apib_path, log_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # Parse warnings like "Line 415: Enum element ..."
    warnings = re.findall(r'Line (\d+): (.*)', log_content)
    
    # Sort descending to avoid line shift issues when inserting lines
    # We use (int(line), msg) and reverse=True
    warnings = sorted([(int(line), msg) for line, msg in warnings], reverse=True, key=lambda x: x[0])

    for line_num, msg in warnings:
        idx = line_num - 1
        if idx >= len(lines): continue
        
        # 1. Action missing parameter definitions
        if "Action is missing parameter definitions" in msg:
            params_match = re.search(r'definitions: (.*)\.', msg)
            if params_match:
                params = params_match.group(1).split(', ')
                # Find the action header preceding this line to insert Parameters after it
                # Or just insert after the line if it IS the action header
                insert_idx = idx + 1
                # Check if next lines already have Parameters (unlikely but safe)
                has_params = False
                for k in range(idx, min(idx + 10, len(lines))):
                    if "+ Parameters" in lines[k]:
                        has_params = True
                        break
                
                if not has_params:
                    # Determine indentation
                    indent_match = re.match(r'^(\s*)', lines[idx])
                    base_indent = indent_match.group(1) if indent_match else "    "
                    # If lines[idx] is a header like ###, then indent for parameters is 4 spaces
                    if lines[idx].strip().startswith('#'):
                        base_indent = "    "
                    
                    param_block = [f"\n{base_indent}+ Parameters\n"]
                    for p in params:
                        p_clean = p.strip()
                        p_desc = COMMON_PARAMS.get(p_clean, f"`{p_clean}` (string, required) - identifier")
                        param_block.append(f"{base_indent}    + {p_desc}\n")
                    lines[insert_idx:insert_idx] = param_block

        # 2. Enum should include members
        elif "should include members" in msg:
            # Inject members
            term_match = re.search(r'Enum element "(.*)"', msg)
            if term_match:
                term = term_match.group(1).lower()
                members = []
                if "gender" in term: members = ["MALE", "FEMALE"]
                elif "status" in term: members = ["ACTIVE", "INACTIVE"]
                elif "rule" in term: members = ["required", "inclusion"]
                else: members = [term.upper() + "_1", term.upper() + "_2"]
                
                # Check for existing members
                has_m = False
                for k in range(idx + 1, min(idx + 5, len(lines))):
                    if lines[k].strip().startswith('-'):
                        has_m = True
                        break
                if not has_m:
                    indent_match = re.match(r'^(\s*)', lines[idx])
                    indent = indent_match.group(1) if indent_match else "        "
                    # Clean the parent line of inline values
                    lines[idx] = re.sub(r':\s*[A-Z, ]+\s*\(', ' (', lines[idx])
                    for m in members:
                        lines.insert(idx + 1, f"{indent}    - {m}\n")

        # 3. Object with value definition
        elif "\"object\" with value definition" in msg:
            # Change + key: value (object) -> + key (object) - value
            match = re.match(r'^(\s*\+\s*)([^:(]+):\s*([^:(]+)\s*\(object\)(.*)$', lines[idx])
            if match:
                indent, name, val, rest = match.groups()
                lines[idx] = f"{indent}{name.strip()} (object) - {val.strip()}{rest}\n"

        # 4. Action already defined
        elif "already defined" in msg:
            # Multi-part uniqueness: append line number to path
            if '[' in lines[idx] and ']' in lines[idx]:
                lines[idx] = lines[idx].replace(']', f'?duplicate_src_{line_num}]')

        # 5. Type attribute "required" is not allowed for a value of type "object"
        elif "required\" is not allowed for a value of type \"object\"" in msg:
            lines[idx] = lines[idx].replace(', required', '')

        # 6. Invalid value format (quotes)
        elif "Invalid value format" in msg:
            lines[idx] = re.sub(r"(['\"])([0-9.]+)\1", r"\2", lines[idx])

        # 7. No name specified: "(Coding)"
        elif "No name specified: \"(Coding)\"" in msg:
            # Change (Coding) to coding (Coding) if it's a member
            lines[idx] = lines[idx].replace('(Coding)', 'coding (Coding)')

        # 8. sub-types of primitive types (family doctor)
        elif "sub-types of primitive types should not have nested members" in msg:
            # Usually happens when we have a string but it has members under it
            # Change (string) to (enum) or (object)
            lines[idx] = lines[idx].replace('(string)', '(enum)')

        # 9. Ignoring unrecognized block (comments, headers)
        elif "Ignoring unrecognized block" in msg:
            if not lines[idx].strip().startswith('<!--'):
                lines[idx] = f"<!-- {lines[idx].strip()} -->\n"

        # 10. Action is missing a response
        elif "Action is missing a response" in msg:
            # Inject a default 200 response if it's an action line
            if lines[idx].strip().startswith('###'):
                lines.insert(idx + 1, "\n    + Response 200 (application/json)\n")

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == "__main__":
    fix_from_warnings('esoz-blueprint.apib', 'warnings.txt')
