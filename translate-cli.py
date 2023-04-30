#!/usr/bin/env python
import urllib.request
import urllib.error
import urllib.parse
import json
import argparse
import os.path
import sys

SCRIPT_PATH = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
try:
    with open(f"{SCRIPT_PATH}/config.json", mode="r") as confFile:
        config = json.loads(confFile.read())
        if(config["instance"][-1] == "/"): 
            config["instance"] = config["instance"][0:len(config["instance"])-1]
except FileNotFoundError:
    print("ERROR: Configuration file does not exist.")
    sys.exit(1)
except PermissionError:
    print("ERROR: Permission denied while trying to load configuration file")
    sys.exit(1)
except:
    print("ERROR: An error occured while trying to load configuration file")
    sys.exit(1)

def request(url):
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as error:
        print(f"ERROR: HTTP error occured: {error.status} ({error.reason})")
        sys.exit(1)
    except urllib.error.URLError as error:
        print(f"ERROR: An error occured: {error.reason}")
        sys.exit(1)
    
    return response.read()

def listLanguages(type):
    # type can be "source" or "target"
    url = config["instance"]
    url += f"/api/v1/languages/{urllib.parse.quote(type)}"
    
    response = request(url)
    response = json.loads(response)
    print("Code\t\tName\n--------------------")
    for language in response["languages"]:
        print(f"{language['code']}\t\t{language['name']}")
    
def translate(source, target, string):
    url = f"{config['instance']}/api/v1/{urllib.parse.quote(source)}/{urllib.parse.quote(target)}/{urllib.parse.quote(string)}"
    response = request(url)
    response = json.loads(response)
    translation = f"{response['translation']}"

    # Pronunciation of input string
    if "query" in response["info"]["pronunciation"]:
        print(f"/{response['info']['pronunciation']['query']}/")
    
    # Source and target languages
    if source == "auto":
        print(f"{source} ({response['info']['detectedSource']}) >> {target}")
    else:
        print(f"{source} >> {target}")    
    
    # Translation
    print(translation, end="\n\n")

    # Pronunciation of translated string
    if "translation" in response["info"]["pronunciation"]:
        print(f"/{response['info']['pronunciation']['translation']}/")
    
    ## Other tranlsations
    if response["info"]["extraTranslations"] != []:
        print("Other translations:")
        for type in response["info"]["extraTranslations"]:
            print(f"\t{type['type']}")
            for word in type["list"]:
                print(f"\t  - {word['word']}")
                
    return translation

def fileInput(fileName):
    try:
        with open(fileName, "r") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"ERROR: File {fileName} does not exist.")
        sys.exit(1)
    except PermissionError:
        print(f"ERROR: Permission denied while trying to read from {fileName}")
        sys.exit(1)
    except:
        print(f"ERROR: An error occured while trying to read from {fileName}")
        sys.exit(1)
    return content

def fileOutput(fileName, content):
    try:
        with open(fileName, "w") as file:
            file.write(content)
    except PermissionError:
        print(f"ERROR: File {fileName} is not writable")
        sys.exit(1)
    except:
        print(f"ERROR: An error occured while trying to write to {fileName}")
        sys.exit(1)

if __name__ == "__main__":
    args = argparse.ArgumentParser(description="CLI client for Lingva Translate, Google Translate front-end.")
    listingArgs = args.add_mutually_exclusive_group()
    listingArgs.add_argument("-l", "--list-source-languages", help="List available source languages and their codes", action="store_true")
    listingArgs.add_argument("-L", "--list-target-languages", help="List available target languages and their codes", action="store_true")
    args.add_argument("-s", "--source-language", help="Specify source language", type=str, action="store", metavar="code")
    args.add_argument("-t", "--target-language", help="Specify target language",type=str, action="store", metavar="code")
    args.add_argument("-o", "--output-file", help="Write translation to a text file", action="store", type=str, metavar="file")
    inputArgs = args.add_mutually_exclusive_group()
    inputArgs.add_argument("-i", "--input-file", help="Use a text file as input", action="store", type=str, metavar="file")
    inputArgs.add_argument("string", help="String to be translated", action="store", nargs="?")
    args = args.parse_args()

    if args.list_source_languages:
        listLanguages("source")
    elif args.list_target_languages:
        listLanguages("target")
    else:
        if args.input_file != None:
            string = fileInput(args.input_file)
        else:
            if args.string == None:
                string = ""
                while True:
                    line = sys.stdin.readline()
                    if(line == "" or line == "\n"):
                        break
                    else:
                        string += line
            else:
                string = args.string

        if args.source_language == None:
            source = config["default_source_language"]
        else:
            source = args.source_language
        
        if args.target_language == None:
            target = config["default_target_language"]
        else:
            target = args.target_language
        if(string == "" or string == "\n"):
            print("Can not translate empty text")
        else:
            translatedText = translate(source, target, string)
        if args.output_file != None:
            fileOutput(args.output_file, translatedText)