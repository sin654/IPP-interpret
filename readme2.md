## Implementační dokumentace k 2. úloze do IPP 2019/2020
Jméno a příjmení: Jan Doležel
Login: xdolez81

## interpret.py

Návrh a implementaci interpretu jsem rozdělil na dvě hlavní části. Účelem první části je zpracovat argumenty příkazové řádky, zkontrolovat vstupní soubory, načíst vstupy a dále zpracovat XML soubor do struktury se kterou se bude poté dobře pracovat. Na načtení a zpracování XML souboru jsem použil knihovnu standartní knihovnu Pythonu `xml`. Pro účel organizace dat z xml souboru jsem implementoval několik funkcí: 

`make_label_dictionary()` - tato funkce projde xml data a vyhledá si v ní instrukce "label"
`make_instruction_dictionary()` - Tato funkce mapuje "order" instrukce na její index ve stromové reprezentaci xml souboru.
`make_sorted_instruction_order()` - Tato pomocná funkce uspořádá hodnoty "order" instrukce, aby se vykompenzovalo jejich možné přeházení a bylo s němi poté možné vzestupně pracovat. 
`sort_arguments()` - Tato funkce zkontroluje pořadí, počet argumentů instrukce a uspořádá je do pole, ve kterém už budou za sebou následovat ve správném pořadí.

Druhou částí programu jsou již funkce potřebné k samotnému vykonávání instrukcí. 
`run()` - Hlavní funkce, jejíž součástí je samotná implementace instrukce. Samotné instrukce mají velmi podobnou implementaci. Začne se načtením argumentů instrukce, poté se zkontrolují  operandy a proměnná do které se má výsledek instrukce uložit. Nakonec se provede operace příslušná instrukci.
`start_program()` - Pomocná funkce která na základě návratové hodnoty funkce `run()` volí následující instrukci k provedení (další/skok)
`is_variable_defined()` - funkce na kontrolu proměnné, do které se má ukládat výsledek provedení instrukce
`get_val_type_of_argument()` - tato funkce zjistí datový typ a hodnotu argumentu instrukce a to jak konstanty, tak i proměnné
`get_type_of_argument()` - zjistí datový typ argumentu instrukce

### Doplňující informace k implementaci interpret.py
Globální a dočasný rámec je realizován obyčejným slovníkem. Lokální rámec tvoří pole slovníků. 
Jakákoliv zásobníková struktura je realizována obyčejným polem a operace `push` je nahrazena metodou `.append()`.
Argumenty příkazové řádky jsou zpracovaný "ručně". Nebyla využita knihovna.
Při implementaci jsem využil knihovny `xml`(na práci s xml souborem) `sys`(chybové výpisy, přístup k argumentům přikazové řádky) a `re` (pro kontrolu jmen a textových řetězců regulárním výrazem)

### Rozšíření
Implementoval jsem rozšíření STACK, kde se argumenty instrukce získávají ze zásobníku a výsledek se ukládá na zásobník.
