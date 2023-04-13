#!/usr/bin/env python
import urllib.request
import urllib.error
import urllib.parse
import json
import argparse
import os.path

SCRIPT_PATH = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
try:
    with open(f"{SCRIPT_PATH}/config.json", mode="r") as confFile:
        config = json.loads(confFile.read())
        if(config["instance"][-1] == "/"): 
            config["instance"] = config["instance"][0:len(config["instance"])-1]
except FileNotFoundError:
    print("Configuration file does not exist.")
    exit()
except PermissionError:
    print("Permission denied while trying to load configuration file")
    exit()
except:
    print("An error occured while trying to load configuration file")
    exit()

def request(url):
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as error:
        print(f"HTTP error occured: {error.status} ({error.reason})")
        return None
    except urllib.error.URLError as error:
        print(f"An error occured: {error.reason}")
        return None
    
    return response.read()

def listLanguages(type):
    # type can be "source" or "target"
    url = config["instance"]
    url += f"/api/v1/languages/{urllib.parse.quote(type)}"
    
    response = request(url)
    if response != None:
        response = json.loads(response)
        print("Code\t\tName\n--------------------")
        for language in response["languages"]:
            print(f"{language['code']}\t\t{language['name']}")
    
def translate(source, target, string):
    url = config["instance"]
    url += f"/api/v1/{urllib.parse.quote(source)}/{urllib.parse.quote(target)}/{urllib.parse.quote(string)}"
    response = request(url)
    if response != None:
        output = ""
        response = json.loads(response)
        if source == "auto":
            output += f"{source} ({response['info']['detectedSource']}) >> {target}"
        else:
            output += f"{source} >> {target}"

        output += f"\n\n{response['translation']}\n"

        if response["info"]["pronunciation"] != {}:
            output += f"\n[{response['info']['pronunciation']['query']}]"
        
        if response["info"]["extraTranslations"] != []:
            output += "\nOther translations:"
            for type in response["info"]["extraTranslations"]:
                output += f"\n\t{type['type']}"
                for word in type["list"]:
                    output += f"\n\t  - {word['word']}"
        return output

def fileInput(fileName):
    try:
        with open(fileName, "r") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File {fileName} does not exist.")
        exit()
    except PermissionError:
        print(f"Permission denied while trying to read from {fileName}")
        exit()
    except:
        print(f"An error occured while trying to read from {fileName}")
        exit()
    return content

def fileOutput(fileName, content):
    try:
        with open(fileName, "w") as file:
            file.write(content)
    except PermissionError:
        print(f"File {fileName} is not writable")
        exit()
    except:
        print(f"An error occured while trying to write to {fileName}")
        exit()

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
                string = input("> ")
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
        
        translatedText = translate(source, target, string)
        print(translatedText)
        if args.output_file != None:
            fileOutput(args.output_file, translatedText)