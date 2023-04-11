#!/usr/bin/env python
import urllib.request
import urllib.error
import urllib.parse
import json
import argparse

try:
    with open("config.json", mode="r") as confFile:
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
        response = json.loads(response)
        if source == "auto":
            print(f"{source} ({response['info']['detectedSource']}) >> {target}")
        else:
            print(f"{source} >> {target}")
        print(f"\n{response['translation']}\n")

        if response["info"]["pronunciation"] != {}:
            print(f"[{response['info']['pronunciation']['query']}]")
        
        if response["info"]["extraTranslations"] != []:
            print("Other translations:")
            for type in response["info"]["extraTranslations"]:
                print(f"\t{type['type']}")
                for word in type["list"]:
                    print(f"\t  - {word['word']}")


if __name__ == "__main__":
    args = argparse.ArgumentParser(description="CLI client for Lingva Translate, Google Translate front-end.")
    listing = args.add_mutually_exclusive_group()
    listing.add_argument("-l", "--list-source-languages", help="List available source languages and their codes", action="store_true")
    listing.add_argument("-L", "--list-target-languages", help="List available target languages and their codes", action="store_true")
    args.add_argument("-s", "--source-language", help="Specify source language", type=str, action="store", metavar="code")
    args.add_argument("-t", "--target-language", help="Specify target language",type=str, action="store", metavar="code")
    args.add_argument("string", help="String to be translated", action="store", nargs="?")
    args = args.parse_args()

    if args.list_source_languages:
        listLanguages("source")
    elif args.list_target_languages:
        listLanguages("target")
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
        
        translate(source, target, string)