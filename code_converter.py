# 2023.09.26 09:45PM

# Filename: code_converter.ipynb
# Author: Ben Sprague

#%%
# DEPENDENCIES
import os
import re
import sys
import html
import json
import string
import random
import shutil
import platform
import subprocess
import webbrowser
import urllib.request
import chromedriver_autoinstaller

from tkinter import Tk
from functools import reduce
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from configparser import DEFAULTSECT
from markdownify import markdownify as md

#%%
# EXAMPLES
examples_dict = {
    'uwisc'     : ['A review of data analysis libraries, courtesy of University of Wisconsin',r'https://icecube.wisc.edu/~icecube-bootcamp/bootcamp2018/Bootcamp_Tutorial_Part4.html'],
    'howison'   : ['An FAQ on data wrangling',r'https://howisonlab.github.io/datawrangling/faq.html'],
    'remap'     : ["A rare explainer on recursive mapping using the 'remap' module from Python's boltons library",r"https://sedimental.org/remap.html"],
    'py2neo'    : ['An example case of using the py2neo driver for neo4j',r'https://notebooks.githubusercontent.com/view/ipynb?browser=chrome&color_mode=auto&commit=50d6f725a1c6c812bd1ab95dd1a02cff27f86997&device=unknown&enc_url=68747470733a2f2f7261772e67697468756275736572636f6e74656e742e636f6d2f6e756e656e75682f67726170682e64617461626173652f353064366637323561316336633831326264316162393564643161303263666632376638363939372f312e496e74726f64756374696f6e2e6970796e62&logged_in=false&nwo=nunenuh%2Fgraph.database&path=1.Introduction.ipynb&platform=android&repository_id=170560198&repository_type=Repository&version=100'],
    'dfstyling' : ['An overview on how to style pandas dataframes (conditional highlighting, etc)', r"https://coderzcolumn.com/tutorials/python/simple-guide-to-style-display-of-pandas-dataframes"],
    'strformat' : ['Real Python: String formatting "Best Practices" (EXCITING!!!;)', r'https://realpython.com/python-string-formatting/']
}
example_keys = list(examples_dict.keys())
random_selection = example_keys[random.randint(0,len(examples_dict)-1)]

#%%
## DEFAULTS 
# for file and driver paths:
file_path = os.getcwd()
exe = shutil.which('chromedriver')
env_bin = os.path.join(sys.prefix, "bin")
chromedriver_autoinstaller.install()

# for html tags and attributes:
tag_type = ["div"]
code_tags = ["pre"]
md_tags = ["p","h1","h2","h3","h4"]
tags_qty = len(code_tags)+len(md_tags)
attr_key = "Ignore all attributes"
code_attr = "input_area"
md_attr = "text_cell_render"
proceed_prompt = "\n------------------ Press <ENTER> to continue ------------------"
paginator =    "\n---------------------------------------------------------------"

#%%
# FUNCTIONS
tup = (list(), set())
# list to keep order, set as lookup table
def dedup(temp, item):
    if item not in temp[1]:
        temp[0].append(item)
        temp[1].add(item)
    return temp

def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def trim(docstring):
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)

#%%
# WELCOME
print('''

         _       _    _                    _             _       _        _   
        / /\    / /\ / /\                /\ \           /\_\    /\ \     /\_\ 
       / / /   / / // /  \              /  \ \         / / /  _ \ \ \   / / / 
      / /_/   / / // / /\ \            / /\ \ \       / / /  /\_\\ \ \_/ / /  
     / /\ \__/ / // / /\ \ \          / / /\ \ \     / / /__/ / / \ \___/ /   
    / /\ \___\/ // / /  \ \ \        / / /  \ \_\   / /\_____/ /   \ \ \_/    
   / / /\/___/ // / /___/ /\ \      / / /    \/_/  / /\_______/     \ \ \     
  / / /   / / // / /_____/ /\ \    / / /          / / /\ \ \         \ \ \    
 / / /   / / // /_________/\ \ \  / / /________  / / /  \ \ \         \ \ \   
/ / /   / / // / /_       __\ \_\/ / /_________\/ / /    \ \ \         \ \_\  
\/_/    \/_/ \_\___\     /____/_/\/____________/\/_/      \_\_\         \/_/  


Welcome to the "Hacky Inline-Example-Code-To-Notebook" Webscraper!''')

url = input (f"\nWhat is the web address (url) of the page you would like to scrape? (or just press enter choose from a list our examples dictionary) ")

if url == '':
    print("EXAMPLES:")
    print(paginator)
    for e in example_keys:
        print(f"{e} : " + examples_dict[e][0])
        print("---------------------------------------------------------------")
    user_selection = input(f"\nTry entering one of the keys above (uwisc, howison, etc.). Otherwise we'll select one for you. ")
    if user_selection in example_keys:
        url = examples_dict[user_selection][1]
        print(f"{paginator}\nWe'll give this a try on '{user_selection}' - {examples_dict[user_selection][0]} ")
    else:
        url = examples_dict[random_selection][1]
        print(f"{paginator}\nWe'll give this a try on '{random_selection}' - {examples_dict[random_selection][0]} ")

a = urlparse(url)

default_filename = ("-".join(re.sub(".html","",a.path).split("/")[1:]))

output_file = default_filename + ".ipynb"

if input(f'''\nThe default filename for this notebook will be '{output_file}'. Would you like to change it (y/[n])? ''').lower() in ['y', 'yes']:
    output_file = (input("\nGive your file a new name (we'll append the extension): ") or default_filename).split(".ipynb")[0] + ".ipynb"

dir_selection_entry = input(f'''{paginator}\nYour current destination directory is {file_path}
\n- To keep this as your destination directory, press <ENTER>. 
- To open a file browser and select a different directory, type 'cd' (then <ENTER>). 
- Alternatively, you can paste the absolute path to whichever directory you would like to use (then press <ENTER>)
> ''')

if dir_selection_entry.lower() == 'cd':
    from tkinter import filedialog
    from tkinter import *
    Tk().withdraw()
    file_path = filedialog.askdirectory() or file_path
else:
    file_path = dir_selection_entry or file_path
print(paginator)
if input('Would you like have the current date and time prepended to your filename ([y]/n)? ').lower() in ["y","yes",""]:
    timestamp = datetime.now().strftime('%Y.%m.%d-%H%Mh')
    output_file = os.path.join( file_path, timestamp + '-' + output_file)
else:

    output_file = os.path.join( file_path, output_file)

if input(f'''{paginator}\nBelow are your selected filename and page url:

file path: {output_file}
source url: {url}

{paginator}\nINSTRUCTIONS (tl;dr):

In order to scrape this page, you'll need to use the 'Inspect Element' tool to find out which of its HTML tags house code and markdown, respectively. We'll collect these from you to use in compiling your notebook.

In a moment, a webbrowser will open displaying your selected webpage. Before we do that, would you like a bit more detail on how to find html tags (y/[n])? ''').lower() == 'y':

    print(paginator)
    input(trim('''INSTRUCTIONS (full-length)

    1. To scrape this notebook, we need to know which HTML tags contain the code and the markdown (text), respectively.
    2. To find out what tags are used to format each type of information (code or text/markdown) on a page, you will need to use the "Inspect Element" tool
    3. To learn how to use Inspect Element, try right-clicking on a code cell when the page opens. Then, from the menu that pops up, open the inspector pane by clicking "Inspect Element".
    4. Once the inspector pane opens (usually in a sidebar), you will see the HTML tag(s) associated with the element you inspected.
    5. If the element you inspect is a code cell, you will probably see a tag like "pre", or "code". Otherwise, you might see "div", "p", "h2", etc. Write down (or remember) this tag.
    6. Repeat this inspection process for every type of element you want to capture, then come back here so we can wrap up the remaining steps and generate your notebook.
    7. Remember these tags, because these HTML tags (e.g. "pre", "code", "p", "h1", "h2", "h3" ...) are what this program will need to know in order to create a jupyter notebook from the webpage.
    8. If you can't figure it out, just take some wild guesses and keep trying until it works. There's no harm whatsoever in running the program multiple times until you get the right tags.
    9. When you're ready, press "Enter" to have selenium open the page so we (you and this program) can each do our part(s) of the data extraction. And don't forget to come back here, after!

    Soon, this process after be effortless. Until then, don't hesitate to refer-back to these instructions.
    ------------------ Press <ENTER> to continue ------------------
    '''))
else:
    print(f"\nOk let's get to it{paginator}")

if os.path.isfile(url):
    with open(url, 'r') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'lxml')
    # Append the file protocol to the URL
    if not url.startswith('file://'):
        url = 'file://' + url
else:
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, features='lxml')
    except:
        try:
            response = urllib.request.urlopen(url)
            text = response.read()
            soup = BeautifulSoup(text, 'lxml')
            webbrowser.open(url)
        except:
            print(f"Looks like there was an issue with the URL: {url}")


all_tags = [tag.name for tag in soup.find_all()]
unique_tags = reduce(dedup, all_tags, tup)[0]
unique_tags.sort()

input(f'''\nAssuming all has gone according to plan, a browser displaying your selected webpage has been/will be opened on your screen. \n\nThe final series of prompts will ask you which page sections (as defined by their HTML tags) contain the code, and which contain the markdown. 
\nIf the page's tags are a close match with this program's default tags, you may choose to proceed without changing anything. \n{proceed_prompt}''')
print(f'''\nHere, in alphabetical order, are all the tags contained on this page: 

{unique_tags}''')
code_defaults_overlap = (set(code_tags) & set(unique_tags))
md_defaults_overlap = (set(md_tags) & set(unique_tags))

if input(f'''\nIt looks like this page includes {len(code_defaults_overlap)} of {len(code_tags)} default code tags {code_defaults_overlap} and {len(md_defaults_overlap)} of {len(md_tags)} default markdown tags {md_defaults_overlap}! 

Would you like to try running this on autopilot to see the results? ([y]/n) ''').lower() in ["y","yes",""]:
    print(f"{paginator}\nGreat! Your notebook (or its enclosing directory) should open momentarily...\n")
    tag_type=md_tags+code_tags

else:
    code_tags = input("\nWhich tag(s) do you want to scrape for code? ").split(" ") or code_tags
    md_tags = input("\nAnd which do you want to scrape for markdown? ").split(" ") or md_tags               
    tagset_inputs_overlap = (set(code_tags) & set(md_tags))
    
    if len(tagset_inputs_overlap) == 0:
        attr_key = "Ignore all attributes"
        code_attr = "Ignore all attributes"
        md_attr = "Ignore all attributes"
        tag_type = md_tags + code_tags
    else:
        print("Your lists of markdown and code tags have these tags in common: ", tagset_inputs_overlap, sep="")
        print(trim('''In order to format the notebook correctly, the scraper needs some way of distinguising markdown from code cells.
        The good news is, since they look different from one another on the webpage, they'll also look different in the core. We just have to find how...
        
        When code and markdown are stored under the same tags, there are two possible approaches: 
        
        The first is to differentiate code tags from markdown tags by their attributes (usually their "class" attribute), but this can only be done where the matching code- and markdown-containing tags have the same attribute KEY, and different attribute VALUES
        
        The second, is to run the scraper with everything but the overlapping tags. 

        We'll start with the first approach, and the second will be our fallback.
        '''))

        print("Here, again are your overlapping tags: ",tagset_inputs_overlap, sep="")


        if input(f'''\Is there any html tag (eg 'div', 'p', etc.) that a) is present in both markdown and code-type sections, and b) has an attribute (e.g. 'class') whose value in the code sections is different from its value in the text/markdown sections (y/n)? ''').lower() == "y":
            tag_type = [input('\nWhich one...? ').split(" ")[0]]
            attr_key = input(f'\nWhat attribute key do the code and markdown {tag_type} tags have in-common? ') or attr_key
            code_attr = input(f'\nFor the {tag_type[0]} tags containing CODE, what value is associated with the {attr_key} attribute key? (Default is: "{code_attr}") ') or code_attr
            md_attr = input(f'\nFor the {tag_type[0]} keys containing MARKDOWN, what value is associated with the {attr_key} attribute key? (Default is: "{md_attr}") ') or md_attr
        else:
            print("Ok. We'll run it with everything but the overlapping tags. Your notebook will be ready mementarily")

#%%
#RUN
dictionary = {  'nbformat': 4, 
                'nbformat_minor': 1, 
                'cells': [
                    { 
                        "metadata":{},"cell_type":"code", "source":[f"# The data in this notebook came from:\n# {url}"],  "outputs": [], "execution_count": None 
                    },
                    {
                        "metadata":{},"cell_type":"markdown","source":["#### Run the code cell below to generate a table of contents"]
                    }
                ], 
                'metadata': {"celltoolbar":
                    [{
                        "name": "Collapsible Headings",
                        "icon": "fa-caret-square-down",
                        "callback": "function toggle() {\n  var ele = this.parentNode.parentNode.nextElementSibling;\n  ele.style.display = (ele.style.display == 'block') ? 'none' : 'block';\n}\nvar headers = document.getElementsByClassName(\"heading\");\nfor (var i = 0; i < headers.length; i++) {\n  headers[i].addEventListener(\"click\", toggle);\n}",
                        "index": 0 
                    }]}}

toc_tags = ["<UL>","</UL>"]
headings = [toc_tags[0]]
hdg_init_len = len(headings)
toc_heading = {"metadata":{},'cell_type':'markdown','source':[]}

def add_cell(target, cell_type, content):
    cell = {}
    cell['metadata'] = {} 
    if cell_type == 'code':
        cell['outputs'] = []
        cell['source'] = content
        cell['execution_count'] = None
    if cell_type == 'markdown':
        cell['source'] = content
    cell['cell_type'] = cell_type
    target['cells'].append(cell)

def extract_first_sentence(text):
    # pattern = re.compile(r'(.*?[.?:-]+)\s')
    pattern = re.compile(r'(\S{4,}.*?[.?:-]+)\s')
    match = pattern.search(text)
    if match:
        first_sentence = match.group(1)
        rest_of_text = text[len(first_sentence):].strip()
    else:
        first_sentence = text
        rest_of_text = ""
    return first_sentence, rest_of_text

def clean_text(text):
    return re.sub(f'[{string.punctuation}]', '', text)

def hash_series(n):
    result = ""
    for i in range(n):
        result += "#"
    return result

def encode_link_text(text):
    return html.escape(text)

for d in soup.findAll(tag_type):
    if attr_key in d.attrs.keys():
        for clas in d.attrs[attr_key]:
            if clas in [code_attr, md_attr]:   
                if clas == code_attr:
                    content = [re.sub(r'(\n\n\n+)', r"\n\n",d.get_text()).strip()]
                    add_cell(dictionary,'code',content)
                else:
                    content = [md(d.decode_contents())]
                    add_cell(dictionary,'markdown',content)
    else:
        if d.name in code_tags: #include and exclude
            content = [re.sub(r'(\n\n\n+)', r"\n\n",d.get_text()).strip()] 
            add_cell(dictionary,'code',content)
            
        elif d.name in md_tags:
            content = md(d.decode_contents())
            if not len(content) == 0: 
                if len(d.name) == 2 and d.name[0]=='h' and d.name[1].isdigit():                  # If the tag is Heading tag, i.e., 'h1' or 'h2'
                    ct = len(headings)
                    val = int(d.name[1])
                    # Pattern below is used to find any existing TOC target link   
                    pattern = re.compile(r'''\[([^][]+)\]''')
                    # alt_content pattern below is used to substitute markdown links 
                    alt_content = re.sub(r'(?:__|[*#])|\[(.*?)\]\(.*?\)',"", content) or ""      # Removes markdown links
                    if alt_content != "":                                                        # Use alt_content version if alt is not empty
                        content = alt_content
                    else:
                        content = pattern.search(content).group(1)
                    first_sentence, rest_of_text = extract_first_sentence(content)
                    first_sentence = first_sentence.strip()
                    first_sentence = re.sub(r'[^\w\s]', '', first_sentence)
                    first_sentence = re.sub(r'\s+', ' ', first_sentence)
                    ct = re.sub(r'\s+', '-', first_sentence)                                     # Substitutes spaces with hyphens BEFORE an additional whitespace is appended to 'first_sentence'
                    first_sentence = first_sentence + " "
                    if val <= 2:
                        headings.append(f"</UL><LI><a href='#{ct}'>{first_sentence}&nbsp</a></OL><UL>")     
                    else:
                        headings.append(f"<LI><a href='#{ct}'>{first_sentence}&nbsp</a>")
                    lines = rest_of_text.splitlines()
                    hashes = hash_series(val)
                    if rest_of_text.strip():  # Check if `rest_of_text` is not empty
                        content = [f"{hashes} [{first_sentence}](#top)<a id='{ct}' class='heading'></a>"]
                        content.append("    - ")
                        for i, line in enumerate(lines):
                            if line.strip():
                                if i == len(lines) - 1:
                                    content.append(f"{line}")
                                else:
                                    content.append(f"{line}\n    ")
                        content = "".join(content)
                    else:
                        content = f"{hashes} [{first_sentence}](#top)<a id='{ct}' class='heading'></a>"
                add_cell(dictionary,'markdown',content) 

headings.append(toc_tags[1])
# toc_body = {"metadata":{},'cell_type':'markdown','source':f'{"".join(headings[1:-1])}'}
toc_body = f'{"".join(headings[1:-1])}'
toc_cell = {"metadata":{},"source":[
                "from IPython.display import HTML\n",
                "import random\n",
                "import re\n",
                "\n",
                "def add_hyphen(html):\n", 
                "    hyphen = '-'\n", 
                "    pattern = re.compile(r\"(<a href=['\\\"])(#[^'\\\"]+)(['\\\"])\")\n", 
                "    html = re.sub(pattern, r'\\1\\2{}\\3'.format(hyphen), html)\n", 
                "    return html\n",
                "# show/hide toggle functionality adapted from this brilliant stackoverflow post: https://stackoverflow.com/a/52664156/19246680\n",
                "def display_toc():\n",
                f'    html = "<a><h3 id=\'top\'>Table of Contents</h3><br></a>{toc_body}"\n', 
                "    toggle_text = 'Toggle show/hide'  # text shown on toggle link\n",
                "\n",
                "    js_f_name = 'code_toggle_{}'.format(str(random.randint(1,2**64)))\n",
                "\n",
                "    if input(\"Are you running this notebook in vsCode? [y/[n]] \").strip()+' '[0] in ['n','N',\" \"]:\n",
                "        html = add_hyphen(html)\n",
                "        html = \"\"\"\n",
                "            <script>function {f_name}() {{$('div.cell.code_cell.rendered.selected').find('div.input').toggle();}}</script></a><a href=\"javascript:{f_name}()\">{toggle_text}</a>{toc}\n", 
                "        \"\"\".format(\n", 
                "            f_name=js_f_name,\n", 
                "            toggle_text=toggle_text,\n", 
                "            toc=html\n",
                "        )\n",
                "\n",
                "    return HTML(html)\n",
                "display_toc()"]
                , "cell_type":"code", "outputs": [], "execution_count": None}

if headings != toc_tags:
    dictionary['cells'].insert(2,toc_cell)
    # dictionary['cells'].insert(1,toc_heading)

open(output_file, 'w').write(json.dumps(dictionary))

if 'driver' in locals() or 'driver' in globals():
    driver.quit()

open_file(output_file)