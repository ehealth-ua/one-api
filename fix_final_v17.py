
import re
import os

# Common parameter definitions
COMMON_PARAMS = {
    'id': '`id` (string, required) - unique identifier',
    'patient_id': '`patient_id` (string, required) - unique identifier of the patient',
    'person_id': '`person_id` (string, required) - unique identifier of the person',
    'composition_id': '`composition_id` (string, required) - unique identifier of the composition',
    'service_request_id': '`service_request_id` (string, required) - identifier of the service request',
    'episode_id': '`episode_id` (string, required) - identifier of the episode',
    'contract_type': '`contract_type` (string, required) - identifier of the contract type',
}

def final_fix_v17(apib_path):
    with open(apib_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into action blocks
    # We look for ### header and go until the next ### or ## header
    blocks = re.split(r'(\n###\s+[^\n]+\[[A-Z]+\s+[^\]]+\])', content)
    
    new_content = [blocks[0]]
    for i in range(1, len(blocks), 2):
        header = blocks[i]
        body = blocks[i+1] if i+1 < len(blocks) else ""
        
        # Extract variables from URI template in header: [GET /path/{id}{?p1,p2}]
        uri_match = re.search(r'\[[A-Z]+\s+([^\]]+)\]', header)
        if uri_match:
            uri = uri_match.group(1)
            # Find all {var} and {?var1,var2}
            vars_found = re.findall(r'\{([^{}]+)\}', uri)
            params_needed = []
            for v_group in vars_found:
                clean_vars = v_group.replace('?', '').split(',')
                for cv in clean_vars:
                    params_needed.append(cv.strip().split('_unique')[0].split('_duplicate')[0].strip())
            
            if params_needed:
                # Does + Parameters section exist in this body?
                if "+ Parameters" not in body:
                    # Inject it at the start of body
                    # Find first blank line or start
                    body = "\n    + Parameters\n" + body
                
                # Ensure every param is present in the block
                p_match = re.search(r'\+ Parameters(.*?)(?=\n[#\+]|\Z)', body, flags=re.DOTALL)
                if p_match:
                    p_block = p_match.group(0)
                    for p_name in params_needed:
                        if f"`{p_name}`" not in p_block:
                            p_line = COMMON_PARAMS.get(p_name, f"`{p_name}` (string, required) - identifier")
                            # Insert after + Parameters
                            body = body.replace("+ Parameters", f"+ Parameters\n        + {p_line}")
        
        new_content.append(header)
        new_content.append(body)

    final_str = "".join(new_content)
    
    # Global Cleanup: Object with value definitions
    final_str = re.sub(r'(\+\s+[^:]+):\s*([^\s(]+)\s+\(object\)', r'\1 (object) - \2', final_str)

    with open(apib_path, 'w', encoding='utf-8') as f:
        f.write(final_str)

if __name__ == "__main__":
    final_fix_v17('esoz-blueprint.apib')
