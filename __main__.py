#!/usr/bin/env python3

##################################################################################
# Released under the GNU Lesser General Public License v2.
# Copyright (C) - 2020 - user "thiswillbeyourgithub" of the website "github".
# This file is part of LiTOY : a tool to help organiser various goals over time.
# Anki card template helping user to retain knowledge.
# 
# LiTOY is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# LiTOY is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with LiTOY.  If not, see <https://www.gnu.org/licenses/>.
# 
# for more information or to get the latest version go to :
# https://github.com/thiswillbeyourgithub/LiTOY
##################################################################################

import time
import random
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import argparse
import pprint
import subprocess
import termplotlib

#from   src.litoy.sql        import *
from   src.litoy.settings   import *
from   src.litoy.elo        import *
from   src.litoy.functions  import *



###################################################################
###################################################################
#                                                                 #
#     __    _ ____________  __                                    #
#    / /   (_)_  __/ __ \ \/ /                                    #
#   / /   / / / / / / / /\  /                                     #
#  / /___/ / / / / /_/ / / /                                      # 
# /_____/_/ /_/  \____/ /_/                                       #
#                                                                 #
#                                                                 #
#   ________            __    _      __     ________          __  #
#  /_  __/ /_  ___     / /   (_)____/ /_   /_  __/ /_  ____ _/ /_ #
#   / / / __ \/ _ \   / /   / / ___/ __/    / / / __ \/ __ `/ __/ #
#  / / / / / /  __/  / /___/ (__  ) /_     / / / / / / /_/ / /_   #
# /_/ /_/ /_/\___/  /_____/_/____/\__/    /_/ /_/ /_/\__,_/\__/   #
#                                                                 #
#    ____        __  ___                    __  __                #
#   / __ \__  __/ /_/ (_)   _____  _____    \ \/ /___  __  __     #
#  / / / / / / / __/ / / | / / _ \/ ___/     \  / __ \/ / / /     #
# / /_/ / /_/ / /_/ / /| |/ /  __(__  )      / / /_/ / /_/ /      #
# \____/\__,_/\__/_/_/ |___/\___/____/      /_/\____/\__,_(_)     #
#                                                                 #
#                                                                 #
#                                                                 #
###################################################################
###################################################################





###################### initialization :

def main() :
    logging.info("\n\n\n\n\n\n########################################\nSTARTING")
    if os.path.exists('database.db'):
        init_table()
    else:
        logging.info("db NOT found")
        print("NO DB FOUND (database.db), creating one...")
        init_table()


###################### main :
    ###################### arguments that call routines :

    parser = argparse.ArgumentParser()
    parser.add_argument("--fight", "-f",
            nargs = "+",
            metavar = "mode",
            dest='fight',
            type = str,
            required=False,
            help = "pick entries at random and make them fight")
    parser.add_argument("--add", "-a",
            nargs = "*",
            type = str,
            metavar='formated_entry deck metadata',
            dest='addentry',
            required=False,
            help = "directly add an entry by putting it inside quotation mark like so : python3 ./__main__.py -a \"do this thing\" \"DIY\" \"I really need to do it that way\"")
    parser.add_argument("--import_from_txt", "-i",
            nargs = "*",
            type = str,
            metavar='database_path',
            dest='import',
            #default='new_entry.txt',
            required=False,
            help = "import from a textfile")
    parser.add_argument("--number", "-n",
            nargs = 1,
            type = int,
            metavar="limit",
            dest='nlimit',
            required=False,
            default=99999,
            help = "sets the limit of entries to process or display etc, default=999999")
    parser.add_argument("--settings", "-S",
            nargs = 2,
            type = str,
            metavar="variable new_value",
            dest='settings',
            required=False,
            help = "set user settings")
    parser.add_argument("--edit", "-e",
            nargs = "*",
            type = str,
            metavar = "ID field newvalue",
            dest="editEntry",
            required=False,
            help = "edit specific field from an entry")
    parser.add_argument("--rank", "-r",
            nargs = "*",
            type = str,
            metavar = "FIELD direction",
            dest="rank",
            required=False,
            help = "display ranked entries according to the right formula")
    parser.add_argument("--deck", "-d",
            nargs = 1,
            type = str,
            metavar = "deck_name",
            dest="deck",
            required=False,
            help = "deck to display or fight or import to")
    parser.add_argument("--tags", "-t",
            nargs = 1,
            type = str,
            metavar = "tags",
            dest="tags",
            required=False,
            help = "tags to display or fight")
    parser.add_argument("--metadata",
            nargs = 1,
            type = str,
            metavar = "metadata",
            dest="metadata",
            required=False,
            help = "metadata to add to the entry")
    parser.add_argument("--external","-x",
            action='store_true',
            required=False,
            dest="ext",
            help = "LINUX : open in sqlite browser")
    parser.add_argument("--state", "-s",
            action='store_true',
            required=False,
            dest="state",
            help = "show current tags decks etc")
    parser.add_argument("--list-disabled",
            action='store_true',
            required=False,
            dest="list_disabled",
            help = "shows the card that have been disabled")
    parser.add_argument("--list-starred",
            action='store_true',
            required=False,
            dest="list_starred",
            help = "shows the card that have been starred")
    parser.add_argument("--verbose",
            action='store_true',
            required=False,
            help = "show debug to the console instead of just in the file")
    parser.add_argument("--check-consistency",
            action='store_true',
            required=False,
            dest="consistency",
            help = "Check the db for incoherent values (non exhaustive)")
    parser.add_argument("--version",
            action='store_true',
            required=False,
            help = "display version information")
    args = parser.parse_args().__dict__

    logging.info("LiTOY started with arguments : " + str(args))

    # exits if incompatible arguments found :
    inc=0
    for i in args.keys() :
        ii = str(args[i])
        inc_list=[]
        if ii not in ["None","False"] and i not in ["nlimit", "verbose", "deck", "tags"]:
            inc_list.append(i)
            inc = inc+1
    if inc>1 :
        print(inc_list)
        print("Are incompatible arguments! \n   Exiting...")
        logging.info("Incompatible arguments :" + str(inc_list) + "\n   Exiting...")
        sys.exit()

    ###################### routines :

#    if args['verbose'] == True:
#        #https://stackoverflow.com/questions/14058453/making-python-loggers-output-all-messages-to-stdout-in-addition-to-log-file
#        file_handler = logging.FileHandler(filename='debug.log')
#        stdout_handler = logging.StreamHandler(sys.stdout)
#        handlers = [file_handler, stdout_handler]
#
#        logging.basicConfig(level=logging.INFO,
#                handlers=handlers,
#                format='%(asctime)s: %(message)s')
#        logger = logging.getLogger('LOGGER_NAME')
#    if args['verbose'] == False:
#        logging.basicConfig(level=logging.INFO,
#                filename = 'debug.log',
#                filemode='a',
#                format='%(asctime)s: %(message)s')
#        logger = logging.getLogger('LOGGER_NAME')


    if args['fight'] != None:
        logging.info("Fight : argument : " + str(args['fight']))
        if len(args['fight']) != 1 or args['deck'] == None :
            logging.info("Fight : wrong number of arguments : " + str(args['fight']))
            print("Fight : Wrong number of arguments")
            print_syntax_examples()
        
        try :  # get nlimit, no matter the format
            limit = int(args['nlimit'][0])
        except TypeError:
            limit = int(args['nlimit']) # needed if nlimit=default value
        if limit < 1:
            print('Fight : Invalid limit number')
            logging.info('Fight : Invalid limit number')
            sys.exit()
        else :
            logging.info("Fight " + str(limit) + " times")

        n_cards = len(fetch_entry("ID >=0"))
        if n_cards <=5 :
            print('You need to have at least 5 entries to make them fight!')
            logging.info("Fight : Not enough entries to fight")
            sys.exit()
        for n in range(limit):
            mode_choice = args['fight'][0]
            mode=""
            if mode_choice  in "time" :
                mode="time"
            if mode_choice  in "importance" :
                mode="importance"
            if mode_choice  in "random" or mode_choice in "mixed" :
                mode=random.choice(["time","importance"])

            if mode=="":
                print("Fight : invalid fight mode")
                logging.info("Fight : invalid fight mode")
                print_syntax_examples()
                sys.exit()

            try : 
                fighters = pick_2_entries(mode, " AND deck IS '" + str(args['deck'][0]) + "'" )
            except sqlite3.OperationalError :
                print("Sql3 error : Wrong deck name? use --list to display deck list")
                logging.info("Fight : Wrong deck name")
                sys.exit()
            except TypeError :
                logging.info("Fight : TypeError : No deck provided, exiting")
                print(col_red + "Typerror : No deck provided? exiting")
                sys.exit()
                #fighters = pick_2_entries(mode, " AND deck IS '" + str(args['deck']) + "'" )
            except IndexError :
                logging.info("Fight : IndexError : No card found")
                print("IndexError : No card found, wrong deck name?")
                print("Decks found in db : " + col_blu + str(get_decks()) + col_rst)
                sys.exit()
            print("\n"*(sizey-10))
            print_2_entries(fighters, str(args['deck'][0]), mode, "noall") #all is for debugging
            print("\n")
            shortcut_and_action(mode, fighters)

    if args["state"] is not False :
        logging.info("Showing state of the database")
        print("Decks found in db : " + col_blu + str(get_decks()) + col_rst)
        print("Tags found in db : " + col_blu + str(get_tags()) + col_rst)
        print("Number of cards : " + col_blu + str(len(fetch_entry("ID >= 0"))) + col_rst)
        print("Current fields in the db : " + col_blu + str(get_field_names()) + col_rst)
        print("\nDelta by deck : ")
        for deck in get_decks():
            print(" => " + col_blu + deck + col_rst)
            for mode in ["importance", "time"] :
                print("    => by " + col_blu + mode + col_rst + " : " + str(get_deck_delta(deck, mode)))
                Seq_delta = get_sequential_deltas(deck, mode)
                derivative = []
                try :
                    # complete plot
                    for n in range(len(Seq_delta)-1):
                        derivative.append(int(Seq_delta[n]["seq_delta"]) - int(Seq_delta[n+1]["seq_delta"]))
#                    for n in range(10, 0, -1):
#                        derivative.append(int(Seq_delta[len(Seq_delta)-n-1]["seq_delta"]) - int(Seq_delta[len(Seq_delta)-n]["seq_delta"]))
                    mean_der = sum(derivative)/len(derivative)
                    print(col_gre + "        => in mode " + mode + ", lost on average " + str(int(mean_der)) + " points per fight. Expected to reach 0 after " + str(int(int(Seq_delta[-1]["seq_delta"])/mean_der)+1) + ' fights.' + col_rst)
                    fightnb = []
                    deltas = []
                    for m, line in enumerate(Seq_delta) :
                        fightnb.append(m)
                        deltas.append(int(line["seq_delta"]))
                    print("\n")
                    fig = termplotlib.figure()
                    fig.plot(fightnb, deltas,
                            label = "Deltas after each fight : " + deck + " ("+mode+")",
                            xlabel="Fight index",
                            width = sizex, height = 20
                            )
                    fig.show()
                except ZeroDivisionError:
                    print(col_yel + "      => in mode " + mode + ", no fights have been fought, no data to show." + col_rst)
                # plot for the last 10 fights :
                try :
                    mean_der = sum(derivative[len(derivative)-10:])/10
                    print(col_gre + "        => in mode " + mode + ", for the last 10 fights : lost on average " + str(int(mean_der)) + " points per fight. Expected to reach 0 after " + str(int(int(Seq_delta[-1]["seq_delta"])/mean_der)+1) + ' fights.' + col_rst)
                    fightnb = []
                    deltas = []
                    for m, line in enumerate(Seq_delta) :
                        fightnb.append(m)
                        deltas.append(int(line["seq_delta"]))
                    print("\n")
                    fig = termplotlib.figure()
                    fig.plot(fightnb, deltas,
                            label = "Deltas after each fight : " + deck + " ("+mode+")",
                            xlabel="Fight index",
                            width = sizex, height = 20
                            )
                    fig.show()
                except IndexError:
                    print(col_yel + "      => in mode " + mode + ", less than 10 fights, no graphics to show." + col_rst)
                except ZeroDivisionError:
                    print(col_yel + "      => in mode " + mode + ", no fights have been fought, no data to show." + col_rst)
                print("\n\n\n")
        logging.info("Listing : done")

    if args["list_starred"] is not False:
        print("Printing the starred entries :")
        logging.info("Showing starred entries : begin")
        all_cards = fetch_entry("ID >=0 AND starred IS 1")
        pprint.pprint(all_cards)
        logging.info("Showing starred entries : done")


    if args["list_disabled"] is not False:
        print("Printing the disabled entries :")
        logging.info("Showing disabled entries : begin")
        all_cards = fetch_entry("ID >=0 AND disabled IS 1")
        pprint.pprint(all_cards)
        logging.info("Showing disabled entries : done")

    if args['addentry'] != None:
        logging.info("Addentry : adding entry : " + str(args['addentry']))
        if len(args['addentry']) != 1:
            print("Invalid number of arguments : " + str(args['addentry']))
            logging.info("Import : Invalid number of arguments : " + str(args['addentry']))
            print_syntax_examples()
            sys.exit()
        add_entry_todb(args)
        
    if args['import'] != None:
        logging.info("Import : Importing from file, arguments : " + str(args['import']))
        if len(args["import"])!=1:
            print("Invalid number of arguments : " + str(args['import']))
            logging.info("Import : Invalid number of arguments : " + str(args['import']))
            print_syntax_examples()
            sys.exit()
        filename=str(args["import"][0])
        if args["deck"] == None :
            print("No deckname supplied")
            logging.info("Import : No deckname supplied")
            print_syntax_examples()
            print("Here are the decks that are already in your db :")
            print(get_decks())
            sys.exit()
        if args["tags"]==None:
            logging.info("No tags supplied")
            rep = input("Are you sure you don't want to add tags? They are really useful!\nTags found in db : " + str(get_tags()) + "\n(Yes/tags)=>")
            if rep in "yes" :
                logging.info("Import : Won't use tags")
                tags=[""]
            else :
                tags=[str(rep)]
        else :
            tags = [args["tags"]]
            
        logging.info("Importing : begin")
        db = sqlite3.connect('database.db') ; cursor = db.cursor()
        with open(filename) as f: # reads line by line
            content = f.readlines()
            content = [x.strip() for x in content] # removes \n character
            content = list(dict.fromkeys(content))
        for n,line in enumerate(content) :
            if line[0] == "#":
                print(col_yel + "Ignored content : " + line + col_rst)
                content[n]=""
        try :content.remove("")  # remove empty lines
        except ValueError : pass # no empty lines

        newID = -1
        for entry in content :
            if tags != [""] or tags != [str(rep)]:
                tags=""  # otherwise it is not reset between entries
            if newID == -1 :
                newID = str(int(get_max_ID())+1)
            else :
                newID = str(int(newID)+1)
            entry = entry.replace("'","`") # otherwise it messes with the SQL
            creation_time = str(int(time.time())) # creation date of the entry
            query_exists = "SELECT ID FROM LiTOY WHERE entry = '" + entry + "'"
            cursor.execute(query_exists)
            try :  # checks if the card already exists
                existence = str(cursor.fetchone()[0])
            except :
                existence = "False"

            if existence is not "False" :
                print("Entry already exists in db : '" + entry + "'")
                logging.info("Entry already exists in db : '" + entry + "'")
            else :
                # this routine uses both "entry" and "addentry" for backwards compatibility with the 
                # argument call when using litoy --add
                dic = {
                        "ID"         : str(newID),
                        "entry"      : [entry],
                        "addentry"   : [entry],
                        "deck"       : [str(args["deck"][0])],
                        }
                # extract tags if present
                if "tags:" in entry :
                    tag_sep = entry.split(sep="tags:")
                    if len(tag_sep) >= 3 :
                        logging.info("Importing : too many tags found!" + tag_sep)
                        print(col_red + "Importing : too many tags found! : " + tag_sep)
                        print("Use the syntax like this : 'somethingtodo tags:DIY/AI/work'" + col_rst)
                        sys.exit()
                    if len(tag_sep) == 2 :
                        space_sep = entry.split(sep=" ")
                        found=0
                        for word in space_sep :
                            if word[0:5] == "tags:":
                                found+=1
                                word = word[5:]
                                tags = list(tags) + word.split(sep="/")
                        if found>1:
                            print(col_red + "Something is wrong")
                            logging.info("Importing : several tags were added ?!")
                        print("           Entry with ID " + dic["ID"] + " will also have the following tags : "  +str(tags))
                        logging.info("Importing : Entry with ID " + dic["ID"] + " will have the following additionnal tags : "  +str(tags[1:]))
                        dic["tags"] = tags
                else :
                    logging.info("Importing : no tag specified for entry with ID " + str(dic["ID"]))

                # extract deck if present
                if "deck:" in entry :
                    deck_sep = entry.split(sep="deck:")
                    if len(deck_sep) > 2:
                        logging.info("Importing : too many deck specified : " + deck_sep)
                        print(col_red + "Importing : more than 1 specific deck specified : " + deck_sep)
                        print("Use the syntax like this : 'somethingtodo deck:somedeck'" + col_rst)
                        sys.exit()
                    else :
                        space_sep = entry.split(" ")
                        deck=""
                        for word in space_sep:
                            if word[0:5] == "deck:":
                                deck = word[5:]
                                dic["deck"] = [deck]
                        if deck=="":
                            print("Deck specified but not found?!")
                            logging.exit("Importing : deck specified but not found : entry is '" + entry + "'")
                            sys.exit()

#                meta_sep = entry.split(sep="__m:")
#                if len(meta_sep) != 1 :
#                    meta_sep = meta_sep[1:]
#                    for i in meta_sep :
#                        logging.info("Metadata found : ")
#                        print("Metadata specified")
#                        ####TODO
#                        pass

                reconstructed=""# remove syntax from the entry
                for word in dic["entry"][0].split(" "):
                    if "tags:" not in word and "deck:" not in word:
                        reconstructed = reconstructed + " " + word
                reconstructed = reconstructed[1:] # removes the leading whitespace
                dic["entry"] = [reconstructed]
                dic["addentry"] = dic["entry"]
                    
                try :
                    dic["metadata"] = args["metadata"]
                except :
                    logging.info("metadata not specified")
                    dic["metadata"] = ""
                    pass
                process_all_metadata(dic, "RETURN")
                add_entry_todb(dic)
        logging.info("Importing : done")

    if args['rank'] != None:
        # python3 litoy main -r all rev -n 5
        logging.info("Ranks : Displaying ranks, arguments : " + str(args['rank']))
        compute_Global_score()
        condition=""
        if len(args['rank']) not in [0, 1, 2]:
            print("Invalid number of arguments : " + str(args['rank']))
            logging.info("Ranks : Invalid number of arguments : " + str(args['rank']))
            print_syntax_examples()
            sys.exit()
        if args['deck'] is None :
            print("Invalid arguments, you have to specify a deck")
            logging.info("Ranks : missing deck")
            print_syntax_examples()
            sys.exit()
        else : 
            deck = str(args['deck'][0])

        if args['rank']==[] : proceed=True
        else : proceed=False

        if proceed==True or args['rank'][0] == "all" :
            logging.info("Ranks : Printing all entries\n")
            condition = "ID >= 0 AND deck IS '" + deck + "' ORDER BY ID"
        if condition=="" : # order by field 
            condition = "ID >= 0 AND deck IS '" + deck + "' ORDER BY " + str(args['rank'][0])
            logging.info("Ranks : Displaying by field " + str(args['rank'][0]))
        try :
            if str(args['rank'][1]) in "reverse" or str(args['rank'][0]) in "reverse":
                condition = condition + " DESC"
        except :
            condition = condition + " ASC"

        try :
            all_cards = fetch_entry(condition)
        except sqlite3.OperationalError :
            if " DESC" in condition :
                condition = "ID >=0 AND deck IS '" + deck + "' ORDER BY ID DESC"
            if " ASC" in condition :
                condition = "ID >=0 AND deck IS '" + deck + "' ORDER BY ID ASC"
            logging.info("Ranks : Field not foundexiting")
            print("Ranks : Field not found, use ID for example")
            print_syntax_examples()
            sys.exit()
        if len(all_cards)==0 :
            print("Ranks : No cards to display!\nEmpty db?")
            logging.info("Ranks : No cards to display!")
            sys.exit()

        try :
            limit = int(args['nlimit'][0])
        except TypeError:
            limit = int(args['nlimit'])
        if limit < 1:
            print('Ranks : Invalid limit number')
            logging.info('Ranks : Invalid limit number')
            sys.exit()
        else :
            logging.info("Ranks : Displaying only n=" + str(limit))
        all_cards = all_cards[:limit]
        logging.info("Ranks : No limit display")

        pprint.pprint(all_cards, compact=True)
        logging.info("Ranks : Done")

    if args['settings'] != None:
        logging.info('Settings : Change settings, arguments : ' + str(args['settings']))
        # read line by line the settings file
#        file = open("src/litoy/settings.py", "r")
#        for line in file:
#            if settings[0] in line.split(sep=" "):
#                print(line)
#        file.close() 
        logging.info("Settings : Done")

    if args['version'] != False:
        print("Version : Check out github at https://github.com/thiswillbeyourgithub/LiTOY/")
        logging.info("Version : Display version")
        sys.exit()

    if args['ext'] != False:
        print("External : Openning in sqlite browser")
        logging.info("External : Openning in sqlite browser\n")
        current_os = platform.system()
        logging.info("External : OS="+current_os)
        if current_os == "Linux" :
            logging.info("External : launching sqlitebrowser")
            results = subprocess.run([sqlitebrowser_path,"-t", "LITOY", "database.db"])
        else :
            print("External : Only linux can launch sqlite3")
            logging.info("External : failed because not linux")

    if args['editEntry'] != None:
        if len(args['editEntry']) != 3 :
                print("Editentry : ERROR : needs 3 arguments\r    exiting")
                logging.info("Editentry : Entry edit error : needs 3 arguments, provided : " + str(args['editEntry']))
                print_syntax_examples()
                sys.exit()
        if str(args['editEntry'][1]) == "ID":
                print("EditEntry : Error : cannot edit ID, are you sure that's what you want to do ?")
                print("If you really need to alter the ID of an entry, interact directly with the db using sqlitebrowser for example")
                logging.info("EditEntry : Error : cannot edit ID")
                sys.exit()
        condition = str(args['editEntry'][0])
        logging.info("Editentry : Editing entry, arguments : " + str(args['editEntry']))
        editField = str(args['editEntry'][1])
        editValue = str(args['editEntry'][2])
        entry_group = fetch_entry(condition)
        for entry in entry_group:
            if editField not in get_field_names():
                print("Editentry : You're not supposed to create new fields like that!")
                logging.info("Editentry : ERROR : trying to add a new field : " + editField)
                sys.exit()
            editPrevious = str(entry[editField])
            if str(editPrevious) == str(editValue):
                print("Editentry : Not edited : values are identical")
                logging.info("Editentry : Not edited : values are identical")
            else :
                entry[editField] = editValue
                logging.info("Editentry : Changed field " + editField + " from value " + editPrevious + " to value " + editValue)
                print("Editentry : Changing field " + editField + " from value " + editPrevious + " to value " + editValue)
                push_dico(entry, "UPDATE")
                logging.info("Editentry : Done editing field\n")
                print("Editentry : entry is now :")
                pprint.pprint(entry)

    if args['consistency'] != False:
        check_db_consistency()




######################## end routines




if __name__ == "__main__" :
    logging.basicConfig(level=logging.INFO,
            filename = 'logs/rotating_log',
            filemode='a',
            format='%(asctime)s: %(message)s')
    #https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python
    log = logging.getLogger()
    handler = RotatingFileHandler("logs/rotating_log", maxBytes=10*10*1024, backupCount=5)
    log.addHandler(handler)

    main()



