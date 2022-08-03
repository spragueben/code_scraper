## Usage
- This script is a python command line utility for populating a jupyter notebook with inline code examples and text from an inputted webpage, enabling code examples to be edited and run, and easily navigated-between using a generated table of contents
- The script prompts users to install chromedriver if it cannot detect that a) chromedriver is installed and b) in a location the kernel can access 

## Assumptions
- The program logic assumes that any provided website's code and markdown sections are differentiable by either a) their html tags, themselves, or b) the attributes on those tags

## Dependencies
- Selenium
- Chrome Driver
- bs4 / BeautifulSoup
- Markdownify (installed via pip)

## Instructions
- From the directory containing this script, activate a virtual environment with Markdownify installed, then run `python -m ./code_converter.py` in the command prompt. 
- Input prompts will request a url to scrape
- In order to identify and differentiate which of the provided webpage's data should be used to populate the code and markdown cells of the outputted notebook, input prompts will request which tags and, where necessary, which attributes should be used to differentiate code sections from markdown sections 
- If an alternate name is not provided for the notebook, a default filename will be applied
- If an alternate destination directory in not provided, the notebook will be outputted to the current working directory

## Future Improvements
- Assign the necessary metadata to format non-python code cells with the correct language
- Enable users to elect webdrivers for a variety of browsers