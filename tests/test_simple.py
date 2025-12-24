from src.iraklis7_ubp.utility_proc import Utility_Bill_Processor


def test_simple():
    invoices_path = "tests/invoices/"
    utility_bill = invoices_path + "GasInvoice_2025-12-04.pdf"
    # utility_bill = invoices_path + "AKN32864488.pdf"
    processor = Utility_Bill_Processor(env="eu", output_dir="output/", use_cache=True)

    print("Processing file: " + utility_bill)
    extract_res = None

    try:
        parse_res = processor.parse(utility_bill)
        schema = processor.get_schema(parse_res.markdown)    
        extract_res = processor.extract(parse_res.markdown, schema)
    except Exception as e:
        print("Error processing file " + utility_bill + ": " + str(e))

    if (extract_res):
        ext_values = extract_res.extraction
        print("{:<30} {:<30} ".format('FIELD', 'VALUE'))
        for key, value in ext_values.items():
            print("{:<30} {:<30} ".format(key, value))

if __name__ == '__main__':
    test_simple()