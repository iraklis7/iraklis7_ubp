from pathlib import Path
from src.utility_bill_processor.utility_proc import Utility_Bill_Processor

def simple_test():
    total_differences = 0
    invoices_path = "./invoices/"
    expected_values_path = "./expected"
    utility_bill = invoices_path + "ElectricityInvoice_2025-11-04.pdf"
    processor = Utility_Bill_Processor(output_dir="../output")


    print("Processing file: " + utility_bill)

    try:
        parse_res   = processor.parse(utility_bill)
        schema      = processor.get_schema(parse_res.markdown)
        extract_res = processor.extract(parse_res.markdown, schema)
    except Exception as e:
        print("Error processing file " + utility_bill + ": " + str(e))
        exit(1)

    ext_values = extract_res.extraction
    print("{:<30} {:<30} ".format('FIELD', 'VALUE'))
    for key, value in ext_values.items():
        print("{:<30} {:<30} ".format(key, value))

def main():
    simple_test()

if __name__ == "__main__":
    main()
