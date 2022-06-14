#   Project Name: IPP - 2.cast 
#   File Name: interpret.py
#   login: xmarek75
#   Author: Pavel Marek
#   Last Edit: 20.04.2022 0:38

from audioop import add
from curses.ascii import ETB
import re
from sys import stderr
from sys import stdin
import sys
import argparse
import xml.etree.ElementTree as ET

from pyparsing import And


class argument:
    def __init__(self,arg_type,value):
        self.type = arg_type
        self.value = value
    

class instruction:
    def __init__(self,name,number):
        self.name = name
        self.number = number
        self.args = []
    def add_argument(self,arg_type,value):
        self.args.append(argument(arg_type,value))

class Variable:
    def __init__(self, varType, value):
        self.type = varType
        self.value = value

instructions=list()
labels = dict() #todo
positionInProgram = 0
GF = dict()
TF = None
LFs = list()
calls = list()

################################################################################

def checkVarExistence(frame, name):
    if frame == "GF":
        if not(name in GF.keys()):
            print(GF.keys())
            stderr.write("Non super existing variable\n")
            exit(54)
    elif frame == "TF":
        if TF == None:
            stderr.write("TF not initialized\n")
            exit(55)

        if not(name in TF.keys()):
            stderr.write("Non existing variable\n")
            exit(54)
    elif frame == "LF":
        if len(LFs) == 0:
            stderr.write("No frame in LF stack\n")
            exit(55)

        if not(name in LFs[len(LFs)-1].keys()):
            stderr.write("Non existing variable\n")
            exit(54)
    else:
        stderr.write("Not supported frame passed\n")
        exit(99)
        
def getVariable(frame, name):
    global TF
    global LFs
    if frame == "GF":
        if not name in GF.keys():
            stderr.write("Non existing variable, exiting...")
            exit(54)
        return GF[name]
    elif frame == "TF":
        if TF == None:
            stderr.write("TF not initialized, exiting...\n")
            exit(55)
        if not name in TF.keys():
            stderr.write("Non existing variable, exiting...")
            exit(54)
        return TF[name]
    elif frame == "LF":
        if len(LFs) == 0:
            stderr.write("No frame in LF stack, exiting...\n")
            exit(55)
        if not name in LFs[len(LFs)-1].keys():
            stderr.write("Non existing variable, exiting...")
            exit(54)
        return LFs[len(LFs)-1][name]     
    
def saveToVariable(frame, name, arg):
    if re.match(r"(int|bool|string|nil)", arg.type): ###pokoud nefunguji nejaky testy zakomentovat tento radek
        if frame == "GF":
            GF[name] = Variable(arg.type, arg.value)
        elif frame == "TF":
            if TF == None:
                stderr.write("TF not initialized, exiting...\n")
                exit(55)
            TF[name] = Variable(arg.type, arg.value)
        elif frame == "LF":
            if len(LFs) == 0:
                stderr.write("No frame in LF stack, exiting...\n")
                exit(55)
            LFs[len(LFs)-1][name] = Variable(arg.type, arg.value)
        else:
            stderr.write("Unsupported frame passed, exiting...\n")
            exit(55)
    elif arg.type == 'var': ###########-------------------->>>check later
        tmp = arg.value.split("@")
        checkVarExistence(tmp[0], tmp[1])
        hold = getVariable(tmp[0],tmp[1])
        if frame == "GF":
            GF[name] = Variable(hold.type, hold.value)
        elif frame == "TF":
            if TF == None:
                stderr.write("TF not initialized, exiting...\n")
                exit(55)
            TF[name] = Variable(hold.type, hold.value)
        elif frame == "LF":
            if len(LFs) == 0:
                stderr.write("No frame in LF stack, exiting...\n")
                exit(55)
            LFs[len(LFs)-1][name] = Variable(hold.type, hold.value)
        else:
            stderr.write("Unsupported frame passed, exiting...\n")
            exit(55)

    else:
        stderr.write("Unexpected error when saving to variable, exiting...\n")
        exit(99)
        
def insDEFVAR(var):
    splitted = var.value.split("@")    
    tmp = Variable(None, None)
    if splitted[0] == "GF":
        if splitted[1] in GF.keys():
            stderr.write("Variable already exists, exiting...\n")
            exit(52)
        else:
            GF.update({splitted[1]: tmp})
    elif splitted[0] == "TF":
        if TF == None:
            stderr.write("TF not initialized, exiting...\n")
            exit(52)

        if splitted[1] in TF.keys():
            stderr.write("Variable already exists, exiting...\n")
            exit(52)
        TF.update({splitted[1]: tmp})
    elif splitted[0] == "LF":
        if LFs.count == 0:
            stderr.write("No LF in stack, exiting...\n")
            exit(52)

        if splitted[1] in LFs[len(LFs)-1].keys():
            stderr.write("Variable already exists, exiting...\n")
            exit(52)
        LFs[len(LFs)-1].update({splitted[1]: tmp})
        
def insMOVE(var, symb):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    saveToVariable(splittedVar[0], splittedVar[1], symb)
    
def insWRITE(symb):
    
    if symb.type =='nil':
        print("",end='')
    if symb.type == 'var':
        splitted = symb.value.split("@")
        tmp = getVariable(splitted[0],splitted[1])
        if tmp.value == 'true' or tmp.value == True:
            print("true")
        elif tmp.value == 'false' or tmp.value == False:
            print("false")
        elif tmp.value != None:
            print(tmp.value)
        else:
            print("",end='')
    
    else:
        tmp = re.split(r"\\", symb.value)
        newString = ""
        for x in range(0, len(tmp)):
            if (x == 0):
                newString += tmp[x]
            elif len(tmp[x]) > 3:
                newString += chr(int(tmp[x][:3]))
                newString += tmp[x][3:]
            else:
                newString += chr(int(tmp[x]))
            print(newString, end=''+"\n")
            
def insADD(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb2.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2=tmp_y.value
    else:
        tmp2 = symb2.value
        
    value = argument('int',int(tmp1) + int(tmp2))
    splittedVar = var.value.split("@")
    #print (value)
    tmp3 = var
    tmp3.value = value
    saveToVariable(splittedVar[0], splittedVar[1], value)

def insSUB(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb2.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2=tmp_y.value
    else:
        tmp2 = symb2.value
        
    value = argument('int',int(tmp1) - int(tmp2))
    splittedVar = var.value.split("@")
    #print (value)
    tmp3 = var
    tmp3.value = value
    saveToVariable(splittedVar[0], splittedVar[1], value)

def insMUL(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb2.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2=tmp_y.value
    else:
        tmp2 = symb2.value
        
    value = argument('int',int(tmp1) * int(tmp2))
    splittedVar = var.value.split("@")
    #print (value)
    tmp3 = var
    tmp3.value = value
    saveToVariable(splittedVar[0], splittedVar[1], value)

def insIDIV(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb2.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2=tmp_y.value
    else:
        tmp2 = symb2.value
    if tmp2 == '0':
        stderr.write("ERROR: division by zero\n")
        exit(57)
    value = argument('int',int(tmp1) / int(tmp2))
    splittedVar = var.value.split("@")
    #print (value)
    tmp3 = var
    tmp3.value = value
    saveToVariable(splittedVar[0], splittedVar[1], value)

def insLT(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb2.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2=tmp_y.value
    else:
        tmp2 = symb2.value
        
    value = argument('bool',int(tmp1) < int(tmp2))
    splittedVar = var.value.split("@")
    saveToVariable(splittedVar[0], splittedVar[1], value)

def insGT(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb2.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2=tmp_y.value
    else:
        tmp2 = symb2.value
        
    value = argument('bool',int(tmp1) > int(tmp2))
    splittedVar = var.value.split("@")
    saveToVariable(splittedVar[0], splittedVar[1], value)

def insEQ(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb2.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2=tmp_y.value
    else:
        tmp2 = symb2.value
        
    value = argument('bool',int(tmp1) == int(tmp2))
    splittedVar = var.value.split("@")
    saveToVariable(splittedVar[0], splittedVar[1], value)

def insAND(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb2.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2=tmp_y.value
    else:
        tmp2 = symb2.value
    if tmp1 == 'true' and tmp2 =='true':
        value = argument('bool', bool(True))
    else:
        value = argument('bool', bool(False))
        
    splittedVar = var.value.split("@")
    saveToVariable(splittedVar[0], splittedVar[1], value)
    
def insOR(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb2.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2=tmp_y.value
    else:
        tmp2 = symb2.value
    if tmp1 == 'true' or tmp2 =='true':
        value = argument('bool', bool(True))
    else:
        value = argument('bool', bool(False))
        
    splittedVar = var.value.split("@")
    saveToVariable(splittedVar[0], splittedVar[1], value)

def insNOT(var,symb1):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value

    if tmp1 == 'true':
        value = argument('bool', bool(False))
    else:
        value = argument('bool', bool(True))
        
    splittedVar = var.value.split("@")
    saveToVariable(splittedVar[0], splittedVar[1], value)

def insINT2CHAR(var, symb1):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    if int(symb1.value) >= 33 and int(symb1.value) <= 126:
        tmp = argument('string',chr(int(symb1.value))) 
    else:
        stderr.write("cant be converted to single character ")
        exit(58)
    saveToVariable(splittedVar[0], splittedVar[1], tmp)
    
def insSTRI2INT(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
    if symb2.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
    if int(symb2.value) > len(symb1.value)-1:
        stderr.write("string index out of range")
        exit(58)
    else:
        if symb2.value.isnumeric():
            tmp1 = argument("int", ord(symb1.value[int(symb2.value)]))
        else:
            stderr.write("third argument must be int\n")
            exit(53)
    saveToVariable(splittedVar[0], splittedVar[1], tmp1)

def insREAD(var,rtype):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    tmp1 = input()
    if rtype.value == 'bool':
        tmp_upper = tmp1.upper()
        if tmp_upper != "FALSE" and tmp_upper != "TRUE":
            tmp1 = None
            tmp2 = argument("nil",'nil')
        else:
            if tmp1.upper() == "TRUE":
                tmp2 = argument("bool",bool(True))
            else:
                tmp2 = argument("bool",bool(False))
    elif rtype.value == "int":
        if not tmp1.isnumeric():
            tmp1 = None
            tmp2 = argument("nil",'nil')
        else:
            tmp2 = argument("int",tmp1)
    elif rtype.value == 'string':
        if tmp1 != None:
            tmp2 = argument("string",tmp1)
        else:
            tmp2 = argument("nil",'nil')
    else:
        stderr.write("wrong type")
        exit(53)
    saveToVariable(splittedVar[0], splittedVar[1], tmp2)  
            
def insCONCAT(var,symb1,symb2):     
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if symb2.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_y = getVariable(splitted[0],splitted[1])
        tmp2 = tmp_x.value
    else:
        tmp2 = symb2.value
    tmp3 = argument("string",tmp1+tmp2)
    saveToVariable(splittedVar[0], splittedVar[1], tmp3)  
    
def insSTRLEN(var,symb1):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp_x = getVariable(splitted[0],splitted[1])
        tmp1 = tmp_x.value
    else:
        tmp1 = symb1.value
    if tmp1==None:
        tmp2 = '0'
    else:
        tmp2 = len(tmp1)
    tmp3 = argument("int", tmp2)
    saveToVariable(splittedVar[0], splittedVar[1], tmp3)  
    
def insGETCHAR(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
    if symb2.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
    if int(symb2.value) > len(symb1.value)-1:
        stderr.write("string index out of range")
        exit(58)
    else:
        if symb2.value.isnumeric():
            tmp1 = argument("string", symb1.value[int(symb2.value)])
        else:
            stderr.write("third argument must be int\n")
            exit(53)
    saveToVariable(splittedVar[0], splittedVar[1], tmp1)

def insSETCHAR(var,symb1,symb2):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
    if symb2.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
    if int(symb1.value) > len(var.value)-1:
        stderr.write("string index out of range")
        exit(58)
    else:
        if symb1.value.isnumeric():
            splitted = var.value.split("@")
            tmp_x = getVariable(splitted[0],splitted[1])
            tmp1 = tmp_x.value
            tmp1 = tmp1[0:int(symb1.value)] + symb2.value + tmp1[int(symb1.value)+1:] 
            tmp3 = argument("string", tmp1)
        else:
            stderr.write("second argument must be int\n")
            exit(53)
    saveToVariable(splittedVar[0], splittedVar[1], tmp3)
def insTYPE(var,symb1):
    splittedVar = var.value.split("@")
    checkVarExistence(splittedVar[0], splittedVar[1])
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp1 = getVariable(splitted[0],splitted[1])
        tmp2 = tmp1.type
    else:
        tmp2 = symb1.type
    tmp3 = argument("string",tmp2)
    saveToVariable(splittedVar[0], splittedVar[1], tmp3)
def insDPRINT(symb1):
    stderr.write(symb1.value)
def insBreak():
    position = str(positionInProgram+1)
    stderr.write("order number in program:")
    stderr.write(position)
def insEXIT(symb1):
    if symb1.type == "var":
        splitted = symb1.value.split("@")
        checkVarExistence(splitted[0], splitted[1])
        tmp1 = getVariable(splitted[0],splitted[1])
        tmp2 = tmp1.value
    else:
        tmp2 = symb1.value
    if int(tmp2) >= 0 and int(tmp2) <= 49:
        exit(tmp2)
    else:
        stderr.write("exit with 57")
        exit(57)
        
def insCREATEFRAME():
    global TF
    TF = dict()

def insPUSHFRAME():
    global TF
    global LF
    LF.append(TF)
    TF = None

def insPOPFRAME():
    global TF
    global LF
    TF = LF.pop()        


################################################################################
def interpretInstruction(inst):
    global positionInProgram
    global TF
    global LFs
    if inst.name == "MOVE":
        var = inst.args[0]
        symb = inst.args[1]
        insMOVE(var, symb)
    elif inst.name == "WRITE":
        symb = inst.args[0]
        insWRITE(symb)
    elif inst.name == "DEFVAR":
        var = inst.args[0]
        insDEFVAR(var)
    elif inst.name =="ADD":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insADD(var,symb1,symb2)
    elif inst.name =="SUB":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insSUB(var,symb1,symb2)
    elif inst.name =="MUL":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insMUL(var,symb1,symb2)
    elif inst.name =="IDIV":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insIDIV(var,symb1,symb2)
    elif inst.name =="LT":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insLT(var,symb1,symb2)
    elif inst.name =="GT":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insGT(var,symb1,symb2)
    elif inst.name =="EQ":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insEQ(var,symb1,symb2)
    elif inst.name =="AND":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insAND(var,symb1,symb2)
    elif inst.name =="OR":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insOR(var,symb1,symb2)
    elif inst.name =="NOT":
        var = inst.args[0]
        symb1 = inst.args[1]
        insNOT(var,symb1)
    elif inst.name =="INT2CHAR":
        var = inst.args[0]
        symb1 = inst.args[1]
        insINT2CHAR(var,symb1)
    elif inst.name =="STRI2INT":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insSTRI2INT(var,symb1,symb2)
    elif inst.name =="READ":
        var = inst.args[0]
        rtype = inst.args[1]
        insREAD(var,rtype)
    elif inst.name =="CONCAT":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insCONCAT(var,symb1,symb2)
    elif inst.name =="STRLEN":
        var = inst.args[0]
        symb1 = inst.args[1]
        insSTRLEN(var,symb1)
    elif inst.name =="GETCHAR":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insGETCHAR(var,symb1,symb2)
    elif inst.name =="SETCHAR":
        var = inst.args[0]
        symb1 = inst.args[1]
        symb2 = inst.args[2]
        insSETCHAR(var,symb1,symb2)
    elif inst.name =="TYPE":
        var = inst.args[0]
        symb1 = inst.args[1]
        insTYPE(var,symb1)
    elif inst.name =="DPRINT":
        symb1 = inst.args[0]
        insDPRINT(symb1)
    elif inst.name =="BREAK":
        insBreak()
    elif inst.name =="EXIT":
        symb1 = inst.args[0]
        insEXIT(symb1)
    elif inst.name =="CREATEFRAME":
        insCREATEFRAME()
    elif inst.name =="PUSHFRAME":
        insPUSHFRAME()
    elif inst.name =="POPFRAME":
        insPOPFRAME()
    
###############################################################################

####### ARGUMENT PARSING
argparser = argparse.ArgumentParser()
argparser.add_argument("--source", nargs=1, help="input file")
argparser.add_argument("--input", nargs=1, help="File containing inputs for reading interpreted code")
args = vars(argparser.parse_args())
if args['input']:
  inputFile = args['input'][0]
else:
  inputFile = None
if args['source']:
  sourceFile = args['source'][0]
else:
  sourceFile = None
###############################################################################

###### XML SOURCE FILE PARSING
tree = None
try:
  if sourceFile:
    tree = ET.parse(sourceFile)
  else:
    tree = ET.parse(stdin)
except Exception as e:
  stderr.write(str(e)+"\n")
  stderr.write("Error occured when parsing source file\n")
  exit(31)


###### XML SORT #####
root = tree.getroot()
if root.tag != 'program':
  stderr.write("Root tag is not program\n")
  exit(32)

#sort
try:
  root[:] = sorted(root, key=lambda child: (child.tag, int(child.get('order'))))
except Exception as e:
  stderr.write(str(e)+"\n")
  stderr.write("Error occured when sorting <instruction> elements\n")
  exit(32)

# sort <arg> elements
for child in root:
  try:
    child[:] = sorted(child, key=lambda child: (child.tag))
    #print(child)
  except Exception as e:
    stderr.write(str(e)+"\n")
    stderr.write("Error occured when sorting <arg#> elements\n")
    exit(32)

#header check
if not('language' in list(root.attrib.keys())):
    stderr.write("language attribute missing\n")
    exit(32)
if not(re.match(r"ippcode22", root.attrib['language'],re.IGNORECASE)):
    stderr.write("Wrong language \n")   
    exit(32)

order = 0

for child in root:
    if child.tag != 'instruction':
        stderr.write("wrong or missing element\n")
        exit(32)
    list_of_attributes=list(child.attrib.keys())

    if not('order' in list_of_attributes):
        stderr.write("missing 'order'\n")
        exit(32)
    if not('opcode' in list_of_attributes):
        stderr.write("missing 'opcode'\n")   
        exit(32)
    if child.attrib['order']==order:
        stderr.write("error same order \n") 
        exit(32)
    order=child.attrib['order']

#iterace v instrucki
    for child in root:
        duplicates = set()
        for i in child:
            if i.tag not in duplicates:
                duplicates.add(i.tag)
        if len(duplicates) != len(child):
            stderr.write("duplicate argument\n")
            exit(32)
        
        for i in child:
            if not(re.match(r"arg[123]",i.tag)):
                stderr.write("wrong number of arguments\n")
                exit(32)
            attributes = list(i.attrib)
            if not('type' in attributes):
                stderr.write("missing type attribute\n")
                exit(32)
# instruction list
instruction_counter = 1
for element in root:
    instructions.append(instruction(element.attrib['opcode'].upper(),instruction_counter))
    for subelement in element:
        instructions[instruction_counter-1].add_argument(
            subelement.attrib['type'].lower(),subelement.text
        )
    instruction_counter +=1
        
for i in instructions:
    if i.name == "LABEL":
        labels.update({i.args[0].value:i.number})

while positionInProgram != len(instructions):
    interpretInstruction(instructions[positionInProgram])
    positionInProgram += 1
        
