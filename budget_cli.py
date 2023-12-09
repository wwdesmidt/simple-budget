from budget import Budget
import configparser
import argparse
import os
import subprocess

# create the default config file if it doesnt exist
def init_config_file(config_path):

    if not os.path.exists(config_path):
        print(f"Configuration not found. Creating default configuration: {config_path}")

        default_config = configparser.ConfigParser()

        default_config['app'] = {
            "storage_path":"./budget",
            "editor":"notepad"
        }

        default_config["budget"] = {
            "refill_amount":120
        }

        with open(config_path, 'w') as config_file:
            default_config.write(config_file)



def main():

    #TODO best place to store config per OS?
    config_path = "./config.ini"
    
    # create config file with default values if it doesnt exist
    init_config_file(config_path)

    # read config
    config = configparser.ConfigParser()
    config.read(config_path)

    # create our budget instance with config values
    budget = Budget(config["app"]["storage_path"], config["budget"]["refill_amount"])

    # set up arg parser
    arg_parser = argparse.ArgumentParser(
        prog="Simple Budget",
        description="Command line budget tracker using simple text files",
        epilog="Happy \nbudgeting :)"
    )

    arg_parser.add_argument("-e", 
                            "--edit",  
                            help="edit the current weeks file\neditor defined in config file) (all other arguments will be ignored)", 
                            dest="edit", 
                            action='store_true')
    
    arg_parser.add_argument("amount", 
                            help="amount of the expense", 
                            type=float, 
                            nargs="?")
    
    arg_parser.add_argument("description", 
                            help="description of the purchase", 
                            type=str, 
                            nargs=argparse.REMAINDER)

    # parse args
    args = arg_parser.parse_args()

    if(args.edit):
        subprocess.run(f"{config['app']['editor']} {budget.get_current_file_name()}")
    
    # amount was passed in so we are creating a new expense
    elif(args.amount):

        amount = args.amount

        description = ""
        if(args.description):
            description = " ".join(args.description)

        budget.add_expense(amount, description)

    # if no other args were processed, print the budget summary   
    else:
        budget.print_summary()

    


if __name__ == '__main__': main()
