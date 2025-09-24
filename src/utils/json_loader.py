import json


def load_config():
    with open('config/default.json','r') as file :
        providers = json.load(file)

    # Print type and data
    print("Loaded Providers:", providers)
    return providers

def get_provider( cfg, name : str):
    for provider in cfg:
        if provider ["name"] == name :
            return provider
        
    return {}
