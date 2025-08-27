
aim:
plain text message -> ANY OPERATION IN BETWEEN ->plain text response 


FLOW

EXAMPLE ->OPENROUTER_AGENT.PY


WE NEED CONFIGS 
WE ARE USING OPEN API COMPATIBLE API WHICH IS FIXED
WHAT CAN BE SET
 WE CAN SET THE BASE URL ANY BASE URL IS SUPPORTED WHIHC USED OPEN AI API
 ANY VALID API KEY FOR THAT BASE URL

 HOW DOES THE CONFG SYSTEM WORKS:

    WE ARE USING THE CONFIG/DEFAULT.YAML FOR THE 
    MODLE BASE URL AND MODEL NAME AND MODEL SETTINGS

    FOR SENSITIVE ENV WE ARE USING THE ENV FILE 

SO TO SETUP MODEL AND ITS SETTING WE USE DEFAULT.YAML FILE

TO PUT THE API KEY WE USE THE ENV FILE

#  CONFIG LOADER HOW THE LOADING OF CONGI WORKS 

```
  cfg = load_config(["config/default.yaml"])
    or_cfg = get_openrouter_cfg(cfg)
    llm = OpenRouterProvider.from_config(or_cfg)

```
we are loadin ghe conif by calling the load config from the config loadder import 

here we are doing two step ocnfig loading 
the load config file is loading the whole tree
the get openrouter_cfg is a fucntion to extract the openrouter specific configs



now that we have config for the openrouter api
we will b e creating the llm model FOR SPecific provider

## HOW PROVIDERS WORKS

providers are wrapper that stores that client instance configs abotu the ml like base url api key and all , so bascially it abstracts the message sendint process to the llm

an agents expects a llm provider so it can send message

llm provider doenst handle tools

## HOW DOES AGENT WORKS

AGENT HANDLES THE TOOL CALLING ANS SENDNG MESSAGE AND INTERMEADIORTY STEPS AND IF LLLM ASK TO CALL ANY TOOL IT DOES IT ON BEHALD OF IT 






