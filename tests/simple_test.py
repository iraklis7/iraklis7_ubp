import sys
from pathlib import Path

# Add the `src` directory to Python's module search path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from utility_bill_processor.utility_proc import Utility_Bill_Processor

def simple_test():
    total_differences = 0
    invoices_path = "tests/invoices/"
    expected_values_path = "tests/expected"
    utility_bill = invoices_path + "ElectricityInvoice_2025-11-04.pdf"
    processor = Utility_Bill_Processor(output_dir="../output")


    print("Processing file: " + utility_bill)

    try:
        parse_res   = processor.parse(utility_bill)
        schema      = processor.get_schema(parse_res.markdown)
        extract_res = processor.extract(parse_res.markdown, schema)
    except Exception as e:
        print("Error processing file " + utility_bill + ": " + str(e))

    if(extract_res):
        ext_values = extract_res.extraction
        print("{:<30} {:<30} ".format('FIELD', 'VALUE'))
        for key, value in ext_values.items():
            print("{:<30} {:<30} ".format(key, value))

def main():
    simple_test()

if __name__ == "__main__":
    main()
