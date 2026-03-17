
import re
import os

# Common parameters to inject if missing
COMMON_PARAMS = {
    'id': '`id` (string, required) - unique identifier',
    'patient_id': '`patient_id` (string, required) - unique identifier of the patient',
    'service_request_id': '`service_request_id` (string, required) - unique identifier of the service request',
    'episode_id': '`episode_id` (string, required) - unique identifier of the episode',
    'person_id': '`person_id` (string, required) - unique identifier of the person',
    'composition_id': '`composition_id` (string, required) - unique identifier of the composition',
    'contract_type': '`contract_type` (string, required) - type of contract',
}

def fix_blueprint_surgical(apib_path, log_path):
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
        
        # 1. primitive types enums: sub-types of primitive types should not have nested members
        if "sub-types of primitive types" in msg:
            # Change (enum[string], required) -> (enum, required) OR (string, enum) -> (enum)
            lines[idx] = re.sub(r'\(enum\[[^\]]+\]', '(enum', lines[idx])
            lines[idx] = re.sub(r'\(string, enum\)', '(enum)', lines[idx])

        # 2. object with value definition
        elif "object\" with value definition" in msg:
            # + key: value (object) -> + key (object) - value
            lines[idx] = re.sub(r':\s*([^\s(]+)\s*\(object\)', r' (object) - \1', lines[idx])

        # 3. Action missing parameter definitions
        elif "Action is missing parameter definitions" in msg:
            p_match = re.search(r'definitions: (.*)\.', msg)
            if p_match:
                params = p_match.group(1).split(', ')
                # Find the action header to inject Parameters after it
                action_idx = idx
                while action_idx >= 0 and not lines[action_idx].strip().startswith('###'):
                    action_idx -= 1
                
                if action_idx >= 0:
                    # Find if + Parameters already exists
                    params_idx = -1
                    for k in range(action_idx, min(action_idx + 20, len(lines))):
                        if "+ Parameters" in lines[k]:
                            params_idx = k
                            break
                    
                    if params_idx == -1:
                        # Inject section
                        lines.insert(action_idx + 1, "    + Parameters\n")
                        params_idx = action_idx + 1
                        shift = 2
                    else:
                        shift = 1
                    
                    for i, p in enumerate(params):
                        p_name = p.strip()
                        # Clean duplicate markers from name
                        p_name_clean = p_name.split('}')[0].split('_unique')[0].split('_duplicate')[0].strip('`')
                        
                        # Already in section?
                        found = False
                        for k in range(params_idx, min(params_idx + 30, len(lines))):
                            if f"`{p_name_clean}`" in lines[k]:
                                found = True
                                break
                        
                        if not found:
                            p_line = COMMON_PARAMS.get(p_name_clean, f"`{p_name_clean}` (string, required) - identifier")
                            lines.insert(params_idx + 1, f"        + {p_line}\n")

        # 4. Action already defined
        elif "already defined" in msg:
            if '[' in lines[idx]:
                # Append unique path marker
                lines[idx] = lines[idx].replace(']', f'?unique_{idx}]')

        # 5. Ignoring unrecognized block (comments or orphaned text)
        elif "Ignoring unrecognized block" in msg:
            # Wrap in comment if not already
            if not lines[idx].strip().startswith('<!--'):
                lines[idx] = f"<!-- {lines[idx].strip()} -->\n"

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == "__main__":
    fix_blueprint_surgical('esoz-blueprint.apib', 'warnings_v2.txt')
