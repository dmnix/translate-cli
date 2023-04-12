# Translate-cli

Command line translator, which uses [Ligva Translate](https://github.com/thedaviddelta/lingva-translate), Google translator front-end.

```
$ python translate-cli.py world
auto (en) >> cs

svět

[wərld]
Other translations:
        noun
          - svět
          - země
          - lidstvo
          - společnost
```

## Configuration

Configuration is done by editing ```config.json``` file. This file must be in the same directory as the main script ```translate-cli.py```. 

```
{
    "instance": "[url]",
    "default_source_language": "[language_code]",
    "default_target_language": "[language_code]"
}
```

List of some available instances can be found [here](https://github.com/thedaviddelta/lingva-translate).

When running the srcipt without specifying source or target languages, defaults are used. Languages are specified by their codes.

## Supported languages
Since this is just front-end, all languages supported by Lingva Translate (Google translator), this tool supports as well. You can get full list by running the script with ```-l``` or ```-L``` flags.