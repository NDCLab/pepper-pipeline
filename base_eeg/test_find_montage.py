from unittest import TestCase
from find_montage import get_montage

import json 

# instantiate test class
t = TestCase()
 
with open("base_eeg/test_json/task-matchingpennies_eeg.json", encoding="utf8") as file:
    # Assuming this should be standard_1020 from previous discussions 
    montage_pennies = "standard_1020"

    cap_json = json.load(file)
    montage_found = get_montage(cap_json) 

    t.assertEqual(montage_pennies, montage_found)

with open("base_eeg/test_json/task-facerecognition_eeg.json", encoding="utf8") as file:
    # Assuming this should be easycap-M1 since the file name is "Easycap EEG"
    montage_facerecog = "easycap-M1"

    cap_json = json.load(file)
    montage_found = get_montage(cap_json) 

    t.assertEqual(montage_facerecog, montage_found)

with open("base_eeg/test_json/task-rest_eeg.json", encoding="utf8") as file:
    # Assuming this should be easycap-M1 following encoding on 
    # https://www.fieldtriptoolbox.org/template/layout/#easycapm11---61-channel-arrangement-10-system-used-in-braincap64
    montage_rest = "easycap-M1"

    cap_json = json.load(file)
    montage_found = get_montage(cap_json) 

    t.assertEqual(montage_rest, montage_found)