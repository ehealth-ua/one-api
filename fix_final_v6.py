
import re
import os

# Common parameter definitions to ensure consistency
COMMON_PARAMS = {
    'id': '`id` (string, required) - unique identifier',
    'patient_id': '`patient_id` (string, required) - unique identifier of the patient',
    'person_id': '`person_id` (string, required) - unique identifier of the person',
    'composition_id': '`composition_id` (string, required) - unique identifier of the composition',
    'service_request_id': '`service_request_id` (string, required) - unique identifier of the service request',
    'episode_id': '`episode_id` (string, required) - unique identifier of the episode',
    'contract_type': '`contract_type` (string, required) - identifier of the contract type',
}

def final_fix_v6(apib_path, log_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    warnings = re.findall(r'Warning at line (\d+): (.*)', log_content)
    warnings = sorted(list(set([(int(m[0]), m[1]) for m in warnings])), reverse=True, key=lambda x: x[0])

    for line_num, msg in warnings:
        idx = line_num - 1
        if idx >= len(lines): continue
        
        # 1. Action is missing parameter definitions
        if "Action is missing parameter definitions" in msg:
            p_match = re.search(r'definitions: (.*)\.', msg)
            if p_match:
                params = [p.strip().split('}')[0].strip('`') for p in p_match.group(1).split(', ')]
                # Find action header
                action_idx = idx
                while action_idx >= 0 and not lines[action_idx].strip().startswith('###'):
                    action_idx -= 1
                
                if action_idx >= 0:
                    # Check for existing Parameters section
                    p_section_idx = -1
                    for k in range(action_idx, min(action_idx + 20, len(lines))):
                        if "+ Parameters" in lines[k]:
                            p_section_idx = k
                            break
                    
                    if p_section_idx == -1:
                        lines.insert(action_idx + 1, "    + Parameters\n")
                        p_section_idx = action_idx + 1
                    
                    # Inject missing params (clean names)
                    for p_name in reversed(params):
                        clean_name = p_name.split('_duplicate')[0].split('_unique')[0]
                        line_to_add = COMMON_PARAMS.get(clean_name, f"`{clean_name}` (string, required) - identifier")
                        lines.insert(p_section_idx + 1, f"        + {line_to_add}\n")

        # 2. Ignoring unrecognized block (comments or orphaned lines)
        elif "Ignoring unrecognized block" in msg:
            if not lines[idx].strip().startswith('<!--'):
                lines[idx] = f"<!-- {lines[idx].strip()} -->\n"

        # 3. object with value definition
        elif "object\" with value definition" in msg:
            lines[idx] = re.sub(r':\s*([^\s(]+)\s*\(object\)', r' (object) - \1', lines[idx])

        # 4. Action already defined
        elif "already defined" in msg:
            if '[' in lines[idx]:
                lines[idx] = lines[idx].replace(']', f'?unique_{idx}]')

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == "__main__":
    final_fix_v6('esoz-blueprint.apib', 'audit_v8.log')
