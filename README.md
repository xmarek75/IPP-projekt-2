# IPP - 2.cast

Navrh, implementace a dokumentace interpretu pro IPPcode22
 
# Autor
Pavel Marek
* login: xmarek75
* email: xmarek75@vutbr.cz


### Implementace

Skript byl implmentovan v jazyce python
Pro implementaci bylo nutne vyuzit nekolik knihoven:


* from audioop import add
* from curses.ascii import ETB
* import re
* from sys import stderr
* from sys import stdin
* import sys
* import argparse
* import xml.etree.ElementTree as ET

Dale byly pro jednoduzsi implementaci implementovany tridy:

* trida <strong>argument</strong> 
    s argumenty: 
    ``` 
    arg_type
    value
    ```

* trida <strong>instruction</strong> 
    s argumenty:
    ``` 
    name
    number
    ```
    

* trida <strong>variable</strong> 
    s argumenty:
    ``` 
    varType
    value
    ```
## Reseni
<ol>
<li>Nacteni souboru ze stdin</li>
<li>Parsing XML souboru</li>
pomoci knihovny <italic>xml.etree.ElmentTree</italic>
<li>Iterace pres XML elementy</li>
ktere se ukladaji do <italic>instructions</italic>
<li>Pomoci dlouheho seznamu if instrukci se spousteji prislusne funkce </li>
<li>Vsechny casti jsou prubezne kontrolovnay</li>
</ol>

## Spousteni skriptu

* Pro spusteni skriptu postupujte nasledovne:

    ```
    $ python3 interpret.py --source= "YourSourceFile"
    ```
* Pro spusteni napovedy postupujte nasledovne:

    ```
    $ python3 interpret.py --help
    ```


## Dulezite pomocne funkce
Pro zjednoduseni implemenatce byla implementovanam rada pomocnych funkci,
z nichz nejdulezitejsi byly:

> checkVarExistence(frame, varname)
* kde frame znaci ramec promenne a name je nazev promenne
* funkce zkontroluje jestli existuje zadana promenna, pokud nebyla tak ukonci program s odpovidajici chybovym kodem

> getVariable(frame, name)
* kde frame znaci ramec promenne a name je nazev promenne
* funkce vyhleda prislusnou promennou a vrati jeji strukturu 

> saveToVariable(frame, name, variable)
* kde frame a name ma stejny vyznam jako u getVariable a variable je nazev dalsi promenne 
* funkce ulozi hodnoty z variable do promenne s nazvem name a s prislusnym ramcem frame

## Volani jednotlivych instrukci

Volani jednotlivych instrukci je reseno pomoci nekolika instrukci if, ktere nasledne ulozi argumenty instrukce do promennych a zavolaji prislusnou funkci 
