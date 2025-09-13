import argparse
import sys

# -------------------------
# Placeholder Agent Actions
# -------------------------


def plan_workflow(args):
    print("🔹 [PLAN] Placeholder: Planning the workflow...")


# -------------------------
# CLI Setup
# -------------------------



#--------------------------
# PRICESS OUTOUT
#--------------------------

commands = []

def process_input(input):
    if(input=="hi"):
        print("hellow !!")
    elif(input =="how are you"):
        print("I am fine , how are you..")
    else:
        print(input)

def main():
    banner = r"""
    ███████╗██╗     ███████╗██╗  ██╗██╗   ██╗ ██████╗ ███████╗███╗   ██╗████████╗
    ██╔════╝██║     ██╔════╝██║  ██║╚██╗ ██╔╝██╔═══██╗██╔════╝████╗  ██║╚══██╔══╝
    █████╗  ██║     █████╗  ███████║ ╚████╔╝ ██║   ██║█████╗  ██╔██╗ ██║   ██║   
    ██╔══╝  ██║     ██╔══╝  ██╔══██║  ╚██╔╝  ██║   ██║██╔══╝  ██║╚██╗██║   ██║   
    ██║     ███████╗███████╗██║  ██║   ██║   ╚██████╔╝███████╗██║ ╚████║   ██║   
    ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
    """
    print(banner)
    print("Welcome to FlexyAgent CLI 🚀 (type 'help' for commands, 'exit' to quit)\n")

    while True:
        user_input=input("> ")
        process_input(user_input)



if __name__=="__main__":
    main()







