import sys
from pathlib import Path

# Add the `src` directory to Python's module search path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from src.utility_bill_processor.utility_proc import Utility_Bill_Processor

import glob
import ast

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def test_regression():
    total_differences = 0
    expected_values_path = "tests/expected"
    processor = Utility_Bill_Processor(output_dir="output/")
    filelist = glob.glob("tests/invoices/*.pdf")
    for i in range(len(filelist)):
        print("Processing file: " + filelist[i])

        try:
            parse_res   = processor.parse(filelist[i])
            schema      = processor.get_schema(parse_res.markdown)
            extract_res = processor.extract(parse_res.markdown, schema)
        except Exception as e:
            print("Error processing file " + filelist[i] + ": " + str(e))
            continue

     
        ext_values = extract_res.extraction
        print("{:<30} {:<30} {:<30} {:<10}".format('FIELD', 'VALUE', 'EXPECTED', 'RESULT'))

        expected_values_from_file = None
        exp_file = Path(expected_values_path + "/" + processor.get_filename() + ".exp")
        try:
            with open(Path(exp_file), 'r') as sc_file:
                expected_values_from_file = sc_file.read()
                sc_file.close()
        except FileNotFoundError as e:
            print("Error reading expected values from file: " + str(e))
            return
        expected_values = ast.literal_eval(expected_values_from_file)

        current_differences = 0
        for key, value in ext_values.items():
            if(value == None):
                value = "None"
            exp_value = expected_values[key]
            if(exp_value == None):
                exp_value = "None"

            values_match_c = u'\N{check mark}'
            if(value != exp_value):
                current_differences += 1
                total_differences += 1
                values_match_c = u'\N{cross mark}'
                print("{:<30} {:<30} {:<30} {:<10}".format(key, value, exp_value, values_match_c))
        print("\n")
        
    if(total_differences == 0):
        print(f"{bcolors.OKGREEN}Total Differences: {total_differences}{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}Total Differences: {total_differences}{bcolors.ENDC}")

