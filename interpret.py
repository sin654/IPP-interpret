# loads XML representation of file/stdin

# • 52 - chyba při sémantických kontrolách vstupního kódu v IPPcode20
# (např. použití nedefinovaného návěští, redefinice proměnné);
# • 53 - běhová chyba interpretace – špatné typy operandů;
# • 54 - běhová chyba interpretace – přístup k neexistující proměnné (rámec existuje);
# • 55 - běhová chyba interpretace – rámec neexistuje (např. čtení z prázdného zásobníku rámců);
# • 56 - běhová chyba interpretace – chybějící hodnota (v proměnné, na datovém zásobníku, nebo v zásobníku volání);
# • 57 - běhová chyba interpretace – špatná hodnota operandu
# (např. dělení nulou, špatná návratová hodnota instrukce EXIT);
# • 58 - běhová chyba interpretace – chybná práce s řetězcem.

import sys  # tisk na stderr
import xml.etree.ElementTree as etree
import re

# parsovani argumentu
global_source = None    # --source
global_input = None     # --input

if len(sys.argv) == 3:  # zadano jmeno + 2 parametry
    if "--source=" in sys.argv[1] and sys.argv[1].index("--source=") == 0:
        global_source = sys.argv[1].replace("--source=", "")
    elif "--source=" in sys.argv[2] and sys.argv[2].index("--source=") == 0:
        global_source = sys.argv[2].replace("--source=", "")
    else:   # chyba
        sys.stderr.write("Chybejici parametr, nebo zakázaná kombinace parametrů.\n")
        exit(10)
    if "--input=" in sys.argv[1] and sys.argv[1].index("--input=") == 0:    # --input=file
        global_input = sys.argv[1].replace("--input=", "")
    elif "--input=" in sys.argv[2] and sys.argv[2].index("--input=") == 0:
        global_input = sys.argv[2].replace("--input=", "")
    else:   # chyba
        sys.stderr.write("Chybejici parametr, nebo zakázaná kombinace parametrů.\n")
        exit(10)
elif len(sys.argv) == 2:    # zadano jmeno +  pouze --help | --input | --source
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print("Program: interpret.py\nInterpret XML formatu jazyka IPPcode20\nParametry:\n--help (vypise tuto zpravu)\n" +
              "--source=file (vstupni soubor s XML reprezentaci zdrojoveho kodu IPPcode20)\n" +
              "--input=file (soubor se vstupy pro samotnou interpretaci zadaneho zdrojoveho kodu)\n" +
              "Alespon jeden z parametru(--source --input) musi byt vzdy zadan. Pokud jeden z nich chybi, " +
              "tak jsou odpovidajici data nacitana ze standardniho vstupu.")
        exit(0)
    elif "--input=" in sys.argv[1] and sys.argv[1].index("--input=") == 0:
        global_input = sys.argv[1].replace("--input=", "")
    elif "--source=" in sys.argv[1] and sys.argv[1].index("--source=") == 0:
        global_source = sys.argv[1].replace("--source=", "")
    else:
        sys.stderr.write("Chybejici parametr, nebo zakázaná kombinace parametrů.\n")
        exit(10)
else:
    sys.stderr.write("Chybejici parametr, nebo zakázaná kombinace parametrů.\n")
    exit(10)
# /parsovani argumentu

# kontrola souboru
if global_source != None and global_input != None:    # zadany oba soubory
    try:
        global_input_file = open(global_input, "r")
        global_input_string = global_input_file.read()
    except FileNotFoundError:
        sys.stderr.write(str(FileNotFoundError))
        exit(11)
    except PermissionError:
        sys.stderr.write(str(PermissionError))
        exit(11)

    try:
        global_source_file = open(global_source, "r")
        global_source_string = global_source_file.read()
    except FileNotFoundError:
        sys.stderr.write(str(FileNotFoundError))
        exit(11)
    except PermissionError:
        sys.stderr.write(str(PermissionError))
        exit(11)
elif global_source != None and global_input == None:    # zadan jen --source
    try:
        global_source_file = open(global_source, "r")
        global_source_string = global_source_file.read()
    except FileNotFoundError:
        sys.stderr.write(str(FileNotFoundError))
        exit(11)
    except PermissionError:
        sys.stderr.write(str(PermissionError))
        exit(11)
elif global_source == None and global_input != None:    # zadan jen --input
    try:
        global_input_file = open(global_input, "r")
        global_input_string = global_input_file.read()
    except FileNotFoundError:
        sys.stderr.write(str(FileNotFoundError))
        exit(11)
    except PermissionError:
        sys.stderr.write(str(PermissionError))
        exit(11)
# /kontrola souboru

# cteni xml ze souboru/stdin
if global_source == None:    # xml se bude brat ze stdin
    xml_string = sys.stdin.read()     # cti stdin do EOF
else:   # mam vstupni xml soubor
    xml_string = global_source_string
# /cteni xml ze souboru/stdin

# cteni z --input souboru/stdin
if global_input != None:    # byl zadan --input=file
    # mam to nactene do global_input_string
    input_array_index = 0
    global_input_string_array = global_input_string.splitlines()
# /cteni z --input souboru/stdin


# kontrola jestli je xml file/string well-formed chyba 31
try:
    root = etree.fromstring(xml_string)
except etree.ParseError as PERR:    # nejake zakladni chyby "well-formed"
    sys.stderr.write("XML parser error: " + str(PERR))
    exit(31)
except:     # nejaky jinny error spojeny s parsem
    sys.stderr.write("XML parser error: not known")
    exit(31)
# /kontrola jestli je xml file/string well-formed chyba 31


# kontrola spravnosti attributu a tagu <program> chyba 32
if root.tag != "program":
    sys.stderr.write("root element neni <program>")
    exit(32)
if len(root.attrib) < 1 or len(root.attrib) >3: # chybi "language", nebo je vic nez max 3 atributy
    sys.stderr.write("<program> ma moc/malo attributu")
    exit(32)
elif len(root.attrib) == 1:
    try:
        if root.attrib["language"] != "IPPcode20":  # povinny attribut
            sys.stderr.write("language != 'IPPcode20'")
            exit(32)
    except KeyError as KERR:
        sys.stderr.write("language neni zadan" + str(KERR))
        exit(32)
elif len(root.attrib) == 2:  # zadany 2 attributy (musi byt language + name/description)
    try:
        if root.attrib["language"] != "IPPcode20":
            sys.stderr.write("language != 'IPPcode20'")
            exit(32)
        try:
            if root.attrib["name"] != "":   # je tam name
                ...  # 2 attributy (languame a name -> vse OK)
        except KeyError as KERR:    #neni tam name
            try:
                if root.attrib["description"] != "":  # je tam description
                    ...  # 2 attributy (languame a description -> vse OK)
            except KeyError as KERR:
                sys.stderr.write("zadany 2 attributy a druhy neni name/description")
                exit(32)
    except KeyError as KERR:
        sys.stderr.write("neni zadan language" + str(KERR))
        exit(32)
elif len(root.attrib) == 3:  # zadany 3 attributy (musi byt language + name + description)
    try:
        if root.attrib["language"] != "IPPcode20":
            sys.stderr.write("language != 'IPPcode20'")
            exit(32)
        elif root.attrib["name"] != "" and root.attrib["description"] != "":
            ...  # vse zadano -> OK
    except KeyError as KERR:    # nejaky attribut neni v tom slovniku root.attrib
        sys.stderr.write("3 attributy, ale nejaky z language/name/description chybi")
        exit(32)
# /kontrola spravnosti attributu a tagu <program> chyba 32


# vytvoření prázdného globálního rámce, vytvoreni prazdneho slovniku labelu, datovy zasobnik
global_frame = {}
local_frame = []
tmp_frame = None

data_stack = []
call_stack = []

global_label_dictionary = {}
global_possible_instruction_opcode = {"MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN",
                                      "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR",
                                      "NOT", "INT2CHAR", "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR",
                                      "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "EXIT", "DPRINT",
                                      "BREAK", "CLEARS", "ADDS", "SUBS", "MULS", "IDIVS", "LTS", "GTS", "EQS", "ANDS",
                                      "ORS", "NOTS", "INT2CHARS", "STRI2INTS", "JUMPIFEQS", "JUMPIFNEQS"}



"""
funkce na nacteni LABEL do global_label_dictionary
+ testuje, jestli nejaky LABEL nebyl redefinovan (chyba 52) 
"""
def make_label_dictionary():
    for index_root in range(0, len(root)):
        if root[index_root].attrib["opcode"].upper() == "LABEL":
            arguments = sort_arguments(index_root, 1)   # vyzadovan 1 argument
            if arguments[0][1] == "label":  # type="label"
                # test jmena promenne pres regex
                if re.fullmatch(r'[a-žA-Ž_\-$&%*!?][\w_\-$&%*!?]*', arguments[0][0]) is None:
                    sys.stderr.write("make_label_dictionary: jmeno labelu neodpovida regexu")
                    exit(32)
                if arguments[0][0] not in global_label_dictionary:  # test redefinice
                    global_label_dictionary[arguments[0][0]] = root[index_root].attrib["order"]
                else:   # pokousime se redefinovat navesti
                    sys.stderr.write("make_label_dictionary: pokus o redefinici navesti")
                    exit(52)
            else:  # asi chyba 32?
                sys.stderr.write(
                    "make_label_dictionary: u instrukce LABEL je argument, ktery nema type='label'")
                exit(32)



"""
funkce na vytvoření slovníku s hodnotami "ORDER":INDEX_DO_ROOT
@return (slovnik "order":index -do pole root)
"""
def make_instuction_dictionary():
    instruction_dictionary = {}
    global global_label_dictionary
    global root
    for index_root in range(0, len(root)):
        instruction_dictionary[root[index_root].attrib["order"]] = index_root
    return instruction_dictionary


"""
funkce na vytvoreni pole, ktere bude obsahovat hodnoty attributu "order" z XML instrukci
pole bude serazeno vzestupne
@return (vraci vzestupne serazene pole s hodnotami "order" instrukci napr. ['1', '2', '3', '6', '8'])
+ kontroluje, zda hodnota "order" neni duplicitni 32
+ kontroluje, zda jsou instrukce uzavreny v tagu <instruction> 32
+ kontroluje, zda "opcode" instrukce je platny (a jestli tam vubec je)
+ kontroluje, zda "order" neni zaporny (a jestli tam vubec je)
+ kontroluje, zda ma instrukce pouze 2 povine parametry
"""
def make_sorted_instruction_order():
    # prvni pruchod
    instruction_order_array = []
    global root
    global global_possible_instruction_opcode
    for instruction in root:  # prochazim instrukce
        if instruction.tag != "instruction":  # kontrola, zda se instrukce nachazi v tagu <instruction>
            sys.stderr.write("Error: instrukce uzavrena v jinem tagu nez <instruction> ")
            exit(32)
        try:
            if instruction.attrib["opcode"].upper() not in global_possible_instruction_opcode:  # kontrola zda je pouzita platna instrukce
                sys.stderr.write("make_sorted_instruction_order: neznamy 'opcode' instrukce")
                exit(32)
            elif int(instruction.attrib["order"]) < 0:  # kontrola, zda order neni zaporny
                sys.stderr.write("make_sorted_instruction_order: zaporna hodnota order")
                exit(32)
            elif int(instruction.attrib["order"]) in instruction_order_array:   # kontrola zda neni duplicitni "order"
                sys.stderr.write("make_sorted_instruction_order: duplicitni hodnota 'order' u instrukce")
                exit(32)
            elif len(instruction.attrib) > 2:   # kontrola zda nejsou uvedene nepovolene parametry (musi byt presne 2)
                sys.stderr.write("make_sorted_instruction_order: uvedeny nepovolene .attrib u instrukce")
                exit(32)
            # vse je OK
            instruction_order_array.append(int(instruction.attrib["order"]))    # pridam si "order" do naseho pole
        except KeyError:    # "order" chybi
            sys.stderr.write("make_sorted_instruction_order: " + str(KeyError) + " order/opcode chybi")
            exit(32)
    instruction_order_array.sort()  # sort vzestupne
    # pretypovani celeho pole  na str (bude se s tim pote lepe pracovat)
    for i in range(0, len(instruction_order_array)):
        instruction_order_array[i] = str(instruction_order_array[i])
    return instruction_order_array


"""
funkce na preskladani argumentu INSTRUKCE, vraci pole s usporadanymi argumenty od arg1 ... arg3
@param [number_of_instruction] - pozice instrukce v XML dokumentu - (0-n)
@param [required_count_of_arguments] - pocet parametru instrukce - (0-3) (kdyz bude zadana 0, tak pouze otestuje, zda je v XML 0 parametru
@return (vraci pole, ve kterem jsou hodnoty ["hodnota", "typ"])
+ kontroluje jestli ma INSTRUKCE spavny pocet parametru (pripadne spravne ocislovane atd.) chyba 32
"""
def sort_arguments(number_of_instruction, required_count_of_arguments):
    # preskladani argumentu instrukce dane number_of_instruction do argument_array (argument_array[0] == arg1 ...)
    argument_array = ["", "", ""]  # toto je dobra prasarna (C ish deklarace velikosti pole :) )
    try:
        for i in range(0, len(root[number_of_instruction])):
            if "arg1" == root[number_of_instruction][i].tag:
                argument_array[0] = [root[number_of_instruction][i].text, root[number_of_instruction][i].attrib["type"]]
            elif "arg2" == root[number_of_instruction][i].tag:
                argument_array[1] = [root[number_of_instruction][i].text, root[number_of_instruction][i].attrib["type"]]
            elif "arg3" == root[number_of_instruction][i].tag:
                argument_array[2] = [root[number_of_instruction][i].text, root[number_of_instruction][i].attrib["type"]]
    except KeyError:
        sys.stderr.write("sort_arguments: " + str(KeyError) + " pravdepodobne chyby 'type' u argumentu instrukce")
        exit(32)

    # otestuju, jestli argumenty odpovidaji poctu
    if required_count_of_arguments == len(root[number_of_instruction]):                 # pocet odpovida, ale treba budou spatne ocislovane
        if required_count_of_arguments == 1 and (argument_array[0] == "" or argument_array[1] != "" or argument_array[2] != ""):
            sys.stderr.write("sort_arguments: spatne cislovane argumenty instrukce ...")
            exit(32)
        elif required_count_of_arguments == 2 and (argument_array[0] == "" or argument_array[1] == "" or argument_array[2] != ""):
            sys.stderr.write("sort_arguments: spatne cislovane argumenty instrukce ...")
            exit(32)
        elif required_count_of_arguments == 3 and (argument_array[0] == "" or argument_array[1] == "" or argument_array[2] == ""):
            sys.stderr.write("sort_arguments: spatne cislovane argumenty instrukce ...")
            exit(32)
    elif required_count_of_arguments == 0 and len(root[number_of_instruction]) != 0:    # instrukce nema mit zadny argument a nejaky ma (asi chyba 32?)
        sys.stderr.write("sort_arguments: spatny pocet argumentu instrukce")
        exit(32)
    elif required_count_of_arguments == 1 and len(root[number_of_instruction]) != 1:    # ma mit jeden a ma !=1
        sys.stderr.write("sort_arguments: spatny pocet argumentu instrukce")
        exit(32)
    elif required_count_of_arguments == 2 and len(root[number_of_instruction]) != 2:    # ma mit dva a ma !=2
        sys.stderr.write("sort_arguments: spatny pocet argumentu instrukce")
        exit(32)
    elif required_count_of_arguments == 3 and len(root[number_of_instruction]) != 3:    # ma mit tri a ma !=3
        sys.stderr.write("sort_arguments: spatny pocet argumentu instrukce")
        exit(32)

    return argument_array

"""
funkce na zjistneni, zda existuje ramec promenne a zda je definovana
@return vraci True, pokud je ma promenna ramec a je definovana
"""
def is_variable_defined(argument):
    if argument[1] != "var":
        sys.stderr.write("is_variable_defined: prvni argument neni var")
        exit(53)
    else:
        # test jmena promenne pres regex
        if re.fullmatch(r'[GLT]F@[a-žA-Ž_\-$&%*!?][\w_\-$&%*!?]*', argument[0]) is None:
            sys.stderr.write("is_variable_defined: jmeno promenne neodpovida regexu")
            exit(32)
        if "GF@" in argument[0] and argument[0].index("GF@") == 0:  # global frame
            if argument[0].replace("GF@", "") in global_frame:
                return True
            else:
                sys.stderr.write("is_variable_defined: promenna GF neni definovana")
                exit(54)    # pristup k neexistujici promenne (ramec existuje)
        elif "LF@" in argument[0] and argument[0].index("LF@") == 0:  # local frame
            if len(local_frame) == 0:  # ramec neexistuje
                sys.stderr.write("is_variable_defined: ramec LF neexistuje")
                exit(55)
            else:
                if argument[0].replace("LF@", "") in local_frame[-1]:
                    return True
                else:
                    sys.stderr.write("is_variable_defined: promenna LF neni definovana")
                    exit(54)
        elif "TF@" in argument[0] and argument[0].index("TF@") == 0:  # temporary frame
            if tmp_frame is None:  # ramec neexistuje
                sys.stderr.write("is_variable_defined: ramec TF neexistuje")
                exit(55)
            else:
                if argument[0].replace("TF@", "") in tmp_frame:
                    return True
                else:
                    sys.stderr.write("is_variable_defined: promenna TF neni definovana")
                    exit(54)
        else:  # chybi definice ramce
            sys.stderr.write("is_variable_defined: promenne chybi ramec")
            exit(53)  # spatny typ operandu

"""
funkce na kontrolu attributu (vráti jeho [hodnota, typ]), pracuje s promennymi i konstantami
@param (cela polozka argumentum napr. arguments[1] ...)
@return [hodnota, typ] kde hodnota uz bude jako z Pythonu a ne jen prosty retezec
"""
def get_val_type_of_argument(argument):
    # pracuju s polem [hodnota, typ]
    if argument[1] == "var":
        # test jmena promenne pres regex
        if re.fullmatch(r'[GLT]F@[a-žA-Ž_\-$&%*!?][\w_\-$&%*!?]*', argument[0]) is None:
            sys.stderr.write("get_val_type_of_argument: jmeno promenne neodpovida regexu")
            exit(32)
        if "GF@" in argument[0] and argument[0].index("GF@") == 0:
            # kontrola existence promenne, pak kontrola inicializace
            if argument[0].replace("GF@", "") in global_frame:
                if global_frame[argument[0].replace("GF@", "")][0] is None and global_frame[argument[0].replace("GF@", "")][1] is None:     # neinicializovana promenna
                    sys.stderr.write("get_val_type_of_argument: chybejici hodnota v promenne")
                    exit(56)  # chybejici hodnota
                else:
                    return [global_frame[argument[0].replace("GF@", "")][0], global_frame[argument[0].replace("GF@", "")][1]]
            else:
                sys.stderr.write("get_val_type_of_argument: promenna GF neni definovana")
                exit(54)  # pristup k neexistujici promenne (ramec existuje)
        elif "LF@" in argument[0] and argument[0].index("LF@") == 0:
            # kontrola ramce, pak kontrola existence promenne, pak kontrola inicializace promenne
            if len(local_frame) > 0:    # v zasobniku LF ramcu nejaky ramec existuje
                if argument[0].replace("LF@", "") in local_frame[-1]:    # definovana promenna?
                    if local_frame[-1][argument[0].replace("LF@", "")][0] is None and local_frame[-1][argument[0].replace("LF@", "")][1] is None:    # je promenna inicializovana?
                        sys.stderr.write("get_val_type_of_argument: chybejici hodnota v promenne")
                        exit(56)  # chybejici hodnota
                    else:   # promenna je inicializovana
                        return [local_frame[-1][argument[0].replace("LF@", "")][0], local_frame[-1][argument[0].replace("LF@", "")][1]]
                else:
                    sys.stderr.write("get_val_type_of_argument: promenna LF neni definovana")
                    exit(54)  # pristup k neexistujici promenne (ramec existuje)
            else:
                sys.stderr.write("get_val_type_of_argument: ramec LF neexistuje")
                exit(55)
        elif "TF@" in argument[0] and argument[0].index("TF@") == 0:
            # kontrola ramce, pak kontrola existence promenne, pak kontrola inicializace promenne
            if tmp_frame is not None:   # ramec TF byl vytvoren pres CREATEFRAME
                if argument[0].replace("TF@", "") in tmp_frame:
                    if tmp_frame[argument[0].replace("TF@", "")][0] is None and tmp_frame[argument[0].replace("TF@", "")][1] is None:    # je inicializovana?
                        sys.stderr.write("get_val_type_of_argument: chybejici hodnota v promenne")
                        exit(56)  # chybejici hodnota
                    else:
                        return [tmp_frame[argument[0].replace("TF@", "")][0], tmp_frame[argument[0].replace("TF@", "")][1]]
                else:
                    sys.stderr.write("get_val_type_of_argument: promenna TF neni definovana")
                    exit(54)  # pristup k neexistujici promenne (ramec existuje)
            else:
                sys.stderr.write("get_val_type_of_argument: ramec TF neexistuje")
                exit(55)
        else:
            exit(53)    # spatna hodnota operandu
    elif argument[1] == "int":
        # pokus o pretypovani a navrat
        try:
            return [int(argument[0]), "int"]
        except ValueError:
            sys.stderr.write("get_val_type_of_argument: fail pretypovani na int")
            exit(53)    # spatne typy operandu
    elif argument[1] == "string":
        # string se nebude pretypovavat, ale jen menit reprezentace escape sekvenci
        if argument[0] is None:     # predany prazdny retezec
            return ["", "string"]
        try:
            tested_string = argument[0]
            iterator = re.findall(r'\\\d\d\d', tested_string)
            if len(iterator) != len(re.findall(r'\\', tested_string)):
                sys.stderr.write("string: je tam zpetne lomitko mimo escape sekvenci")
                exit(32)
            if re.search(r'[#\s]', tested_string) is not None:
                sys.stderr.write("string: je tam # regex")
                exit(32)

            for escape in iterator:
                escape_char = int(escape.replace("\\", ""))
                if escape_char == 92:  # zpetne lomitko
                    escape_char = "\\\\"  # jen jedno lomitko by v tom stringu byla escape sekvence
                else:
                    escape_char = chr(escape_char)
                y = re.sub(r'\\\d\d\d', escape_char, tested_string, 1)
                tested_string = y
        except:
            sys.stderr.write("string: nahrada escape sekvenci fail NECO")
            exit(32)
        return [tested_string, "string"]
    elif argument[1] == "nil":
        if argument[0] != "nil":
            sys.stderr.write("get_val_type_of_argument: nil nema hodnotu nil")
            exit(53)
        else:
            return [None, "nil"]
    elif argument[1] == "bool":
        if argument[0] == "true":
            return [True, "bool"]
        elif argument[0] == "false":
            return [False, "bool"]
        else:
            sys.stderr.write("get_val_type_of_argument: bool neni true/false")
            exit(53)
    else:
        sys.stderr.write("get_val_type_of_argument: neplatny typ argumentu")
        exit(53)

"""
funkce na zjisteni typu
"""
def get_type_of_argument(argument):
    # pracuju s polem [hodnota, typ]
    if argument[1] == "var":
        # test jmena promenne pres regex
        if re.fullmatch(r'[GLT]F@[a-žA-Ž_\-$&%*!?][\w_\-$&%*!?]*', argument[0]) is None:
            sys.stderr.write("get_type_of_argument: jmeno promenne neodpovida regexu")
            exit(32)
        if "GF@" in argument[0] and argument[0].index("GF@") == 0:
            # kontrola existence promenne
            if argument[0].replace("GF@", "") in global_frame:
                return global_frame[argument[0].replace("GF@", "")][1]
            else:
                sys.stderr.write("get_type_of_argument: promenna GF neni definovana")
                exit(54)  # pristup k neexistujici promenne (ramec existuje)
        elif "LF@" in argument[0] and argument[0].index("LF@") == 0:
            # kontrola ramce, pak kontrola existence promenne
            if len(local_frame) > 0:    # v zasobniku LF ramcu nejaky ramec existuje
                if argument[0].replace("LF@", "") in local_frame[-1]:    # definovana promenna?
                    return local_frame[-1][argument[0].replace("LF@", "")][1]
                else:
                    sys.stderr.write("get_type_of_argument: promenna LF neni definovana")
                    exit(54)  # pristup k neexistujici promenne (ramec existuje)
            else:
                sys.stderr.write("get_type_of_argument: ramec LF neexistuje")
                exit(55)
        elif "TF@" in argument[0] and argument[0].index("TF@") == 0:
            # kontrola ramce, pak kontrola existence promenne, pak kontrola inicializace promenne
            if tmp_frame is not None:   # ramec TF byl vytvoren pres CREATEFRAME
                if argument[0].replace("TF@", "") in tmp_frame:
                    return tmp_frame[argument[0].replace("TF@", "")][1]
                else:
                    sys.stderr.write("get_type_of_argument: promenna TF neni definovana")
                    exit(54)  # pristup k neexistujici promenne (ramec existuje)
            else:
                sys.stderr.write("get_type_of_argument: ramec TF neexistuje")
                exit(55)
        else:
            exit(53)    # spatna hodnota operandu
    elif argument[1] == "int":
        # pokus o pretypovani a navrat
        try:
            int(argument[0])
            return "int"
        except ValueError:
            sys.stderr.write("get_type_of_argument: fail pretypovani na int")
            exit(53)  # spatne typy operandu
    elif argument[1] == "string":
        # kontrola string konstanty regexem
        try:
            tested_string = argument[0]
            iterator = re.findall(r'\\\d\d\d', tested_string)
            if len(iterator) != len(re.findall(r'\\', tested_string)):
                sys.stderr.write("string: je tam zpetne lomitko mimo escape sekvenci")
                exit(32)
            if re.search(r'[#\s]', tested_string) is not None:
                sys.stderr.write("string: je tam # regex")
                exit(32)

            for escape in iterator:
                escape_char = int(escape.replace("\\", ""))
                if escape_char == 92:  # zpetne lomitko
                    escape_char = "\\\\"  # jen jedno lomitko by v tom stringu byla escape sekvence
                else:
                    escape_char = chr(escape_char)
                y = re.sub(r'\\\d\d\d', escape_char, tested_string, 1)
                tested_string = y
        except:
            sys.stderr.write("string: nahrada escape sekvenci fail NECO")
            exit(32)
        return "string"
    elif argument[1] == "nil":
        if argument[0] == "nil":
            return "nil"
        else:
            sys.stderr.write("get_type_of_argument: typ 'nil' nema hodnotu nil")
            exit(53)
    elif argument[1] == "bool":
        if argument[0] == "true" or argument[0] == "false":
            return "bool"
        else:
            sys.stderr.write("get_type_of_argument: typ 'bool' nema hodnotu true/false")
            exit(53)
    else:
        sys.stderr.write("get_type_of_argument: neplatny typ argumentu")
        exit(53)


# root je tu jako <program> v XML
# root.attrib slovník atrubutů daného elementu
# root.text je text daného elementu
# pro přístup k pod elementům použijeme root[1][0] ... seznamová struktura

# zpracovani xml souboru
sorted_instruction_order_list = make_sorted_instruction_order()
#print(sorted_instruction_order_list)
# slovnik instrukci "order":index do root[index]
instruction_dict = make_instuction_dictionary()
#print(instruction_dict)

make_label_dictionary()
#print(global_label_dictionary)





# zacatek provedenim prvni instrukce manualne (pote si tok rizeni a posun v instrukcich budou resit samotne instrukce)
# DO
# root[index]

"""
pomocna funkce na postupne spousteni instukci ve funkci run(index_of_instruction in root)
"""
def start_program():
    index_to_sorted_order_list = 0
    while index_to_sorted_order_list < len(sorted_instruction_order_list):
        next_instruction = run(instruction_dict[sorted_instruction_order_list[index_to_sorted_order_list]])
        if next_instruction == True:    # run() vraci True, kdyz mame pokracovat dalsi instrukci v poradi
            index_to_sorted_order_list += 1
        else:   # run() vraci "order" dalsi instrukce, ktera se ma provest (JUMP...)
            # zde musim nastavit index_to_sorted_order_list na odpovidajici hodnotu po skoku
            index_to_sorted_order_list = sorted_instruction_order_list.index(next_instruction)
    # vsechny instrukce se provedly uspesne (ukoncuji interpret s navratovym kodem 0)
    exit(0)

"""
funkce na provedeni instrukce
@param (index do root[] kde se nachazi instrukce na provedeni)
@return (True - bude se provadet dalsi instrukce v poradi, "order" instrukce pokud se jedna o skok)
"""
def run(index_of_instruction):
    global tmp_frame
    global root
    global sorted_instruction_order_list
    global instruction_dict
    global global_frame
    global local_frame
    global input_array_index
    global global_input_string_array
    global call_stack
    global data_stack

    #print(global_frame)
    #print(local_frame)
    #print(tmp_frame)
    #print(data_stack)
    #print(call_stack)
    #print("\n")

    attributes = root[index_of_instruction].attrib

    # DONE
    # ---------------------------------------------------------------------------------------------------
    if attributes["opcode"].upper() == "MOVE":  # kontrola op code, case-insensitive
        #provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 2)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:
            if "GF@" in arguments[0][0]:
                global_frame[arguments[0][0].replace("GF@", "")] = get_val_type_of_argument(arguments[1])
            elif "LF@" in arguments[0][0]:
                local_frame[-1][arguments[0][0].replace("LF@", "")] = get_val_type_of_argument(arguments[1])
            elif "TF@" in arguments[0][0]:
                tmp_frame[arguments[0][0].replace("TF@", "")] = get_val_type_of_argument(arguments[1])
        # presun na dalsi instrukci
        return True
    # ---------------------------------------------------------------------------------------------------


    # DONE
    # ---------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "CREATEFRAME":
        #provedeni instrukce
        sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        tmp_frame = {}
        # prechod na dalsi instrukci
        return True
    # ---------------------------------------------------------------------------------------------------

    # DONE
    # ---------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "PUSHFRAME":
        # provedeni instrukce
        sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if tmp_frame is None:    # TF je nedefinovany
            sys.stderr.write("PUSHFRAME: ramec TF neexistuje")
            exit(55)
        else:
            local_frame.append(tmp_frame)   # presune TF na zasobnik ramcu LF
        tmp_frame = None
        # prechod na dalsi instrukci
        return True
    # ---------------------------------------------------------------------------------------------------

    # DONE
    # ---------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "POPFRAME":
        # provedeni instrukce
        sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if len(local_frame) == 0:     # LF zasobnik je prazdny
            sys.stderr.write("POPFRAME: prazdny LF zasobnik")
            exit(55)
        tmp_frame = local_frame.pop()   # vrcholovy ramec z LF presune do TF
        # presun na dalsi instrukci
        return True
    # ---------------------------------------------------------------------------------------------------

    # DONE revised
    # --------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "DEFVAR":  # DEFVAR <var>
        #vykonani instrukce
        arguments = sort_arguments(index_of_instruction, 1) # nacteni argumentu instrukce
        if arguments[0][1] != "var":  # spatny typ operandu
            sys.stderr.write("DEFVAR: spatny typ operandu")
            exit(53)
        else:
            # test jmena promenne pres regex
            if re.fullmatch(r'[GLT]F@[a-žA-Ž_\-$&%*!?][\w_\-$&%*!?]*', arguments[0][0]) is None:
                sys.stderr.write("DEFVAR: jmeno promenne neodpovida regexu")
                exit(32)
            if "GF@" in arguments[0][0] and arguments[0][0].index("GF@") == 0:  # global frame
                if arguments[0][0].replace("GF@", "") in global_frame:     # check, ze tam uz neni -> redefinice 52
                    sys.stderr.write("DEFVAR: redefinice promenne GF")
                    exit(52)
                else:
                    global_frame[arguments[0][0].replace("GF@", "")] = [None, None]
            elif "LF@" in arguments[0][0] and arguments[0][0].index("LF@") == 0:   # local frame
                if len(local_frame) == 0:  # ramec neexistuje
                    sys.stderr.write("DEFVAR: ramec LF neexistuje")
                    exit(55)
                else:
                    if arguments[0][0].replace("LF@", "") in local_frame[-1]:  # redefinice promenne
                        sys.stderr.write("DEFVAR: redefinice promenne LF")
                        exit(52)
                    else:
                        local_frame[-1][arguments[0][0].replace("LF@", "")] = [None, None]
            elif "TF@" in arguments[0][0] and arguments[0][0].index("TF@") == 0:   # temporary frame
                if tmp_frame is None:  # ramec neexistuje
                    sys.stderr.write("DEFVAR: ramec TF neexistuje")
                    exit(55)
                else:
                    if arguments[0][0].replace("TF@", "") in tmp_frame:  # redefinice promenne
                        sys.stderr.write("DEFVAR: redefinice promenne TF")
                        exit(52)
                    else:
                        tmp_frame[arguments[0][0].replace("TF@", "")] = [None, None]
            else:   # chybi definice ramce
                sys.stderr.write("DEFVAR: promenne chybi ramec")
                exit(53)    # spatny typ operandu
        # pokracovani dalsi instrukci / konec programu
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "CALL":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 1)  # nacteni argumentu instrukce
        if arguments[0][1] != "label":
            sys.stderr.write("CALL: type neni label")
            exit(53)
        # ulozeni inkrementovane aktualni hodnoty do zasobniku volani
        try:
            call_stack.append(sorted_instruction_order_list[sorted_instruction_order_list.index(root[index_of_instruction].attrib["order"]) + 1])
        except IndexError:  # CALL je jako posledni instrukce v programu
            call_stack.append(None)
        if arguments[0][0] in global_label_dictionary:
            # presun na pozici navesti <label> arguments[0][0]
            # run(instruction_dict[global_label_dictionary[arguments[0][0]]])
            return global_label_dictionary[arguments[0][0]]
        else:
            sys.stderr.write("CALL: pokus o skok na neexistujici navesti")
            exit(52)
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "RETURN":
        # provedeni instrukce
        sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce (kontrola)
        if len(call_stack) > 0:     # zasobnik volani neni prazdny
            next_instr = call_stack.pop()
            if next_instr is not None:
                return next_instr
            else:   # call na ktery byl proveden return byla posledni instrukce programu
                exit(0)
        else:
            sys.stderr.write("RETURN: zasovnik volani je prazdny")
            exit(56)
        #return True
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "PUSHS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 1)  # nacteni argumentu instrukce
        data_stack.append(get_val_type_of_argument(arguments[0]))
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "POPS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 1)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:
            if len(data_stack) > 0:
                if "GF@" in arguments[0][0]:
                    global_frame[arguments[0][0].replace("GF@", "")] = data_stack.pop()
                elif "LF@" in arguments[0][0]:
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = data_stack.pop()
                elif "TF@" in arguments[0][0]:
                    tmp_frame[arguments[0][0].replace("TF@", "")] = data_stack.pop()
            else:   # prazdny data_stack
                sys.stderr.write("POPS: pokus o cteni z prazdneho datoveho zasobniku")
                exit(56)
        # presun na dalsi isntrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "ADD":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:   # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] + argument2[0], "int"]
                else:
                    sys.stderr.write("ADD: spatne typy operandu")
                    exit(53)    # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] + argument2[0], "int"]
                else:
                    sys.stderr.write("ADD: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] + argument2[0], "int"]
                else:
                    sys.stderr.write("ADD: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "SUB":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] - argument2[0], "int"]
                else:
                    sys.stderr.write("SUB: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] - argument2[0], "int"]
                else:
                    sys.stderr.write("SUB: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] - argument2[0], "int"]
                else:
                    sys.stderr.write("SUB: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "MUL":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] * argument2[0], "int"]
                else:
                    sys.stderr.write("MUL: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] * argument2[0], "int"]
                else:
                    sys.stderr.write("MUL: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] * argument2[0], "int"]
                else:
                    sys.stderr.write("MUL: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "IDIV":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    if argument2[0] != 0:
                        global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] // argument2[0], "int"]
                    else:   # deleni 0
                        sys.stderr.write("IDIV: deleni 0")
                        exit(57)
                else:
                    sys.stderr.write("IDIV: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    if argument2[0] != 0:
                        local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] // argument2[0], "int"]
                    else:   # deleni 0
                        sys.stderr.write("IDIV: deleni 0")
                        exit(57)
                else:
                    sys.stderr.write("IDIV: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int" and argument2[1] == "int":
                    if argument2[0] != 0:
                        tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] // argument2[0], "int"]
                    else:   # deleni 0
                        sys.stderr.write("IDIV: deleni 0")
                        exit(57)
                else:
                    sys.stderr.write("IDIV: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "LT":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry stejneho typu
                if argument1[1] == "int" and argument2[1] == "int":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] < argument2[0], "bool"]
                elif argument1[1] == "string" and argument2[1] == "string":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] < argument2[0], "bool"]
                elif argument1[1] == "bool" and argument2[1] == "bool":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] < argument2[0], "bool"]
                else:
                    sys.stderr.write("LT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry stejneho typu
                if argument1[1] == "int" and argument2[1] == "int":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] < argument2[0], "bool"]
                elif argument1[1] == "string" and argument2[1] == "string":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] < argument2[0], "bool"]
                elif argument1[1] == "bool" and argument2[1] == "bool":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] < argument2[0], "bool"]
                else:
                    sys.stderr.write("LT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry stejneho typu
                if argument1[1] == "int" and argument2[1] == "int":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] < argument2[0], "bool"]
                elif argument1[1] == "string" and argument2[1] == "string":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] < argument2[0], "bool"]
                elif argument1[1] == "bool" and argument2[1] == "bool":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] < argument2[0], "bool"]
                else:
                    sys.stderr.write("LT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "GT":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry stejneho typu
                if argument1[1] == "int" and argument2[1] == "int":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] > argument2[0], "bool"]
                elif argument1[1] == "string" and argument2[1] == "string":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] > argument2[0], "bool"]
                elif argument1[1] == "bool" and argument2[1] == "bool":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] > argument2[0], "bool"]
                else:
                    sys.stderr.write("GT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry stejneho typu
                if argument1[1] == "int" and argument2[1] == "int":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] > argument2[0], "bool"]
                elif argument1[1] == "string" and argument2[1] == "string":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] > argument2[0], "bool"]
                elif argument1[1] == "bool" and argument2[1] == "bool":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] > argument2[0], "bool"]
                else:
                    sys.stderr.write("GT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry stejneho typu
                if argument1[1] == "int" and argument2[1] == "int":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] > argument2[0], "bool"]
                elif argument1[1] == "string" and argument2[1] == "string":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] > argument2[0], "bool"]
                elif argument1[1] == "bool" and argument2[1] == "bool":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] > argument2[0], "bool"]
                else:
                    sys.stderr.write("GT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "EQ":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry stejneho typu
                if argument1[1] == "nil" or argument2[1] == "nil":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] == argument2[0], "bool"]
                elif argument1[1] == "int" and argument2[1] == "int":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] == argument2[0], "bool"]
                elif argument1[1] == "string" and argument2[1] == "string":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] == argument2[0], "bool"]
                elif argument1[1] == "bool" and argument2[1] == "bool":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] == argument2[0], "bool"]
                else:
                    sys.stderr.write("EQ: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry stejneho typu
                if argument1[1] == "nil" or argument2[1] == "nil":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] == argument2[0], "bool"]
                elif argument1[1] == "int" and argument2[1] == "int":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] == argument2[0], "bool"]
                elif argument1[1] == "string" and argument2[1] == "string":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] == argument2[0], "bool"]
                elif argument1[1] == "bool" and argument2[1] == "bool":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] == argument2[0], "bool"]
                else:
                    sys.stderr.write("EQ: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry stejneho typu
                if argument1[1] == "nil" or argument2[1] == "nil":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] == argument2[0], "bool"]
                elif argument1[1] == "int" and argument2[1] == "int":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] == argument2[0], "bool"]
                elif argument1[1] == "string" and argument2[1] == "string":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] == argument2[0], "bool"]
                elif argument1[1] == "bool" and argument2[1] == "bool":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] == argument2[0], "bool"]
                else:
                    sys.stderr.write("EQ: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------



    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "AND":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu bool
                if argument1[1] == "bool" and argument2[1] == "bool":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] and argument2[0], "bool"]
                else:
                    sys.stderr.write("AND: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu bool
                if argument1[1] == "bool" and argument2[1] == "bool":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] and argument2[0], "bool"]
                else:
                    sys.stderr.write("AND: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "bool" and argument2[1] == "bool":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] and argument2[0], "bool"]
                else:
                    sys.stderr.write("AND: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "OR":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu bool
                if argument1[1] == "bool" and argument2[1] == "bool":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] or argument2[0], "bool"]
                else:
                    sys.stderr.write("OR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu bool
                if argument1[1] == "bool" and argument2[1] == "bool":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] or argument2[0], "bool"]
                else:
                    sys.stderr.write("OR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "bool" and argument2[1] == "bool":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] or argument2[0], "bool"]
                else:
                    sys.stderr.write("OR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "NOT":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 2)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu bool
                if argument1[1] == "bool":
                    global_frame[arguments[0][0].replace("GF@", "")] = [not argument1[0], "bool"]
                else:
                    sys.stderr.write("NOT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu bool
                if argument1[1] == "bool":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [not argument1[0], "bool"]
                else:
                    sys.stderr.write("NOT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu bool
                if argument1[1] == "bool":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [not argument1[0], "bool"]
                else:
                    sys.stderr.write("NOT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "INT2CHAR":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 2)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int":
                    try:
                        global_frame[arguments[0][0].replace("GF@", "")] = [chr(argument1[0]), "string"]
                    except ValueError:
                        sys.stderr.write("INT2CHAR: chr(int) nevalidni ordinalni hodnota")
                        exit(58)
                else:
                    sys.stderr.write("INT2CHAR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int":
                    try:
                        local_frame[-1][arguments[0][0].replace("LF@", "")] = [chr(argument1[0]), "string"]
                    except ValueError:
                        sys.stderr.write("INT2CHAR: chr(int) nevalidni ordinalni hodnota")
                        exit(58)
                else:
                    sys.stderr.write("INT2CHAR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu int
                if argument1[1] == "int":
                    try:
                        tmp_frame[arguments[0][0].replace("TF@", "")] = [chr(argument1[0]), "string"]
                    except ValueError:
                        sys.stderr.write("INT2CHAR: chr(int) nevalidni ordinalni hodnota")
                        exit(58)
                else:
                    sys.stderr.write("INT2CHAR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "STRI2INT":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametr1 je string, parametr2 je int
                if argument1[1] == "string" and argument2[1] == "int":
                    try:
                        global_frame[arguments[0][0].replace("GF@", "")] = [ord(argument1[0][argument2[0]]), "int"]
                    except IndexError:
                        sys.stderr.write("STRI2INT: ord(char) indexovani mimo retezec")
                        exit(58)
                    except TypeError:
                        sys.stderr.write("STRI2INT: ord(char) char je nevalidni hodnota")
                        exit(58)
                else:
                    sys.stderr.write("STRI2INT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametr1 je string, parametr2 je int
                if argument1[1] == "string" and argument2[1] == "int":
                    try:
                        local_frame[-1][arguments[0][0].replace("LF@", "")] = [ord(argument1[0][argument2[0]]), "int"]
                    except IndexError:
                        sys.stderr.write("STRI2INT: ord(char) indexovani mimo retezec")
                        exit(58)
                    except TypeError:
                        sys.stderr.write("STRI2INT: ord(char) char je nevalidni hodnota")
                        exit(58)
                else:
                    sys.stderr.write("STRI2INT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametr1 je string, parametr2 je int
                if argument1[1] == "string" and argument2[1] == "int":
                    try:
                        tmp_frame[arguments[0][0].replace("TF@", "")] = [ord(argument1[0][argument2[0]]), "int"]
                    except IndexError:
                        sys.stderr.write("STRI2INT: ord(char) indexovani mimo retezec")
                        exit(58)
                    except TypeError:
                        sys.stderr.write("STRI2INT: ord(char) char je nevalidni hodnota")
                        exit(58)
                else:
                    sys.stderr.write("STRI2INT: spatne typy operandu")
                    exit(32)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "READ":
        arguments = sort_arguments(index_of_instruction, 2)
        value = ""
        if is_variable_defined(arguments[0]) == True:
            if global_input == None:    # nacitam ze stdin
                if arguments[1][1] == "type" and arguments[1][0] == "int":
                    try:
                        value = [int(input()), "int"]
                    except ValueError:
                        value = [None, "nil"]
                    except EOFError:
                        value = [None, "nil"]
                elif arguments[1][1] == "type" and arguments[1][0] == "string":
                    try:
                        value = [str(input()), "string"]
                    except ValueError:
                        value = [None, "nil"]
                    except EOFError:
                        value = [None, "nil"]
                elif arguments[1][1] == "type" and arguments[1][0] == "bool":
                    try:
                        value = input()
                    except EOFError:
                        value = [None, "nil"]
                    if value.upper() == "TRUE":
                        value = [True, "bool"]
                    else:
                        value = [False, "bool"]
                else:
                    sys.stderr.write("READ: spatne typy operandu")
                    exit(32)  # spatne typy operandu
            else:   # ctu global_input_array[index]
                if input_array_index < len(global_input_string_array):
                    value = global_input_string_array[input_array_index]
                    input_array_index += 1
                    if arguments[1][1] == "type" and arguments[1][0] == "int":
                        try:
                            value = [int(value), "int"]
                        except ValueError:
                            value = [None, "nil"]
                    elif arguments[1][1] == "type" and arguments[1][0] == "string":
                        try:
                            value = [value, "string"]
                        except ValueError:
                            value = [None, "nil"]
                    elif arguments[1][1] == "type" and arguments[1][0] == "bool":
                        if value.upper() == "TRUE":
                            value = [True, "bool"]
                        else:
                            value = [False, "bool"]
                    else:
                        sys.stderr.write("READ: spatne typy operandu")
                        exit(53)  # spatne typy operandu
                else:
                    value = [None, "nil"]
        # ulozeni value do <var>
        if "GF@" in arguments[0][0]:
            global_frame[arguments[0][0].replace("GF@", "")] = value
        elif "LF@" in arguments[0][0]:
            local_frame[-1][arguments[0][0].replace("LF@", "")] = value
        if "TF@" in arguments[0][0]:
            tmp_frame[arguments[0][0].replace("TF@", "")] = value
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "WRITE":   # WRITE <symb> (True="true", False="false"  nil@nil="") print( ,end='')
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 1)
        argument0 = get_val_type_of_argument(arguments[0])
        if argument0[1] == "nil":
            print("", end='')
        elif argument0[1] == "bool":
            if argument0[0] == True:
                print("true", end='')
            elif argument0[0] == False:
                print("false", end='')
        else:
            print(argument0[0], end='')
        # volani nasledujici instrukce
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "CONCAT":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu string
                if argument1[1] == "string" and argument2[1] == "string":
                    global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0] + argument2[0], "string"]
                else:
                    sys.stderr.write("CONCAT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu string
                if argument1[1] == "string" and argument2[1] == "string":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0] + argument2[0], "string"]
                else:
                    sys.stderr.write("CONCAT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu string
                if argument1[1] == "string" and argument2[1] == "string":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0] + argument2[0], "string"]
                else:
                    sys.stderr.write("CONCAT: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "STRLEN":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 2)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu string
                if argument1[1] == "string":
                    global_frame[arguments[0][0].replace("GF@", "")] = [len(argument1[0]), "int"]
                else:
                    sys.stderr.write("STRLEN: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu string
                if argument1[1] == "string":
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [len(argument1[0]), "int"]
                else:
                    sys.stderr.write("STRLEN: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametry jsou typu string
                if argument1[1] == "string":
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [len(argument1[0]), "int"]
                else:
                    sys.stderr.write("STRLEN: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "GETCHAR":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:  # je <var> definovana?
            argument1 = get_val_type_of_argument(arguments[1])
            argument2 = get_val_type_of_argument(arguments[2])
            if "GF@" in arguments[0][0]:
                # kontrola, zda parametr1 je string, parametr2 je int
                if argument1[1] == "string" and argument2[1] == "int":
                    try:
                        global_frame[arguments[0][0].replace("GF@", "")] = [argument1[0][argument2[0]], "string"]
                    except IndexError:
                        sys.stderr.write("GETCHAR: indexovani mimo retezec")
                        exit(58)
                    except TypeError:
                        sys.stderr.write("GETCHAR: char je nevalidni hodnota")
                        exit(58)
                else:
                    sys.stderr.write("GETCHAR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "LF@" in arguments[0][0]:
                # kontrola, zda parametr1 je string, parametr2 je int
                if argument1[1] == "string" and argument2[1] == "int":
                    try:
                        local_frame[-1][arguments[0][0].replace("LF@", "")] = [argument1[0][argument2[0]], "string"]
                    except IndexError:
                        sys.stderr.write("GETCHAR: indexovani mimo retezec")
                        exit(58)
                    except TypeError:
                        sys.stderr.write("GETCHAR: char je nevalidni hodnota")
                        exit(58)
                else:
                    sys.stderr.write("GETCHAR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            elif "TF@" in arguments[0][0]:
                # kontrola, zda parametr1 je string, parametr2 je int
                if argument1[1] == "string" and argument2[1] == "int":
                    try:
                        tmp_frame[arguments[0][0].replace("TF@", "")] = [argument1[0][argument2[0]], "string"]
                    except IndexError:
                        sys.stderr.write("GETCHAR: indexovani mimo retezec")
                        exit(58)
                    except TypeError:
                        sys.stderr.write("GETCHAR: char je nevalidni hodnota")
                        exit(58)
                else:
                    sys.stderr.write("GETCHAR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "SETCHAR":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        argument1 = get_val_type_of_argument(arguments[1])
        argument2 = get_val_type_of_argument(arguments[2])
        if is_variable_defined(arguments[0]) == True:
            # <symb1> celociselny int od 0, <symb2> je string
            if argument1[1] == "int" and argument2[1] == "string":
                if "GF@" in arguments[0][0] and global_frame[arguments[0][0].replace("GF@", "")][1] == "string":
                    try:
                        # budu si muset vytahnout hodnotu <var> udelat z ni list() pak join a ulozit z5
                        var_string = global_frame[arguments[0][0].replace("GF@", "")][0]
                        var_string = list(var_string)
                        var_string[argument1[0]] = argument2[0][0]
                        var_string = ''.join(var_string)
                        global_frame[arguments[0][0].replace("GF@", "")][0] = var_string
                    except IndexError:
                        sys.stderr.write("SETCHAR: indexace mimo retezec, nebo prazdny <symb2>")
                        exit(58)  # spatne typy operandu
                elif "LF@" in arguments[0][0] and local_frame[-1][arguments[0][0].replace("LF@", "")][1] == "string":
                    try:
                        # budu si muset vytahnout hodnotu <var> udelat z ni list() pak join a ulozit z5
                        var_string = local_frame[-1][arguments[0][0].replace("LF@", "")][0]
                        var_string = list(var_string)
                        var_string[argument1[0]] = argument2[0][0]
                        var_string = ''.join(var_string)
                        local_frame[-1][arguments[0][0].replace("LF@", "")][0] = var_string
                    except IndexError:
                        sys.stderr.write("SETCHAR: indexace mimo retezec, nebo prazdny <symb2>")
                        exit(58)  # spatne typy operandu
                elif "TF@" in arguments[0][0] and tmp_frame[arguments[0][0].replace("TF@", "")][1] == "string":
                    try:
                        # budu si muset vytahnout hodnotu <var> udelat z ni list() pak join a ulozit z5
                        var_string = tmp_frame[arguments[0][0].replace("TF@", "")][0]
                        var_string = list(var_string)
                        var_string[argument1[0]] = argument2[0][0]
                        var_string = ''.join(var_string)
                        tmp_frame[arguments[0][0].replace("TF@", "")][0] = var_string
                    except IndexError:
                        sys.stderr.write("SETCHAR: indexace mimo retezec, nebo prazdny <symb2>")
                        exit(58)  # spatne typy operandu
                else:
                    sys.stderr.write("SETCHAR: spatne typy operandu")
                    exit(53)  # spatne typy operandu
            else:
                sys.stderr.write("SETCHAR: spatne typy operandu")
                exit(53)  # spatne typy operandu
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "TYPE":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 2)  # nacteni argumentu instrukce
        if is_variable_defined(arguments[0]) == True:
            if "GF@" in arguments[0][0]:
                type_of_symb = get_type_of_argument(arguments[1])
                if type_of_symb is None:    # neinicializovana promenna -> hodnota <var> bude prazdny retezec
                    global_frame[arguments[0][0].replace("GF@", "")] = ["", "string"]
                else:
                    global_frame[arguments[0][0].replace("GF@", "")] = [type_of_symb, "string"]
            elif "LF@" in arguments[0][0]:
                type_of_symb = get_type_of_argument(arguments[1])
                if type_of_symb is None:  # neinicializovana promenna -> hodnota <var> bude prazdny retezec
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = ["", "string"]
                else:
                    local_frame[-1][arguments[0][0].replace("LF@", "")] = [type_of_symb, "string"]
            elif "TF@" in arguments[0][0]:
                type_of_symb = get_type_of_argument(arguments[1])
                if type_of_symb is None:  # neinicializovana promenna -> hodnota <var> bude prazdny retezec
                    tmp_frame[arguments[0][0].replace("TF@", "")] = ["", "string"]
                else:
                    tmp_frame[arguments[0][0].replace("TF@", "")] = [type_of_symb, "string"]
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "LABEL":
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "JUMP":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 1)  # nacteni argumentu instrukce
        if arguments[0][1] != "label":
            sys.stderr.write("JUMP: type neni label")
            exit(53)
        if arguments[0][0] in global_label_dictionary:
            # presun na pozici navesti <label> arguments[0][0]
            #run(instruction_dict[global_label_dictionary[arguments[0][0]]])
            return global_label_dictionary[arguments[0][0]]
        else:
            sys.stderr.write("JUMP: pokus o skok na neexistujici navesti")
            exit(52)
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "JUMPIFEQ":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if arguments[0][1] != "label":
            sys.stderr.write("JUMPIFEQ: type neni label")
            exit(53)
        argument1 = get_val_type_of_argument(arguments[1])
        argument2 = get_val_type_of_argument(arguments[2])
        if argument1[1] == "nil" or argument2[1] == "nil":
            if argument1[0] == argument2[0]:    # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    #run(instruction_dict[global_label_dictionary[arguments[0][0]]])
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQ: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "int" and argument2[1] == "int":
            if argument1[0] == argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQ: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "string" and argument2[1] == "string":
            if argument1[0] == argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQ: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "bool" and argument2[1] == "bool":
            if argument1[0] == argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQ: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        else:
            sys.stderr.write("JUMPIFEQ: spatne typy operandu")
            exit(53)
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "JUMPIFNEQ":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 3)  # nacteni argumentu instrukce
        if arguments[0][1] != "label":
            sys.stderr.write("JUMPIFNEQ: type neni label")
            exit(53)
        argument1 = get_val_type_of_argument(arguments[1])
        argument2 = get_val_type_of_argument(arguments[2])
        if argument1[1] == "nil" or argument2[1] == "nil":
            if argument1[0] != argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQ: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "int" and argument2[1] == "int":
            if argument1[0] != argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQ: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "string" and argument2[1] == "string":
            if argument1[0] != argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQ: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "bool" and argument2[1] == "bool":
            if argument1[0] != argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQ: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        else:
            sys.stderr.write("JUMPIFEQ: spatne typy operandu")
            exit(53)
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ------------------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "EXIT":    # EXIT <symb> cele cislo 0-49 vcetne, nevalidni celoc. hodnota -> chyba 57
        arguments = sort_arguments(index_of_instruction, 1)
        argument0 = get_val_type_of_argument(arguments[0])
        if argument0[1] != "int":   # typ neni int
            sys.stderr.write("EXIT - spatny typ <symb>, muze byt jen celociselny 0-49")
            exit(53)  # spatne typy operandu
        else:   # vse ok , jen se jeste nekontrolovala hodnota .text aka arguments[0][0]
                if argument0[0] < 0 or argument0[0] > 49:  # je to int (overeni rozsahu 0-49)
                    sys.stderr.write("EXIT - spatna hodnota operandu <symb> muze byt jen 0-49")
                    exit(57)  # spatna hodnota operandu
                else:
                    # ukonceni programu s navratovym kodem
                    exit(argument0[0])
    # ------------------------------------------------------------------------------------------------------------

    # DONE
    # ------------------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "DPRINT":  # neimplementovano, pouze preskoci na dalsi instrukci
        sort_arguments(index_of_instruction, 1)     # test, ze ma argument <symb>
        # presun na dalsi instrukci
        return True
    # ------------------------------------------------------------------------------------------------------------

    # DONE
    # ------------------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "BREAK":   # neimplementovano, pouze preskoci na dalsi instrukci
        sort_arguments(index_of_instruction, 0)  # test, ze nema argumenty
        # presun na dalsi instrukci
        return True
    # ------------------------------------------------------------------------------------------------------------

    # DONE rev
    # ------------------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "CLEARS":  # rozsireni STACK
        # provedeni instrukce
        sort_arguments(index_of_instruction, 0)  # test, ze nema argumenty
        data_stack = []     # smaze obsah datoveho zasobniku
        # presun na dalsi instrukci
        return True
    # ------------------------------------------------------------------------------------------------------------

    # DONE rev
    # ------------------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "ADDS":
        # provedeni instrukce
        sort_arguments(index_of_instruction, 0)  # test, ze nema argumenty
        if len(data_stack) >= 2:    # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("ADDS: pokus o cteni z prazdneho datoveho zasobniku")
        # kontrola, zda parametry jsou typu int
        if argument1[1] == "int" and argument2[1] == "int":
            data_stack.append([argument1[0] + argument2[0], "int"])
        else:
            sys.stderr.write("ADDS: spatne typy operandu")
            exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ------------------------------------------------------------------------------------------------------------

    # DONE rev
    # ------------------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "SUBS":  # rozsireni STACK
        # provedeni instrukce
        sort_arguments(index_of_instruction, 0)  # test, ze nema argumenty
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("SUBS: pokus o cteni z prazdneho datoveho zasobniku")
        # kontrola, zda parametry jsou typu int
        if argument1[1] == "int" and argument2[1] == "int":
            data_stack.append([argument1[0] - argument2[0], "int"])
        else:
            sys.stderr.write("SUBS: spatne typy operandu")
            exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ------------------------------------------------------------------------------------------------------------

    # DONE rev
    # ------------------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "MULS":  # rozsireni STACK
        # provedeni instrukce
        sort_arguments(index_of_instruction, 0)  # test, ze nema argumenty
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("MULS: pokus o cteni z prazdneho datoveho zasobniku")
        # kontrola, zda parametry jsou typu int
        if argument1[1] == "int" and argument2[1] == "int":
            data_stack.append([argument1[0] * argument2[0], "int"])
        else:
            sys.stderr.write("MULS: spatne typy operandu")
            exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ------------------------------------------------------------------------------------------------------------

    # DONE
    # ------------------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "IDIVS":  # rozsireni STACK
        # provedeni instrukce
        sort_arguments(index_of_instruction, 0)  # test, ze nema argumenty
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("IDIVS: pokus o cteni z prazdneho datoveho zasobniku")
        # kontrola, zda parametry jsou typu int
        if argument1[1] == "int" and argument2[1] == "int":
            if argument2[0] != 0:
                data_stack.append([argument1[0] // argument2[0], "int"])
            else:
                sys.stderr.write("IDIVS: deleni 0")
                exit(57)
        else:
            sys.stderr.write("IDIVS: spatne typy operandu")
            exit(53)  # spatne typy operandu
        # presun na dalsi instrukci
        return True
    # ------------------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "LTS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("LTS: pokus o cteni z prazdneho datoveho zasobniku")
        if argument1[1] == "int" and argument2[1] == "int":
            data_stack.append([argument1[0] < argument2[0], "bool"])
        elif argument1[1] == "string" and argument2[1] == "string":
            data_stack.append([argument1[0] < argument2[0], "bool"])
        elif argument1[1] == "bool" and argument2[1] == "bool":
            data_stack.append([argument1[0] < argument2[0], "bool"])
        else:
            sys.stderr.write("LTS: spatne typy operandu")
            exit(53)
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "GTS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("GTS: pokus o cteni z prazdneho datoveho zasobniku")
        if argument1[1] == "int" and argument2[1] == "int":
            data_stack.append([argument1[0] > argument2[0], "bool"])
        elif argument1[1] == "string" and argument2[1] == "string":
            data_stack.append([argument1[0] > argument2[0], "bool"])
        elif argument1[1] == "bool" and argument2[1] == "bool":
            data_stack.append([argument1[0] > argument2[0], "bool"])
        else:
            sys.stderr.write("GTS: spatne typy operandu")
            exit(53)
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "EQS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("EQS: pokus o cteni z prazdneho datoveho zasobniku")
        if argument1[1] == "nil" or argument2[1] == "nil":
            data_stack.append([argument1[0] == argument2[0], "bool"])
        elif argument1[1] == "int" and argument2[1] == "int":
            data_stack.append([argument1[0] == argument2[0], "bool"])
        elif argument1[1] == "string" and argument2[1] == "string":
            data_stack.append([argument1[0] == argument2[0], "bool"])
        elif argument1[1] == "bool" and argument2[1] == "bool":
            data_stack.append([argument1[0] == argument2[0], "bool"])
        else:
            sys.stderr.write("EQS: spatne typy operandu")
            exit(53)
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "ANDS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("ANDS: pokus o cteni z prazdneho datoveho zasobniku")
        if argument1[1] == "bool" and argument2[1] == "bool":
            data_stack.append([argument1[0] and argument2[0], "bool"])
        else:
            sys.stderr.write("ANDS: spatne typy operandu")
            exit(53)
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "ORS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("ORS: pokus o cteni z prazdneho datoveho zasobniku")
        if argument1[1] == "bool" and argument2[1] == "bool":
            data_stack.append([argument1[0] or argument2[0], "bool"])
        else:
            sys.stderr.write("ORS: spatne typy operandu")
            exit(53)
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "NOTS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if len(data_stack) >= 1:  # kontrola, ze datovy zasobnik neni prazdny
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("NOTS: pokus o cteni z prazdneho datoveho zasobniku")
        if argument1[1] == "bool":
            data_stack.append([not argument1[0], "bool"])
        else:
            sys.stderr.write("NOTS: spatne typy operandu")
            exit(53)
        # prechod na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------


    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "INT2CHARS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if len(data_stack) >= 1:  # kontrola, ze datovy zasobnik neni prazdny
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("INT2CHARS: pokus o cteni z prazdneho datoveho zasobniku")
        if argument1[1] == "int":
            try:
                data_stack.append([chr(argument1[0]), "string"])
            except ValueError:
                sys.stderr.write("INT2CHARS: chr(int) nevalidni ordinalni hodnota")
                exit(58)
        else:
            sys.stderr.write("INT2CHARS: spatne typy operandu")
            exit(53)
        # presun na dalsi instrukci
        return True
    # ----------------------------------------------------------------------------------------------------

    elif attributes["opcode"].upper() == "STRI2INTS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 0)  # nacteni argumentu instrukce
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("STRI2INTS: pokus o cteni z prazdneho datoveho zasobniku")
        # kontrola, zda parametr1 je string, parametr2 je int
        if argument1[1] == "string" and argument2[1] == "int":
            try:
                data_stack.append([ord(argument1[0][argument2[0]]), "int"])
            except IndexError:
                sys.stderr.write("STRI2INTS: ord(char) indexovani mimo retezec")
                exit(58)
            except TypeError:
                sys.stderr.write("STRI2INTS: ord(char) char je nevalidni hodnota")
                exit(58)
        else:
            sys.stderr.write("STRI2INTS: spatne typy operandu")
            exit(32)  # spatne typy operandu
        # presun na dalsi instrukci
        return True

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "JUMPIFEQS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 1)  # nacteni argumentu instrukce
        if arguments[0][1] != "label":
            sys.stderr.write("JUMPIFEQS: type neni label")
            exit(53)
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("JUMPIFEQS: pokus o cteni z prazdneho datoveho zasobniku")
        if argument1[1] == "nil" or argument2[1] == "nil":
            if argument1[0] == argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    # run(instruction_dict[global_label_dictionary[arguments[0][0]]])
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQS: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "int" and argument2[1] == "int":
            if argument1[0] == argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQS: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "string" and argument2[1] == "string":
            if argument1[0] == argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQS: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "bool" and argument2[1] == "bool":
            if argument1[0] == argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFEQS: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        else:
            sys.stderr.write("JUMPIFEQS: spatne typy operandu")
            exit(53)
    # ----------------------------------------------------------------------------------------------------

    # DONE
    # ----------------------------------------------------------------------------------------------------
    elif attributes["opcode"].upper() == "JUMPIFNEQS":
        # provedeni instrukce
        arguments = sort_arguments(index_of_instruction, 1)  # nacteni argumentu instrukce
        if arguments[0][1] != "label":
            sys.stderr.write("JUMPIFNEQS: type neni label")
            exit(53)
        if len(data_stack) >= 2:  # kontrola, ze datovy zasobnik neni prazdny
            argument2 = data_stack.pop()
            argument1 = data_stack.pop()
        else:
            exit(56)
            sys.stderr.write("JUMPIFNEQS: pokus o cteni z prazdneho datoveho zasobniku")
        if argument1[1] == "nil" or argument2[1] == "nil":
            if argument1[0] != argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    # run(instruction_dict[global_label_dictionary[arguments[0][0]]])
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFNEQS: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "int" and argument2[1] == "int":
            if argument1[0] != argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFNEQS: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "string" and argument2[1] == "string":
            if argument1[0] != argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFNEQS: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        elif argument1[1] == "bool" and argument2[1] == "bool":
            if argument1[0] != argument2[0]:  # plati podminka
                # skaceme
                if arguments[0][0] in global_label_dictionary:
                    # presun na pozici navesti <label> arguments[0][0]
                    return global_label_dictionary[arguments[0][0]]
                else:
                    sys.stderr.write("JUMPIFNEQS: pokus o skok na neexistujici navesti")
                    exit(52)
            else:
                # pokracuj dalsi instrukci
                return True
        else:
            sys.stderr.write("JUMPIFNEQS: spatne typy operandu")
            exit(53)
    # ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------

start_program()     # spusti provadeni instrukci
