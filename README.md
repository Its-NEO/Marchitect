# MARCHITECT

**- Your mod architect.**

An awesome cli which helps creating and sharing Minecraft mod-packs a piece of cake!

Initialise using [setup.bat](./setup.bat), run using [run.bat](run.bat) and ENJOY!

## Requirements

[Python 3.10](https://www.python.org/downloads/release/python-3100/)

## Basic Commands

- **SEARCH**

To search a mod use:

```commandline
search [mod name]
```

- **ADD**

Add the index of the required mod:

```commandline
add [index]
```

- **LIST**

List the added mods:

```commandline
list
```

- **REMOVE**

Remove the mod which you don't need in your mod-pack:

```commandline
remove [index]
```

- **EXPORT**

Export the mod-pack you have just created:

```commandline
export [out path]
```

- **DOWNLOAD**

Send this file to anyone and they can download your mod-pack using:

```commandline
download [file path] -o [output path]
```

## IMPORTANT
**Note:**
> To use this mod-pack developer, you must create a python file "src/key.py" and create a function *get_key()* 
> inside it to return the api key of curseforge developers.

For your convenience:
```python
# This code must be inside src/key.py
def get_key():
    return "CURSEFORGE API KEY"
```

>Where to get the developer key?  
>Here - [Curseforge](https://console.curseforge.com/#/login)
