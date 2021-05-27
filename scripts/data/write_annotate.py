import json
import sys

def read_dict_to_json(dict_array):
    if dict_array is None:
        print("Invalid dictionary array",file=sys.stderr)
        sys.exit(1)

    with open('output_preproc.json', 'w') as file:
        str=json.dumps(dict_array,indent=4)
        file.seek(0)
        file.write(str)