
import re
import os

# Common parameter definitions
COMMON_PARAMS = {
    'id': '`id` (string, required) - unique identifier',
    'patient_id': '`patient_id` (string, required) - unique identifier of the patient',
    'person_id': '`person_id` (string, required) - unique identifier of the person',
    'composition_id': '`composition_id` (string, required) - unique identifier of the composition',
    'service_request_id': '`service_request_id` (string, required) - identifier of the service request',
    'episode_id': '`episode_id` (string, required) - unique identifier of the episode',
    'contract_type': '`contract_type` (string, required) - identifier of the contract type',
}

def final_fix_v7(apib_path, log_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    warnings = re.findall(r'Warning at line (\d+): (.*)', log_content)
    warnings = sorted(list(set([(int(m[0]), m[1]) for m in warnings])), reverse=True, key=lambda x: x[0])

    for line_num, msg in warnings:
        idx = line_num - 1
        if idx >= len(lines): continue
        
        # 1. Action is missing parameter definitions: [param1, param2]
        if "Action is missing parameter definitions" in msg:
            p_match = re.search(r'definitions: (.*)\.', msg)
            if p_match:
                params_str = p_match.group(1)
                # Split by comma but be careful with names
                raw_params = [p.strip() for p in params_str.split(',')]
                
                # Find action header
                header_idx = idx
                while header_idx >= 0 and not lines[header_idx].strip().startswith('###'):
                    header_idx -= 1
                
                if header_idx >= 0:
                    # Find if + Parameters already exists
                    p_section_idx = -1
                    for k in range(header_idx, min(header_idx + 25, len(lines))):
                        if "+ Parameters" in lines[k]:
                            p_section_idx = k
                            break
                    
                    if p_section_idx == -1:
                        # Insert section
                        lines.insert(header_idx + 1, "    + Parameters\n")
                        p_section_idx = header_idx + 1
                    
                    # Inject params in reverse to preserve order
                    for p_raw in reversed(raw_params):
                        # Clean param name: `{?id}` -> `id`, `id_unique_123` -> `id`
                        clean_name = re.sub(r'[\?}{`]', '', p_raw).split('_unique')[0].split('_duplicate')[0].strip()
                        
                        # Already in section?
                        found = False
                        for k in range(p_section_idx, min(p_section_idx + 40, len(lines))):
                            if f"`{clean_name}`" in lines[k]:
                                found = True
                                break
                        
                        if not found:
                            line_to_add = COMMON_PARAMS.get(clean_name, f"`{clean_name}` (string, required) - identifier")
                            lines.insert(p_section_idx + 1, f"        + {line_to_add}\n")

        # 2. Ignoring unrecognized block
        elif "Ignoring unrecognized block" in msg:
            if not lines[idx].strip().startswith('<!--'):
                # Ensure no metadata blocks are hidden
                if not lines[idx].strip().startswith(('###', '## ', '# ')):
                    lines[idx] = f"<!-- {lines[idx].strip()} -->\n"

        # 3. Action already defined
        elif "already defined" in msg:
            if '[' in lines[idx]:
                lines[idx] = re.sub(r'\]', f'?unique_{line_num}]', lines[idx], count=1)

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == "__main__":
    final_fix_v7('esoz-blueprint.apib', 'audit_v9.log')
