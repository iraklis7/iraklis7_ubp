import os
import json
from pathlib import Path
from landingai_ade import LandingAIADE
from landingai_ade.lib import pydantic_to_json_schema
from landingai_ade.types.parse_response import ParseResponse
from landingai_ade.types.extract_response import ExtractResponse
from src.iraklis7_ubp import utility_model


class Utility_Bill_Processor(object):
    def __init__(self, env="eu", output_dir="./output", use_cache=False):
        self.__output_dir = output_dir
        self.__use_cache = use_cache
        self.__ade_client = LandingAIADE(
            apikey=os.environ.get("VISION_AGENT_API_KEY"),
            environment=env
        )
        self.__filename = ""
        # Create output directory if it doesn't exist
        self.__create_dir_if_not_exists(self.__output_dir)

    def get_filename(self):
        return self.__filename

    def __read_file(self, input_path):
        try:
            with open(input_path, 'r') as file:
                content = json.load(file)
                file.close()
                return content
        except FileNotFoundError as e:
            print(str(e))
            raise

    def __create_dir_if_not_exists(self, path):
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print("Creation of the directory failed: " + str(e))
            raise

    def __write_file(self, output_path, content):
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(content, file, ensure_ascii=False, indent=4)
                file.close()
        except OSError as e:
            print("Error writing to file: " + str(e))
            raise

    def parse(self, input_path)->ParseResponse:
        # Store filename
        self.__filename = os.path.basename(input_path)

        response = None
        if(self.__use_cache):
            try:
                # If use_cache is True, read from cached markdown file
                pout = Path(self.__output_dir + "/" + self.__filename + ".parse.json")
                print("Using parse results from cache: " + str(pout))
                json_s = self.__read_file(pout)
                response = ParseResponse(**json_s)
            except Exception as e:
                print("Cache miss: " + str(e))                
        if(self.__use_cache is False or response is None):
            try:
                # ADE Client to Parse Utility bills and produce markdown
                response = self.__ade_client.parse(
                    # use document= for local files, document_url= for remote URLs
                    document=Path(input_path),
                    model="dpt-2-latest",
                )
                pout = Path(self.__output_dir + "/" + self.__filename + ".parse.json]")
                self.__write_file(pout, response)
            except Exception as e:
                print("Communication with the ADE server failed: " + str(e))
                raise
    
        return response

    def get_schema(self, markdown):
        bill_type = None
        if "ΠΡΟΜΗΘΕΙΑ ΦΥΣΙΚΟΥ ΑΕΡΙΟΥ" in markdown:
            bill_type = utility_model.Utility_Bill_Gas
        elif "ΛΟΓΑΡΙΑΣΜΟΣ ΗΛΕΚΤΡΙΚΟΥ ΡΕΥΜΑΤΟΣ" in markdown:
            bill_type = utility_model.Utility_Bill_Power
        elif "Ύδρευσης" in markdown:
            bill_type = utility_model.Utility_Bill_Water
        else:
            bill_type = utility_model.Utility_Bill
            print("Unrecognized utility bill type. Defaulting to base Utility_Bill schema.")
        return pydantic_to_json_schema(bill_type)

    def extract(self, markdown, schema):
        # Use with the SDK
        # Convert markdown to structured data
        response = None
        if(self.__use_cache):
            try:
                # If use_cache is True, read from cached markdown file
                pout = Path(self.__output_dir + "/" + self.__filename + ".extract.json")
                print("Using parse results from cache: " + str(pout))
                json_s = self.__read_file(pout)
                response = ExtractResponse(**json_s)
            except Exception as e:
                print("Cache miss: " + str(e))                
        if(self.__use_cache is False or response is None):
            try:
                response = self.__ade_client.extract(
                    schema=schema,
                    # use markdown= for local files, markdown_url= for remote URLs
                    markdown=markdown,
                    model="extract-latest"
                )
                # Write extract response to file.
                pout = Path(self.__output_dir + "/" + self.__filename + ".extract.json")
                self.__write_file(pout, response)
            except Exception as e:
                print("Communication with the ADE server failed: " + str(e))
                raise

        return response
