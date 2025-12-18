import os
from landingai_ade import LandingAIADE
from landingai_ade.lib import pydantic_to_json_schema
#from utility_model import Utility_Bill, Utility_Bill_Gas, Utility_Bill_Power, Utility_Bill_Water
from .utility_model import Utility_Bill, Utility_Bill_Gas, Utility_Bill_Power, Utility_Bill_Water
from pathlib import Path

class Utility_Bill_Processor(object) :
    def __init__(self, output_dir="./output"):
        self.__output_dir           = output_dir
        self.__ade_client           = LandingAIADE(
            apikey=os.environ.get("VISION_AGENT_API_KEY"),
            environment="eu"
        )
        self.__filename             = ""
    
    def get_filename(self):
        return self.__filename
    
    def parse(self, input_path) :    
        # Store filename
        self.__filename = os.path.basename(input_path)
        
        try:
            with open(input_path, 'r') as file:
                file.close()
            #Path(input_path).is_file()
        except FileNotFoundError as e:
            print(str(e))
            raise
            
        # ADE Client to Parse Utility bills and produce markdown
        try:
            response = self.__ade_client.parse(
                # use document= for local files, document_url= for remote URLs
                document=Path(input_path),
                model="dpt-2-latest",
            )
        except Exception as e:
            print("Communication with the ADE server failed: " + str(e))
            raise

        # Create output directory if it doesn't exist
        try:
            Path(self.__output_dir).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print("Creation of the output directory failed: " + str(e))
            raise

        # Write parse response to file.
        pout = Path(self.__output_dir + "/" + self.__filename + ".parse")
        try:
            with open(Path(pout), 'w') as sc_file:
                sc_file.write("===================== Response Markdown   =====================\n")
                sc_file.write(response.markdown + "\n")
                sc_file.write("===================== Response Chunks   =====================\n")
                for i in range(len(response.chunks)):
                    sc_file.write("----- Chunk " + str(i) + " -----\n")
                    sc_file.write(str(response.chunks[i]))
                sc_file.close()
        except OSError as e:
            print("Error writing parse output to file: " + str(e))

        return response
        
    def get_schema(self, markdown) :
        bill_type = None
        if "ΠΡΟΜΗΘΕΙΑ ΦΥΣΙΚΟΥ ΑΕΡΙΟΥ" in markdown:
            bill_type = Utility_Bill_Gas
        elif "ΛΟΓΑΡΙΑΣΜΟΣ ΗΛΕΚΤΡΙΚΟΥ ΡΕΥΜΑΤΟΣ" in markdown:
            bill_type = Utility_Bill_Power
        elif "Ύδρευσης" in markdown:
            bill_type = Utility_Bill_Water 
        else:
            bill_type = Utility_Bill
            print("Unrecognized utility bill type. Defaulting to base Utility_Bill schema.")
        return pydantic_to_json_schema(bill_type) 

    def extract(self, markdown, schema) :
        # Use with the SDK
        # Convert markdown to structured data
        try:
            response = self.__ade_client.extract(
                schema=schema,
                # use markdown= for local files, markdown_url= for remote URLs
                markdown=markdown,
                model="extract-latest"
            )
        except Exception as e:
            print("Communication with the ADE server failed: " + str(e))
            raise

        eout = Path(self.__output_dir + "/" + self.__filename + ".extract")

        # Write extracted response to file.
        try:
            with open(Path(eout), 'w') as sc_file:
                sc_file.write("===================== Response Extraction   =====================\n")
                sc_file.write(str(response.extraction) + "\n")
                sc_file.write("===================== Response Metadata     =====================\n")
                sc_file.write(str(response.metadata) + "\n")
                sc_file.write("===================== Response Ext Metadata =====================\n")
                sc_file.write(str(response.extraction_metadata) + "\n")
                sc_file.close()
        except FileNotFoundError as e:
            print("Error writing extract output to file: " + str(e))

        return response
    