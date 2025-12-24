import os
import json
import logging
import sys
from pathlib import Path
from landingai_ade import LandingAIADE
from landingai_ade.lib import pydantic_to_json_schema
from landingai_ade.types.parse_response import ParseResponse
from landingai_ade.types.extract_response import ExtractResponse
from . import utility_model


class Utility_Bill_Processor(object):
    def __init__(self, env="eu", output_dir="./output", use_cache=False):
        self.__output_dir = output_dir
        self.__use_cache = use_cache
        self.__filename = ""
        # Create output directory if it doesn't exist
        self.__create_dir_if_not_exists(self.__output_dir)

        # Initialize ADE client
        self.__ade_client = LandingAIADE(
            apikey=os.environ.get("VISION_AGENT_API_KEY"),
            environment=env
        )

        # Set up logging
        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.DEBUG)
        self.__formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

        self.__stdout_handler = logging.StreamHandler(sys.stdout)
        self.__stdout_handler.setLevel(logging.INFO)
        self.__stdout_handler.setFormatter(self.__formatter)
        self.__file_handler = logging.FileHandler('iraklis7_ubp.log')
        self.__file_handler.setLevel(logging.DEBUG)
        self.__file_handler.setFormatter(self.__formatter)

        self.__logger.addHandler(self.__file_handler)
        self.__logger.addHandler(self.__stdout_handler)

    def get_filename(self):
        return self.__filename

    def __read_file(self, input_path):
        try:
            self.__logger.debug("Reading file: " + str(input_path))
            with open(input_path, 'r') as file:
                content = json.load(file)
                self.__logger.debug("File contents: " + str(content))
                file.close()
                return content
        except FileNotFoundError as e:
            print(str(e))
            raise

    def __create_dir_if_not_exists(self, path):
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.__logger.error("Creation of the directory " + path + " failed: " + str(e))
            raise

    def __write_file(self, output_path, content):
        try:
            self.__logger.debug("Writing file: " + str(output_path))
            self.__logger.debug("File contents: " + str(content))
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(content, file, ensure_ascii=False, indent=4)
                file.close()
        except OSError as e:
            self.__logger.error("Error writing to file " + str(output_path) + ": " + str(e))
            raise

    def __get_file_md5(self, input_path):
        import hashlib

        hash_md5 = hashlib.md5()
        try:
            with open(input_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            result = hash_md5.hexdigest()
            self.__logger.debug("Computed MD5 for file " + str(input_path) + ": " + result)
            return result
        except FileNotFoundError as e:
            self.__logger.error("Error computing MD5: " + str(e))
            raise

    def parse(self, input_path)->ParseResponse:
        # Store filename
        self.__filename = os.path.basename(input_path)

        response = None
        if(self.__use_cache):
            try:
                self.__logger.info("use_cache is enabled. Checking cache validity.")
                # Check to see if cache is dirty
                pout = Path(self.__output_dir + "/" + self.__filename + ".md5.json")
                self.__logger.debug("Retrieving cache MD5 for : " + str(pout))
                cached_md5 = self.__read_file(pout)
                actual_md5 = self.__get_file_md5(input_path)
                
                self.__logger.debug("Input file MD5: " + actual_md5)
                self.__logger.debug("Cached MD5: " + cached_md5['md5'])

                if(cached_md5['md5'] != actual_md5):
                    self.__logger.info("Cache is dirty. Will try to fetch fresh results.")
                    raise Exception("Cache is dirty")
                else:
                    self.__logger.info("Cache is valid, will read parse results from cache.")

                # If use_cache is True, read from cached markdown file
                pout = Path(self.__output_dir + "/" + self.__filename + ".parse.json")
                self.__logger.info("Using parse results from cache: " + str(pout))
                json_s = self.__read_file(pout)
                response = ParseResponse(**json_s)
                self.__logger.debug("Parse response from cache: " + str(response))
            except Exception as e:
                self.__logger.info("Cache miss: " + str(e))                
        if(self.__use_cache is False or response is None):
            try:
                self.__logger.info("use_cache is disabled or cache miss. Calling ADE parse API.")
                # ADE Client to Parse Utility bills and produce markdown
                response = self.__ade_client.parse(
                    # use document= for local files, document_url= for remote URLs
                    document=Path(input_path),
                    model="dpt-2-latest",
                )
                self.__logger.debug("Parse response from LandingAI ADE: " + str(response))

                # Write MD5 to file
                pout = Path(self.__output_dir + "/" + self.__filename + ".md5.json")
                actual_md5 = self.__get_file_md5(input_path)
                md5 = dict(md5=actual_md5)
                # Write MD5 to file
                self.__logger.debug("Writing MD5: " + actual_md5 + " to cache file: " + str(pout))
                self.__write_file(pout, md5)
                # Write parse response to file
                pout = Path(self.__output_dir + "/" + self.__filename + ".parse.json")
                self.__logger.debug("Writing parse response to file: " + str(pout))
                self.__write_file(pout, response)
            except Exception as e:
                self.__logger.error("Communication with the ADE server failed: " + str(e))
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
            self.__logger.warning("Unrecognized utility bill type. Defaulting to base Utility_Bill schema.")
        self.__logger.info("Determined bill type schema: " + str(bill_type))
        return pydantic_to_json_schema(bill_type)

    def extract(self, markdown, schema):
        # Use with the SDK
        # Convert markdown to structured data
        response = None
        if(self.__use_cache):
            try:
                self.__logger.info("use_cache is enabled. Checking cache validity.")
                # Check to see if cache is dirty
                pout = Path(self.__output_dir + "/" + self.__filename + ".schema.json")
                self.__logger.debug("Retrieving cached schema from : " + str(pout))
                cached_schema = self.__read_file(pout)
                actual_schema = json.loads(schema)

                self.__logger.debug("Input file schema: " + schema)
                self.__logger.debug("Cached schema: " + json.dumps(cached_schema)) 
                
                if(cached_schema != actual_schema):
                    self.__logger.info("Cache is dirty. Will try to fetch fresh results.")
                    raise Exception("Cache is dirty")
                else:
                    self.__logger.info("Cache is valid, will read extract results from cache.")
                # If use_cache is True, read from cached markdown file
                pout = Path(self.__output_dir + "/" + self.__filename + ".extract.json")
                self.__logger.info("Using extract results from cache: " + str(pout))
                json_s = self.__read_file(pout)
                response = ExtractResponse(**json_s)
                self.__logger.debug("Extract response from cache: " + str(response))
            except Exception as e:
                self.__logger.info("Cache miss: " + str(e))                
        if(self.__use_cache is False or response is None):
            try:
                self.__logger.info("use_cache is disabled or cache miss. Calling ADE parse API.")
                response = self.__ade_client.extract(
                    schema=schema,
                    # use markdown= for local files, markdown_url= for remote URLs
                    markdown=markdown,
                    model="extract-latest"
                )
                self.__logger.debug("Extract response from LandingAI ADE: " + str(response))

                # Write schema to file.
                pout = Path(self.__output_dir + "/" + self.__filename + ".schema.json")
                self.__logger.debug("Writing schema: " + schema + " to cache file: " + str(pout))
                self.__write_file(pout, json.loads(schema))
                # Write extract response to file.
                pout = Path(self.__output_dir + "/" + self.__filename + ".extract.json")
                self.__logger.debug("Writing extract response to cache file: " + str(pout))
                self.__write_file(pout, response)
            except Exception as e:
                self.__logger.error("Communication with the ADE server failed: " + str(e))
                raise

        return response
