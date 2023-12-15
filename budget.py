from datetime import datetime, timedelta
import os
import configparser
import argparse
import subprocess


# class to manage simple budget, stored in text files
# takes: 
#   the location of the text files
#   how much should be added to the budget every time it is refilled 
#       currently hard coded to weekly
class Budget:
    def __init__(self, storage_path, refill_amount) -> None:

        self.storage_path = storage_path
        self.refill_amount = refill_amount
        self.date_format = "%Y-%m-%d"

        self.init_current_file()

    # this actually controls the length of the budget cycle
    # if the file name was just year and month, it would get recreated monthly isntead of weekly
    # TODO get option from config and allow daily/weekly/monthly/yearly?
    def get_current_file_name(self):
        return f"{self.storage_path}/{datetime.today().isocalendar().year}-{datetime.today().isocalendar().week}.txt"
    
    def init_current_file(self):
        # if the file doesnt exist, create it and add the refill line (refill amount on monday)
        if not os.path.exists(self.get_current_file_name()):

            monday = (datetime.now() - timedelta( days = datetime.now().weekday())).strftime(self.date_format)
            
            os.makedirs(os.path.dirname(self.get_current_file_name()), exist_ok=True)

            with open(self.get_current_file_name(), "w") as file:
                file.write(f"{monday} {self.refill_amount} refill\n")


    def add_expense(self, amount, description):

        date = datetime.now().strftime(self.date_format)
        # dont know what was passed in, but we are adding a - ourselves
        amount_abs = abs(amount)

        with open(self.get_current_file_name(), "a") as file:
            file.write(f"{date} -{amount_abs} {description}\n")

    def get_total_balance(self):
        
        total = 0

        # go through all the files
        for path, subdirs, files in os.walk(self.storage_path):
            for filename in files:

                full_file_path = os.path.join(path, filename)

                with open(full_file_path,"r") as file:
                    lines = file.readlines()
                    for line in lines:
                        total += float(line.split(" ")[1])

        return round(total,2)
    
    def get_current_week_expenses(self):

        expenses = []

        with open(self.get_current_file_name(), "r") as file:
            lines = file.readlines()
            for line in lines:
                split_line = line.split(" ")
                date = split_line[0]
                amount = float(split_line[1])
                description = (" ".join(split_line[2:])).strip()

                # only return expenses
                if amount < 0:
                    expenses.append([date, abs(amount), description])

            return expenses

    def print_summary(self):

        current_balance = self.get_total_balance()
        
        print("\nThis Week's Expenses\n--------------------")

        for expense in self.get_current_week_expenses():
            print("%-12s%7.2f   %-s" % (expense[0], expense[1], expense[2]))

        print(f"\nTotal Remaining: {current_balance}")



# create the default config file if it doesnt exist
def init_config_file(config_path):

    if not os.path.exists(config_path):

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
        prog="budget",
        description="Command line budget tracker using simple text files",
        epilog="Happy \nbudgeting :)"
    )

    arg_parser.add_argument("-e", 
                            "--edit",  
                            help="edit the current weeks file (editor defined in config file) (all other arguments will be ignored)", 
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
