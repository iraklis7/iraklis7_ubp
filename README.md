# utility_bill_processor
This project uses the Landing.AI Python library to parse and extract data from Greek utility bills. This may be part of a larger workflow, that stores the extracted data in a database, in order to perform data analysis. Although the package was tested using greek utility bills, it should also work with foreign utility bills.

The package uses GitHub Actions for automated regression testing upon every push/pull event, as well as an automated CI/CD pipeline to build and publish the package to TestPyPi. If the publication is successful, then the package is also uploaded to PyPi. 

Please note that the VISION_AGENT_API_KEY environment variable must be set to the API key value in order for the Landing.AI python library to work.

A caching mechanism has been added (use_cache option), which instructs the processor to look for a corresponding parse/extract results file in the 'output' directory. These files are the JSON dumps of the Landing.AI client's responses during normal operation.
If use_cache is True and such a file is found, then the file contents are used by the processor, instead of calling the Landing.AI client. This is particularly useful during development, testing and demonstrations, since the flow is faster and no credits are consumed. 
The processor keeps an MD5 sum and the schema of all invoices processed, so it can automatically determine whether the cache is dirty and if so, try to use the Landing.AI client to fetch fresh results.

## Installation
You can install the package via pip:
pip install iraklis7_ubp