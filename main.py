import subprocess
import sys
import re
import os
import inspect
import random
import time
import argparse
import json

from similar_text import similar_text
from rply import LexerGenerator
from rply import ParserGenerator
from rply.token import Token
from functools import cache


argslist = "ecx.edx.ebx.edi.esi.r8d.r9d.r10d".split(".")

def error(msg,code=0):
    print(msg)
    sys.exit(code)



class SyntaxChecker(object):
    def __init__(self,lexerStream,lib=None):
        self.lib = lib
        self.tokens = []
        self.cursor = 0
        for i in lexerStream:
            self.tokens.append(i)

    def pass_except(self,ttype,msg):
        if not self.current().gettokentype() == ttype:
            self.SyntaxError(msg,self.current())

    def eat(self):
        self.cursor += 1

    def current(self):
        res = None
        try:
            res = self.tokens[self.cursor]
        except:
            res = None
        return res

    def SyntaxError(self,msg,tok):
        if self.lib:
            loc = tok.source_pos
            location = f"{loc.lineno+1}.{loc.colno-1}"
            print(f"Syntax Error at lib '{self.lib}' {location}: {msg}")
            sys.exit(1)
        loc = tok.source_pos
        location = f"{loc.lineno+1}.{loc.colno-1}"
        print(f"Syntax Error at {location}: {msg}")
        sys.exit(1)

    def pass_args(self):
        c = 0
        tok = self.tokens[self.cursor-1]
        while self.current().gettokentype() != ")":
            self.eat()
            c += 1
            if c > 256 or self.current().gettokentype() == "NL":
                self.SyntaxError(f"( was never closed",tok)
            if self.current().gettokentype() == "(":
                self.pass_args()
        self.eat()

    def check_func_declaration(self):
        self.eat()
        self.pass_except("ID","missing function name at dec"+
                "laration")
        self.eat()
        self.pass_except("(","missing (  at function dec"+
                "laration")
        self.eat()
        self.check_args_annot()
        self.pass_except("->","missing -> at function declaration")
        self.eat()
        self.pass_except("TYPE","missing function type after ->")
        self.eat()
        self.pass_except("{","missing { open block at function dec"+
                "laration")
        self.eat()


    def check_func_call(self):
        self.eat()
        self.pass_except("ID","missing function name at call")
        self.eat()
        self.pass_except("(","missing ( at function call")
        self.eat()
        self.pass_args()

    def check_arg_annot(self):
        if self.current().value == "void":
            self.eat()
            return
        self.pass_except("ID","missing arg name at function declaration")
        self.eat()
        self.pass_except(":","missing : at args function")
        self.eat()
        self.pass_except("TYPE","missing arg type")
        self.eat()
        if self.current().gettokentype() == ")":
            return
        else:
            self.pass_except(",","missing , beetwen args")
            self.eat()

    def check_args_annot(self):
        c = 0
        tok = self.tokens[self.cursor-1]
        while self.current().gettokentype() != ")":
            c += 1
            self.check_arg_annot()
            if c > 256 or self.current().gettokentype() == "NL":
                self.SyntaxError(f"( was never closed",tok)
        self.eat()

    def check_include(self):
        self.eat()
        self.pass_except("CALL_METHOD","missing lib name at #include")
        self.eat()

    def check_asm(self):
        self.eat()
        self.pass_except("STRING","missing string after __asm__")
        self.eat()

    def check_if(self):
        self.eat()
        self.pass_except("(","missing ( at if")
        self.eat()
        self.pass_args()
        self.pass_except("{","missing open block { at if")
        self.eat()

    def check_const(self):
        self.eat()
        self.pass_except("ID","missing name at const declaration")
        self.eat()
        self.pass_except("=","missing = at const declaration")
        self.eat()

    def check_return(self):
        self.eat()
        if self.current().gettokentype() == "NL":
            self.SyntaxError("missing expression at return",self.current())

    def check_s_cast(self):
        self.eat()
        self.pass_except("<","missing < at static cast")
        self.eat()
        self.pass_except("TYPE","missing type at static cast")
        self.eat()
        self.pass_except(">","missing > at static cast")
        self.eat()
        self.pass_except("(","missing ( at static cast")
        self.eat()
        self.pass_args()

    def check_adr(self):
        self.eat()
        self.pass_except("ID","& operator except variable name")
        self.eat()

    def check_else(self):
        self.eat()
        self.pass_except("{","except { at else")
        self.eat()

    def check_array(self):
        self.eat()
        self.pass_except("TYPE","array except type")
        self.eat()
        self.pass_except("[","array create except [")
        self.eat()
        self.pass_except("NUMBER","size of static array created on stack musnt only constant number literal")
        self.eat()
        self.pass_except("]","[ was never closed at array")
        self.eat()
        self.pass_except("ID","missing array name")
        self.eat()

    def check(self):
        while self.current():
            curtype = self.current().gettokentype()
            if curtype == "DEF":
                self.check_func_declaration()
            elif curtype == "CALL":
                self.check_func_call()
            elif curtype == "INCLUDE":
                self.check_include()
            elif curtype == "ASM":
                self.check_asm()
            elif curtype == "IF":
                self.check_if()
            elif curtype == "CONST":
                self.check_const()
            elif curtype == "RETURN":
                self.check_return()
            elif curtype == "CAST":
                self.check_s_cast()
            elif curtype == "ADR":
                self.check_adr()
            elif curtype == "ELSE":
                self.check_else()
            elif curtype == "ARRAY":
                self.check_array()
            else:
                self.eat()



class typechecker:

    int_types = ["int8","int16","int32","int","bool","char","void"]

    @classmethod
    def TypeError(self,error):
        inter.error(error)
        sys.exit(0)

    @classmethod
    def pass_return(self, funcname, obj):
        if not funcname in inter.Functions:
            return
        vartype = inter.Functions[funcname]["type"]
        if isinstance(obj,ast.FuncCall):
            functype = inter.Functions[obj["name"]]["type"]
            if not vartype == functype:
                self.TypeError(f"TypeError at return: " + 
                                f"except type - {vartype}, got - function type {functype}")
        elif isinstance(obj,ast.Integer):
            if not vartype in self.int_types:
                self.TypeError(f"TypeError at return: " + 
                                f"except type - {vartype}, got - int")
        elif isinstance(obj,ast.String):
            if not vartype == "string":
                self.TypeError(f"TypeError at return: " + 
                                f"except type - {vartype}, got - string")
        elif isinstance(obj,ast.Char):
            if not vartype in self.int_types and not vartype == "char":
                self.TypeError(f"TypeError at return: " + 
                                f"except type - {vartype}, got - char")
        elif isinstance(obj,ast.GetAdr) or isinstance(obj,ast.Ptr):
            if not vartype == "ptr":
                self.TypeError(f"TypeError at return: " + 
                                f"except type - {vartype}, got - ptr")
        elif isinstance(obj,ast.GetVar):
            if obj["name"] in inter.Consts:
                self.pass_assign(varname,inter.Consts[obj["name"]])
                return
            vartype2 = inter.Vars[obj["name"]]["type"]
            if not vartype == vartype2:
                if vartype in self.int_types and not vartype2 in self.int_types:
                    self.TypeError(f"TypeError at return: " + 
                                f"except type - {vartype}, got - {vartype2}")
        elif isinstance(obj,ast.GetArrItem):
            arrtype = inter.Vars[obj["name"]]["type"]
            if arrtype == "ptr":
                return
            if not vartype == arrtype:
                self.TypeError(f"TypeError at return: " + 
                                f"except type - {vartype}, got - {arrtype}")
        else:
            return


    @classmethod
    def pass_assign(self, varname, obj):
        if not varname in inter.Vars:
            return
        vartype = inter.Vars[varname]["type"]
        if isinstance(obj,ast.FuncCall):
            functype = inter.Functions[obj["name"]]["type"]
            if not vartype == functype:
                self.TypeError(f"TypeError at variable assignment: " + 
                                f"except type - {vartype}, got - function type {functype}")
        elif isinstance(obj,ast.Integer):
            if not vartype in self.int_types:
                self.TypeError(f"TypeError at variable assignment: " + 
                                f"except type - {vartype}, got - int")
        elif isinstance(obj,ast.String):
            if not vartype == "string":
                self.TypeError(f"TypeError at variable assignment: " + 
                                f"except type - {vartype}, got - string")
        elif isinstance(obj,ast.Char):
            if not vartype in self.int_types and not vartype == "char":
                self.TypeError(f"TypeError at variable assignment: " + 
                                f"except type - {vartype}, got - char")
        elif isinstance(obj,ast.GetAdr) or isinstance(obj,ast.Ptr):
            if not vartype == "ptr":
                self.TypeError(f"TypeError at variable assignment: " + 
                                f"except type - {vartype}, got - ptr")
        elif isinstance(obj,ast.GetVar):
            if obj["name"] in inter.Consts:
                self.pass_assign(varname,inter.Consts[obj["name"]])
                return
            vartype2 = inter.Vars[obj["name"]]["type"]
            if not vartype == vartype2:
                self.TypeError(f"TypeError at variable assignment: " + 
                                f"except type - {vartype}, got - {vartype2}")
        elif isinstance(obj,ast.GetArrItem):
            arrtype = inter.Vars[obj["name"]]["type"]
            if arrtype == "ptr":
                return
            if not vartype == arrtype:
                self.TypeError(f"TypeError at variable assignment: " + 
                                f"except type - {vartype}, got - {arrtype}")
        else:
            return

    @classmethod
    def pass_args(self, funcname, callobj):
        for c,ar in enumerate(inter.Functions[funcname]["args"]):
            vartype = ar[1]
            obj = callobj["args"][c]
            if isinstance(obj,ast.FuncCall):
                functype = inter.Functions[obj["name"]]["type"]
                if not vartype == functype:
                    if vartype in self.int_types and not functype in self.int_types:
                        self.TypeError(f"TypeError at function call (arg {c}): " + 
                                    f"except type - {vartype}, got - function type {functype}")
            elif isinstance(obj,ast.Integer):
                if not vartype in self.int_types:
                    self.TypeError(f"TypeError at function '{funcname}' call (arg {c}): " + 
                                    f"except type - {vartype}, got - int")
            elif isinstance(obj,ast.String):
                if not vartype == "string":
                    if vartype == "ptr":
                        return
                    self.TypeError(f"TypeError at function '{funcname}' call (arg {c}): " + 
                                    f"except type - {vartype}, got - string")
            elif isinstance(obj,ast.Char):
                if not vartype in self.int_types and not vartype == "char":
                    self.TypeError(f"TypeError at function '{funcname}' call (arg {c}): " + 
                                    f"except type - {vartype}, got - char")
            elif isinstance(obj,ast.GetAdr) or isinstance(obj,ast.Ptr):
                if not vartype == "ptr" or vartype == "string":
                    self.TypeError(f"TypeError at function '{funcname}' call (arg {c}): " + 
                                    f"except type - {vartype}, got - ptr")
            elif isinstance(obj,ast.GetVar):
                if obj["name"] in inter.Consts:
                    self.pass_assign(varname,inter.Consts[obj["name"]])
                    return
                if not obj["name"] in inter.Vars:
                    return
                vartype2 = inter.Vars[obj["name"]]["type"]
                if not vartype == vartype2:
                    if vartype == "int" and vartype2 in self.int_types:
                        return 
                    if vartype == "string" and vartype2 == "ptr":
                        return
                    self.TypeError(f"TypeError at function '{funcname}' call (arg {c}): " + 
                                    f"except type - {vartype}, got - {vartype2}")
            elif isinstance(obj,ast.GetArrItem):
                arrtype = inter.Vars[obj["name"]]["type"]
                if arrtype == "ptr":
                    return
                if not vartype == arrtype:
                    self.TypeError(f"TypeError at function '{funcname}' call (arg {c}): " + 
                                    f"except type - {vartype}, got - {arrtype}")
            else:
                continue



"""
yula object for contact yula lang and
python objects
"""
class YulaObject(object):
    def __init__(self,props):
        self.props = props
        
    def __getitem__(self,item):
        try:
            return self.props[item]
        except:
            pass
        
    def __setitem__(self,item,value):
        self.props[item] = value
        

class ast:
    class Integer(YulaObject):
        n = 0
        def eval(self):
            if self['value'].bit_length() > 4:
                inter.error(f"\tconstant {self['value']} is so big ({self['value'].bit_length()} bytes).")
            inter.output(f"\tpush {self['value']}")
            
            
    class Statement(YulaObject):
        def get_block(self):
            return self.props["block"]

        def run(self):
            for obj in self.get_block().get():
                obj.eval()
               
            
    class BinaryOp(object):
        b = 0
        def __init__(self,left,right,dop=None):
            self.left = left
            self.right = right
            self.dop = dop

            
    class Add(BinaryOp):
        def eval(self):
            if not self.dop:
                if isinstance(self.left,ast.Integer):
                    inter.output(f"\tmov eax, {self.left['value']}")
                else:
                    self.left.eval()
                if isinstance(self.right,ast.Integer):
                    inter.output(f"\tmov ebx, {self.right['value']}")
                else:
                    self.right.eval()
                if not isinstance(self.right,ast.Integer):
                    inter.output("\tpop ebx")
                if not isinstance(self.left,ast.Integer):
                    inter.output("\tpop eax")
                inter.output("\tadd eax, ebx")
                inter.output("\tpush eax")
            else:
                ast.Integer({'value': self.dop}).eval()
            
            
    class Sub(BinaryOp):
        def eval(self):
            if not self.dop:
                if isinstance(self.left,ast.Integer):
                    inter.output(f"\tmov eax, {self.left['value']}")
                else:
                    self.left.eval()
                if isinstance(self.right,ast.Integer):
                    inter.output(f"\tmov ebx, {self.right['value']}")
                else:
                    self.right.eval()
                if not isinstance(self.right,ast.Integer):
                    inter.output("\tpop ebx")
                if not isinstance(self.left,ast.Integer):
                    inter.output("\tpop eax")
                inter.output("\tsub eax, ebx")
                inter.output("\tpush eax")
            else:
                ast.Integer({'value': self.dop}).eval()
            
            
    class Mul(BinaryOp):
        def eval(self):
            if not self.dop:
                if isinstance(self.left,ast.Integer):
                    inter.output(f"\tmov eax, {self.left['value']}")
                else:
                    self.left.eval()
                if isinstance(self.right,ast.Integer):
                    inter.output(f"\tmov ebx, {self.right['value']}")
                else:
                    self.right.eval()
                if not isinstance(self.right,ast.Integer):
                    inter.output("\tpop ebx")
                if not isinstance(self.left,ast.Integer):
                    inter.output("\tpop eax")
                inter.output("\timul eax, ebx")
                inter.output("\tpush eax")
            else:
                ast.Integer({'value': self.dop}).eval()
            

    class Div(BinaryOp):
        def eval(self):
            if not self.dop:
                if isinstance(self.left,ast.Integer):
                    inter.output(f"\tmov eax, {self.left['value']}")
                else:
                    self.left.eval()
                if isinstance(self.right,ast.Integer):
                    inter.output(f"\tmov ebx, {self.right['value']}")
                else:
                    self.right.eval()
                if not isinstance(self.right,ast.Integer):
                    inter.output("\tpop ebx")
                if not isinstance(self.left,ast.Integer):
                    inter.output("\tpop eax")
                inter.output("\tmov edx, 0")
                inter.output("\tdiv ebx")
                inter.output("\tpush eax")
                inter.output("\tmov edx, ecx")
            else:
                ast.Integer({'value': self.dop}).eval()
        
                  
    class Block(YulaObject):
        def append(self,node):
            if not "lines" in self.props:
                self["lines"] = []
                self["lines"] = [node] + self["lines"]
            else:
                self["lines"] = [node] + self["lines"]

        def get(self):
            return self["lines"]

        def run(self):
            for line in self.get():
                line.eval()

        def eval(self):
            self.run()

    class DeclareVar(YulaObject):
        def eval(self):
            if self["name"] in inter.Vars:
                inter.error(f"NameError: cannot declare '{self['name']}', variable"+
                            f" already declared in '{inter.Vars[self['name']]['f']}' function")
            if self["type"] in inter.sizes:
                inter.var_index += inter.sizes[self["type"]]
            else:
                inter.var_index += 4
            ofs = inter.var_index
            inter.Vars[self["name"]] = {}
            if "class" in self.props:
                inter.Vars[self["name"]]["class"] = self["class"]
            inter.Vars[self["name"]]["type"] = self["type"]
            inter.Vars[self["name"]]["f"] = globals()["curfunc"]
            inter.Vars[self["name"]]["offset"] = ofs
            if "value" in self.props:
                ast.AssignVar({'name': self["name"],'value': self['value']}).eval()

    class AssignVar(YulaObject):
        def eval(self):
            typechecker.pass_assign(self["name"],self["value"])
            value = self["value"]
            if isinstance(value,ast.Integer):
                inter.output(f"\tmov dword [ebp-{inter.Vars[self['name']]['offset']}], dword {value['value']}")
                return
            if isinstance(value,ast.Char):
                inter.output(f"\tmov {inter.sizeswords[inter.Vars[self['name']]['type']]} [ebp-{inter.Vars[self['name']]['offset']}], {inter.sizeswords[inter.Vars[self['name']]['type']]} {ord(value['value'])}")
                return
            value.eval()
            inter.output("\tpop eax")
            inter.output(f"\tmov {inter.sizeswords[inter.Vars[self['name']]['type']]} [ebp-{inter.Vars[self['name']]['offset']}], {inter.sizesreg[inter.Vars[self['name']]['type']]}")

    @classmethod
    def getval(self, yo):
        val = yo
        while hasattr(val,"eval"):
            val = val.eval()
        return val


    class Return(YulaObject):
        def eval(self):
            typechecker.pass_return(globals()["curfunc"],self["value"])
            if isinstance(self["value"],ast.Integer):
                if str(self["value"]["value"]) == "0":
                    inter.output(f"\txor eax, eax")
                else:
                    inter.output(f"\tmov eax, {self['value']['value']}")
                inter.output(f"\tadd esp, {globals()['stack_alloc']}")
                inter.output("\tpop ebp")
                inter.output(f"\tret")
                return
            if isinstance(self["value"],ast.GetVar):
                inter.output(f"\tmov eax, dword [ebp-{inter.Vars[self['value']['name']]['offset']}]")
                inter.output(f"\tadd esp, {globals()['stack_alloc']}")
                inter.output("\tpop ebp")
                inter.output(f"\tret")
                return
            self["value"].eval()
            inter.output(f"\tpop eax")
            inter.output(f"\tadd esp, {globals()['stack_alloc']}")
            inter.output("\tpop ebp")
            inter.output(f"\tret")

    class String(YulaObject):
        def eval(self):
            if self["value"] in inter.strs:
                ind = ""
                for i in inter.strs:
                    if i == self["value"]:
                        ind = i
                        break
                inter.output(f"\tpush {inter.strs[ind]}")
                return
            else:
                ind = f"s_{inter.str_index}"
                inter.strs[self["value"]] = ind
                inter.str_index += 1
                inter.output(f"\tpush {ind}")
                value = '"' + self["value"].replace(r"\n",'",10,"') + '"'
                inter._add_data("\t" + f"{ind}: db " + value + ",0")


    class FuncDecl(Statement):
        def eval(self):
            if self["name"] in inter.Functions:
                return
            cs = {}
            cs["name"] = self["name"]
            cs["type"] = self["type"]
            inter.callstack.append(cs)
            globals()["curfunc"] = self["name"]
            if "curclass" in globals():
                if globals()["curclass"]:
                    inter.methods[self["name"]] = self
            inter.Functions[self["name"]] = {}
            inter.Functions[self["name"]]["args"] = self["args"]
            inter.Functions[self["name"]]["block"] = self["block"]
            inter.Functions[self["name"]]["type"] = self["type"]
            offsets = inter.block_has(self["block"])
            salloc = 0
            if not self["name"] == "main":
                for i in self["args"]:
                    if i[1] in inter.sizes:
                        salloc += inter.sizes[i[1]]
                    else:
                        salloc += 4
            for i in offsets:
                salloc += offsets[i]
            salloc = (salloc + 4) * 2
            globals()["stack_alloc"] = salloc
            argstring = ""
            for i in self["args"]:
                argstring += f"{i[1]} {i[0]},"
            inter.output(f"\n{self['name']}:")
            inter.output(f"\t; {self['type']} {self['name']}({argstring[:-1]})")
            inter.output(f"""\tpush ebp
\tmov ebp, esp
\tsub esp, {salloc}""")
            sizes = {"int32": 4,"int16": 2,"int8":1,'int':4,"string": 4}
            if not self["name"] == "main":
                ofs = 0
                for c,arg in enumerate(self["args"]):
                    reg = globals()["argslist"][c]
                    ast.DeclareVar({'name': arg[0],'type': arg[1],"line": None}).eval()
                    inter.output(f"\tmov dword [ebp-{inter.Vars[arg[0]]['offset']}], {reg}")
            else:
                if not self["args"] == []:
                    if len(self["args"]) > 0 and self["args"][0][0] == "argc":
                        ast.DeclareVar({'name': "argc",'type': "int","line": None}).eval()
                        inter.output(f"\tmov edx, dword [ebp+8]")
                        inter.output(f"\tmov dword [ebp-{inter.Vars['argc']['offset']}], edx")
                    if len(self["args"]) > 1 and self["args"][1][0] == "argv":
                        ast.DeclareVar({'name': "argv",'type': "string","line": None}).eval()
                        inter.output(f"\tmov edx, dword [ebp+12]")
                        inter.output(f"\tmov [ebp-12], edx")

            inter.Functions[self["name"]]["block"].eval()
            if self["type"] == "void":
                ast.Return({'value': ast.Integer({'value': 0})}).eval()
            for i in inter.Vars.copy():
                try:
                    if inter.Vars[i]["f"] == self["name"]:
                        del inter.Vars[i]
                except:
                    pass
            if inter.var_index >= 8012:
                inter.error(f"you allocate in stack {inter.var_index*2} bytes\n"+
                    f"\tdon't use big local variables or use $alloc in std lib")
            inter.var_index = 4
            del inter.callstack[-1]


    class Asm(YulaObject):
        def eval(self):
            if self["code"] in inter.asms:
                if "extern" in self["code"]:
                    return
            inter.output("\t" + self["code"])
            inter.asms[self["code"]] = 0

    class GetVar(YulaObject):
        def eval(self):
            if self["name"] in inter.Vars:
                inter.output(f"\tpush dword [ebp-{inter.Vars[self['name']]['offset']}]")
            elif self["name"] in inter.Consts:
                inter.Consts[self["name"]].eval()
            elif self["name"] in inter.Functions:
                inter.error(f"not found variable {self['name']}.\n"+
                    f"\tdid you mean ${self['name']}(...)?")
            else:
                vname = ""
                for i in inter.Vars.copy():
                    if self["name"].lower() == i.lower():
                        vname = i
                if not vname == "":
                    c = 0
                    vname2 = ""
                    for i in inter.Vars.copy():
                        for ct,j in enumerate(list(i)):
                            try:
                                if self["name"][ct] == j:
                                    c += 1
                                if c > int(len(self["name"]/2)):
                                    vname = i
                            except:
                                break
                    if not vname2 == "":
                        inter.error(f"not found variable {self['name']}.\n"+
                        f"\tdid you mean {vname2}?")
                    else:
                        inter.error(f"not found variable {self['name']}.\n"+
                        f"\tdid you mean {vname}?")
                else:
                    vname2 = ""
                    for i in inter.Vars.copy():
                        proc = similar_text(self["name"],i)
                        if proc > 70:
                            vname2 = i
                    if not vname2 == "":
                        inter.error(f"not found variable {self['name']}.\n"+
                        f"\tdid you mean {vname2}?")
                    else:
                        inter.error(f"not found variable {self['name']}")


    class GetAdr(YulaObject):
        def eval(self):
            if "null" in self.props:
                inter.output("push 0")
            ofs = inter.Vars[self["name"]]["offset"]
            inter.output(f"\tmov eax, ebp")
            inter.output(f"\tsub eax, {ofs}")
            inter.output(f"\tpush eax")

    class Bool(YulaObject):
        def eval(self):
            if self["value"] == "false":
                inter.output(f"\tpush 0")
            else:
                inter.output(f"\tpush 1")

    class If(Statement):
        def eval(self):
            if isinstance(self["condition"],ast.Bool):
                if self["condition"]["value"] == "false":
                    if self["else"]:
                        inter.output(f"\t{elselab}:")
                        self["else"].eval()
                        inter.output(f"\tjmp {endlab}")
                        inter.output(f"\t{endlab}:")
                    return
                if self["condition"]["value"] == "true":
                    self["block"].eval()
                    return
            if isinstance(self["condition"],ast.Integer):
                if self["condition"]["value"] == 0:
                    if self["else"]:
                        inter.output(f"\t{elselab}:")
                        self["else"].eval()
                        inter.output(f"\tjmp {endlab}")
                        inter.output(f"\t{endlab}:")
                    return
                if self["condition"]["value"] != 0:
                    self["block"].eval()
                    return
            self["condition"].eval()
            iflab = str("IF" + str(inter.lab_index))
            inter.lab_index += 1
            inter.output("\tpop eax")
            inter.output("\tcmp eax, 0")
            elselab = str("ELSE" + str(inter.lab_index))
            inter.lab_index += 1
            endlab = str("END" + str(inter.lab_index))
            inter.lab_index += 1
            inter.output(f"\tje {elselab}")
            inter.output(f"\t{iflab}:")
            self["block"].eval()
            if self["else"]:
                inter.output(f"\tjmp {endlab}")
            if self["else"]:
                inter.output(f"\t{elselab}:")
                self["else"].eval()
                inter.output(f"\tjmp {endlab}")
            else:
                inter.output(f"\t{elselab}:")
            inter.output(f"\t{endlab}:")

    class While(Statement):
        def eval(self):
            if isinstance(self["condition"],ast.Bool):
                if self["condition"]["value"] == "false":
                    return
            if isinstance(self["condition"],ast.Integer):
                if self["condition"]["value"] == 0:
                    return
            preiflab = str("PREIF" + str(inter.lab_index))
            inter.lab_index += 1
            blocklab = str("WHILE" + str(inter.lab_index))
            inter.lab_index += 1
            breaklab = str("END" + str(inter.lab_index))
            inter.breaks.append(breaklab)
            inter.lab_index += 1
            inter.output(f"\t{preiflab}:")
            self["condition"].eval()
            inter.output(f"\tpop eax")
            inter.output(f"\tcmp eax, 0")
            inter.output(f"\tje {breaklab}")
            inter.output(f"\tjmp {blocklab}")
            inter.output(f"\t{blocklab}:")
            self["block"].eval()
            inter.output(f"\tjmp {preiflab}")
            inter.output(f"\t{breaklab}:")
            del inter.breaks[-1]



    class FuncCall(YulaObject):
        def eval(self):
            name = self["name"]
            args = self["args"]
            if "obj" in self.props:
                self["args"] = [ast.GetVar({'name': self["obj"]})] + self["args"]
                args = self["args"]
            ex_args = inter.Functions[name]["args"]
            if not len(args) == len(ex_args):
                inter.error(f"function {name} except {len(ex_args)}, got {len(args)}")
            typechecker.pass_args(name,self)
            argslist = globals()["argslist"]
            for c,arg in enumerate(args):
                reg = argslist[c]
                if isinstance(arg,ast.Integer):
                    inter.output(f"\tmov {reg}, {arg['value']}")
                    continue
                arg.eval()
                inter.output(f"\tpop {reg}")
            inter.output(f"\tcall {name}")
            if not inter.Functions[name]["type"] == "void":
                inter.output(f"\tpush eax")


    class Equal(BinaryOp):
        def eval(self):
            if self.dop:
                if self.dop == "False":
                    inter.output(f"\tpush 0")
                else:
                    inter.output(f"\tpush 1")
                return
            one = str("L" + str(inter.lab_index))
            inter.lab_index += 1
            two = str("L" + str(inter.lab_index))
            inter.lab_index += 1
            endlab = str("L" + str(inter.lab_index))
            inter.lab_index += 1

            if isinstance(self.left,ast.Integer):
                inter.output(f"\tmov eax, {self.left['value']}")
            else:
                self.left.eval()

            if isinstance(self.right,ast.Integer):
                inter.output(f"\tmov ebx, {self.right['value']}")
            else:
                self.right.eval()

            if not isinstance(self.right,ast.Integer):
                inter.output(f"\tpop ebx")
            if not isinstance(self.left,ast.Integer):
                inter.output(f"\tpop eax")
            inter.output(f"\tcmp eax, ebx")
            inter.output(f"\tje {one}")
            inter.output(f"\tjne {two}")
            inter.output(f"\t{one}:")
            inter.output(f"\tpush 1")
            inter.output(f"\tjmp {endlab}")
            inter.output(f"\t{two}:")
            inter.output(f"\tpush 0")
            inter.output(f"\t{endlab}:")

    class Less(BinaryOp):
        def eval(self):
            if self.dop:
                if self.dop == "False":
                    inter.output(f"\tpush 0")
                else:
                    inter.output(f"\tpush 1")
                return
            one = str("L" + str(inter.lab_index))
            inter.lab_index += 1
            two = str("L" + str(inter.lab_index))
            inter.lab_index += 1
            endlab = str("L" + str(inter.lab_index))
            inter.lab_index += 1
            if isinstance(self.left,ast.Integer):
                inter.output(f"\tmov eax, {self.left['value']}")
            else:
                self.left.eval()

            if isinstance(self.right,ast.Integer):
                inter.output(f"\tmov ebx, {self.right['value']}")
            else:
                self.right.eval()

            if not isinstance(self.right,ast.Integer):
                inter.output(f"\tpop ebx")
            if not isinstance(self.left,ast.Integer):
                inter.output(f"\tpop eax")
            inter.output(f"\tcmp eax, ebx")
            inter.output(f"\tjl {one}")
            inter.output(f"\tjnl {two}")
            inter.output(f"\t{one}:")
            inter.output(f"\tpush 1")
            inter.output(f"\tjmp {endlab}")
            inter.output(f"\t{two}:")
            inter.output(f"\tpush 0")
            inter.output(f"\t{endlab}:")

    class Above(BinaryOp):
        def eval(self):
            if self.dop:
                if self.dop == "False":
                    inter.output(f"\tpush 0")
                else:
                    inter.output(f"\tpush 1")
                return
            one = str("L" + str(inter.lab_index))
            inter.lab_index += 1
            two = str("L" + str(inter.lab_index))
            inter.lab_index += 1
            endlab = str("L" + str(inter.lab_index))
            inter.lab_index += 1
            if isinstance(self.left,ast.Integer):
                inter.output(f"\tmov eax, {self.left['value']}")
            else:
                self.left.eval()

            if isinstance(self.right,ast.Integer):
                inter.output(f"\tmov ebx, {self.right['value']}")
            else:
                self.right.eval()

            if not isinstance(self.right,ast.Integer):
                inter.output(f"\tpop ebx")
            if not isinstance(self.left,ast.Integer):
                inter.output(f"\tpop eax")
            inter.output(f"\tcmp eax, ebx")
            inter.output(f"\tja {one}")
            inter.output(f"\tjna {two}")
            inter.output(f"\t{one}:")
            inter.output(f"\tpush 1")
            inter.output(f"\tjmp {endlab}")
            inter.output(f"\t{two}:")
            inter.output(f"\tpush 0")
            inter.output(f"\t{endlab}:")


    class Char(YulaObject):
        def eval(self):
            inter.output(f"\tpush dword {ord(self['value'])}")

    class Break(YulaObject):
        def eval(self):
            inter.output(f"\tjmp {inter.breaks[-1]}")

    class Inc(YulaObject):
        def eval(self):
            if isinstance(self["adr"],ast.GetAdr):
                ofs = inter.Vars[self["adr"]["name"]]["offset"]
                if isinstance(self["value"],ast.Integer):
                    inter.output(f"\tmov eax, {self['value']['value']}")
                    inter.output(f"\tmov ebx, dword [ebp-{ofs}]")
                    inter.output(f"\tadd eax, ebx")
                    inter.output(f"\tmov dword [ebp-{ofs}], eax")
                else:
                    inter.output(f"\tmov edi, [ebp-{ofs}]")
                    self["value"].eval()
                    inter.output(f"\tpop edx")
                    inter.output(f"\tadd edi, edx")
                    inter.output(f"\tmov dword [ebp-{ofs}], edx")
                return
            self["adr"].eval()
            if isinstance(self["value"],ast.Integer):
                inter.output(f"\tmov eax, {self['value']['value']}")
            else:
                self["value"].eval()
            inter.output(f"\tpop ebx")
            if not isinstance(self["value"],ast.Integer):
                inter.output(f"\tpop eax")
            inter.output(f"\tmov eax, dword [eax]")
            inter.output(f"\tadd eax, ebx")
            inter.output(f"\tmov edx, ebp")
            inter.output(f"\tsub edx, ebx")
            inter.output(f"\tmov dword [edx], eax")

    class Dec(YulaObject):
        def eval(self):
            if isinstance(self["adr"],ast.GetAdr):
                ofs = inter.Vars[self["adr"]["name"]]["offset"]
                if isinstance(self["value"],ast.Integer):
                    inter.output(f"\tmov eax, {self['value']['value']}")
                    inter.output(f"\tmov ebx, dword [ebp-{ofs}]")
                    inter.output(f"\tsub eax, ebx")
                    inter.output(f"\tmov dword [ebp-{ofs}], eax")
                else:
                    inter.output(f"\tmov edi, dword [ebp-{ofs}]")
                    self["value"].eval()
                    inter.output(f"\tpop edx")
                    inter.output(f"\tsub edi, edx")
                    inter.output(f"\tmov dword [ebp-{ofs}], edx")
                return
            self["adr"].eval()
            if isinstance(self["value"],ast.Integer):
                inter.output(f"\tmov eax, {self['value']['value']}")
            else:
                self["value"].eval()
            inter.output(f"\tpop ebx")
            if not isinstance(self["value"],ast.Integer):
                inter.output(f"\tpop eax")
            inter.output(f"\tmov eax, dword [eax]")
            inter.output(f"\tsub eax, ebx")
            inter.output(f"\tmov edx, ebp")
            inter.output(f"\tsub edx, ebx")
            inter.output(f"\tmov dword [edx], eax")

    class GetP(YulaObject):
        def eval(self):
            if isinstance(self["adr"],ast.GetAdr):
                vname = self["adr"]["name"]
                ofs = inter.Vars[vname]["offset"]
                inter.output(f"\tpush dword [ebp-{ofs}]")
                return
            self["adr"].eval()
            inter.output(f"\tpop eax")
            inter.output(f"\tpush dword [eax]")

    class Include(YulaObject):
        def eval(self):
            inc = inter.compare_lib(open(self["file"].replace(".","/")+".hl","r").read(),self["file"])
            inc.eval()

    class Not(YulaObject):
        def eval(self):
            if isinstance(self["condition"],ast.Integer):
                res = 0
                if not self["condition"]["value"] == 0:
                    res = 1
                inter.output(f"\tpush {res}")
                return
            if isinstance(self["condition"],ast.Bool):
                res = 0
                if not self["condition"]["value"] == "true":
                    res = 1
                inter.output(f"\tpush {res}")
                return
            self["condition"].eval()
            labtrue = inter.lab_index
            inter.lab_index += 1
            labfalse = inter.lab_index
            inter.lab_index += 1
            labend = inter.lab_index
            inter.lab_index += 1
            inter.output(f"\tpop eax")
            inter.output(f"\tcmp eax, 0")
            inter.output(f"\tje L{labtrue}")
            inter.output(f"\tjmp L{labfalse}")
            inter.output(f"\tL{labtrue}:")
            inter.output(f"\tpush 1")
            inter.output(f"\tjmp L{labend}")
            inter.output(f"\tL{labfalse}:")
            inter.output(f"\tpush 0")
            inter.output(f"\tL{labend}:")

    class Const(YulaObject):
        def eval(self):
            inter.Consts[self["name"]] = self["value"]

    class Ptr(YulaObject):
        def eval(self):
            self["value"].eval()


    class Array(YulaObject):
        def eval(self):
            if self["size"]["value"] > 2000:
                inter.error(f"a size of static array is so big ({self['size']['value']})\n"+
                    f"\tbecase its allocate in stack {self['size']['value']*4} "+
                    f"bytes, got stack overflow")
            ast.DeclareVar({'name': self["name"],'type':self["type"]}).eval()
            inter.Vars[self["name"]]["isarray"] = True
            inter.Vars[self["name"]]["sizearray"] = self["size"]["value"]*inter.sizes[self["type"]]
            inter.var_index += (self["size"]["value"]*inter.sizes[self["type"]]) - inter.sizes[self["type"]]


    class GetArrItem(YulaObject):
        def eval(self):
            if self["name"] == "argv":
                if isinstance(self["index"],ast.Integer):
                    ofs = self["index"]["value"] * 4
                    inter.output(f"\tmov edx, dword [ebp-{inter.Vars['argv']['offset']}]")
                    inter.output(f"\tmov edx, dword [edx+{ofs}]")
                    inter.output(f"\tpush edx")
                    return 
                self["index"].eval()
                inter.output(f"\tpop ecx")
                inter.output(f"\tmov edx, dword [ebp-{inter.Vars['argv']['offset']}]")
                inter.output(f"\timul ecx, 4")
                inter.output(f"\tadd edx, ecx")
                inter.output(f"\tpush dword [edx]")
                return
            if isinstance(self["index"],ast.Integer):
                ofs = (self["index"]["value"] * inter.sizes[inter.Vars[self['name']]['type']]) + inter.Vars[self["name"]]["offset"]
                inter.output(f"\tpush dword [ebp-{ofs}]")
                return 
            ofs = inter.Vars[self["name"]]["offset"]
            inter.output(f"\tmov edx, {ofs}")
            self["index"].eval()
            inter.output(f"\tpop edi")
            inter.output(f"\timul edi, {inter.sizes[inter.Vars[self['name']]['type']]}")
            inter.output(f"\tadd edx, edi")
            inter.output(f"\tmov esi, ebp")
            inter.output(f"\tsub esi, edx")
            inter.output(f"\tpush dword [esi]")

    class SetArrItem(YulaObject):
        def eval(self):
            typechecker.pass_assign(self["name"],self["value"])
            if isinstance(self["index"],ast.Integer):
                ofs = (self["index"]["value"] * inter.sizes[inter.Vars[self['name']]['type']]) + inter.Vars[self["name"]]["offset"]
                if isinstance(self["value"],ast.Integer):
                    inter.output(f"\tmov [ebp-{ofs}], dword {self['value']['value']}")
                    return
                self["value"].eval()
                inter.output(f"\tpop edx")
                inter.output(f"\tmov [ebp-{ofs}], edx")
                return 
            ofs = inter.Vars[self["name"]]["offset"]
            inter.output(f"\tmov edx, {ofs}")
            self["index"].eval()
            inter.output(f"\tpop edi")
            inter.output(f"\timul edi, {inter.sizes[inter.Vars[self['name']]['type']]}")
            inter.output(f"\tadd edx, edi")
            inter.output(f"\tmov esi, ebp")
            inter.output(f"\tsub esi, edx")
            inter.output(f"\tmov ecx, esi")
            if isinstance(self["value"],ast.Integer):
                inter.output(f"\tmov dword [ecx], {self['value']['value']}")
                return
            self["value"].eval()
            inter.output(f"\tpop edx")
            inter.output(f"\tmov dword [ecx], edx")

    class For(Statement):
        def eval(self):
            if not isinstance(self["init"],ast.DeclareVar):
                inter.error(f"for except in one expression (1;2;3) variable "+
                            "declaration, like - int i = 0.")
            preiflab = str("PREIF" + str(inter.lab_index))
            inter.lab_index += 1
            blocklab = str("FOR" + str(inter.lab_index))
            inter.lab_index += 1
            breaklab = str("END" + str(inter.lab_index))
            inter.breaks.append(breaklab)
            inter.lab_index += 1
            vname = self["init"]["name"]
            self["init"].eval()
            inter.output(f"\t{preiflab}:")
            self["condition"].eval()
            inter.output(f"\tpop eax")
            inter.output(f"\tcmp eax, 0")
            inter.output(f"\tje {breaklab}")
            inter.output(f"\tjmp {blocklab}")
            inter.output(f"\t{blocklab}:")
            self["block"].eval()
            self["end"].eval()
            inter.output(f"\tjmp {preiflab}")
            inter.output(f"\t{breaklab}:")
            del inter.breaks[-1]

    class S_cast(YulaObject):
        def eval(self):
            ttype = self["type"]
            obj = self["obj"]
            if ttype == "int":
                if isinstance(obj,ast.String):
                    return ast.Integer({'value': int(obj["value"])})
                elif isinstance(obj,ast.Char):
                    return ast.Integer({'value': int(obj["value"])})
                elif isinstance(obj,ast.Bool):
                    if obj["value"] == "true":
                        return ast.Integer({'value': 1})
                    else:
                        return ast.Integer({'value': 0})
                else:
                    inter.Functions["preprocessor"] = {}
                    inter.Functions["preprocessor"]["type"] = "void"
                    globals()["curfunc"] = "preprocessor"
                    inter.error(f"\tcannot static cast {str(type(obj))} to int")
            elif ttype == "string":
                if isinstance(obj,ast.Integer):
                    return ast.String({'value': str(obj["value"])})
                elif isinstance(obj,ast.Char):
                    return ast.String({'value': str(obj["value"])})
                elif isinstance(obj,ast.Bool):
                    if obj["value"] == "true":
                        return ast.String({'value': "1"})
                    else:
                        return ast.String({'value': "0"})
                else:
                    inter.Functions["preprocessor"] = {}
                    inter.Functions["preprocessor"]["type"] = "void"
                    globals()["curfunc"] = "preprocessor"
                    inter.error(f"\tcannot static cast {str(type(obj))} to string")

    class Class(Statement):
        def eval(self):
            self.fields = []
            globals()["field_offset"] = 4
            globals()["curclass"] = self
            inter.classes[self["name"]] = {}
            inter.classes[self["name"]]["fields"] = {}
            inter.classes[self["name"]]["methods"] = {}
            for i in self["block"].get():
                if isinstance(i,ast.Field):
                    i.eval()
            for field in self.fields:
                inter.classes[self["name"]]["fields"][field["name"]] = field
            for i in self["block"].get():
                if isinstance(i,ast.FuncDecl):
                    i.eval()
            inter.classes[self["name"]]["methods"] = inter.methods.copy()
            inter.methods = {}
            globals()["curclass"] = None
            globals()["field_offset"] = 0


    class Field(YulaObject):
        def eval(self):
            self["offset"] = globals()["field_offset"]
            globals()["curclass"].fields.append(self)
            globals()["field_offset"] += 4

    class Object(YulaObject):
        def eval(self):
            sizeof = (len(inter.classes[self["class"]]["fields"])*4)+4
            ast.DeclareVar({'name': self["name"],'type': f"type[{self['class']}]",'class': self['class']}).eval()
            inter.output(f"\tpush {sizeof}")
            inter.output(f"\tcall malloc")
            inter.output(f"\tadd esp, 4")
            inter.output(f"\tmov dword [ebp-{inter.Vars[self['name']]['offset']}], eax")
            inter.output(f"\t; put sizeof class in first 4 bytes")
            inter.output(f"\tmov dword [eax], dword {sizeof-4}")
            eax_break = False
            inter.output(f"\t; init class fields")
            for field in inter.classes[self["class"]]["fields"]:
                if isinstance(inter.classes[self['class']]['fields'][field]["initval"],ast.Integer):
                    if eax_break:
                        inter.output(f"\tmov esi, dword [ebp-{inter.Vars[self['name']]['offset']}]")
                        inter.output(f"\tmov dword [esi+{inter.classes[self['class']]['fields'][field]['offset']}], dword {inter.classes[self['class']]['fields'][field]['initval']['value']}")
                    else:
                        inter.output(f"\tmov dword [eax+{inter.classes[self['class']]['fields'][field]['offset']}], dword {inter.classes[self['class']]['fields'][field]['initval']['value']}")
                else:
                    eax_break = True
                    field["initval"].eval()
                    inter.output(f"\tpop ecx")
                    inter.output(f"\tmov esi, dword [ebp-{inter.Vars[self['name']]['offset']}]")
                    inter.output(f"\tmov dword [esi+{inter.classes[self['class']]['fields'][field]['offset']}], ecx")

            if "__"+self["class"]+"__" in inter.classes[self['class']]["methods"]:
                inter.output(f"\t; __constructor__")
                ast.CallMethod({'obj':self["name"],'item':"__"+self["class"]+"__",'args': self["args"]}).eval()


    class GetField(YulaObject):
        def eval(self):
            obj = inter.Vars[self["obj"]["name"]]
            klass = None
            if "class" in obj:
                klass = inter.classes[obj["class"]]
            elif globals()["curclass"]:
                klass = inter.classes[globals()["curclass"]["name"]]
            else:
                klass = inter.classof(self["obj"]["name"])
            field = klass["fields"][self["item"]["name"]]
            self["obj"].eval()
            inter.output(f"\tpop ecx")
            inter.output(f"\tpush dword [ecx+{field['offset']}]")

    class CallMethod(YulaObject):
        def eval(self):
            ast.FuncCall({'name': self["item"],'args': self["args"],'obj': self["obj"]}).eval()

    class Cextern(YulaObject):
        def eval(self):
            if not self['func'] in inter.externed:
                inter.output(f"extern {self['func']}")
                inter.externed.append(self["func"])

    class FieldOf(YulaObject):
        def eval(self):
            ofs = inter.classes[self["class"]]["fields"][self["field"]]["offset"]
            self["ptr"].eval()
            inter.output(f"\tpop ecx")
            inter.output(f"\tpush dword [ecx+{ofs}] ; fieldof(ptr, '{self['field']}','{self['class']}')")

    class SetField(YulaObject):
        def eval(self):
            ofs = inter.classes[self["class"]]["fields"][self["field"]]["offset"]
            self["ptr"].eval()
            self["value"].eval()
            inter.output(f"\tpop edx")
            inter.output(f"\tpop ecx")
            inter.output(f"\tmov dword [ecx+{ofs}], edx ; setfield(ptr, value, '{self['field']}','{self['class']}')")

    class SetFieldAuto(YulaObject):
        def eval(self):
            name = self["name"]
            field = self["field"]
            ofs = inter.classof(name)["fields"][field]["offset"]
            klass = inter.Vars[name]["type"].split("[")[1].split("]")[0]
            ast.GetVar({'name': name}).eval()
            self["value"].eval()
            inter.output(f"\tpop edx")
            inter.output(f"\tpop ecx")
            inter.output(f"\tmov dword [ecx+{ofs}], edx ; setfield(ptr, value, '{field}','{klass}')")


class Inter(object):
    sizeswords = {'int32': "dword",'int16':"word","int8":"byte","string": "dword","int": "dword","void":"dword","char":"byte","ptr":"dword","bool":"dword"}
    sizes = {"int32": 4,"int16": 2,"int8":1,'int':4,"string": 4,"void": 4,"char": 1,"ptr":4,"bool":4}
    sizesreg = {"int32": "eax","int16":"ax","int8":"al","int":"eax","string":"eax","char":"al","ptr":"eax"}
    sizesregecx = {"int32": "ecx","int16":"cx","int8":"cl","int":"ecx","string":"ecx","char":"cl","ptr":"ecx","bool": "ecx"}
    sizesregebx = {"int32": "ebx","int16":"bx","int8":"bl","int":"ebx","string":"ebx","char":"bl","ptr":"ebx","bool": "ebx"}
    sizesregedi = {"int32": "edi","int16":"di","int8":"dil","int":"edi","string":"edi","char":"edi","ptr":"edi","bool":"edi"}
    sizesregedi = {"int32": "esi","int16":"si","int8":"sil","int":"esi","string":"esi","char":"esi","ptr":"esi","bool":"esi"}
    sizesregedx = {"int32": "edx","int16":"dx","int8":"dl","int":"edx","string":"edx","char":"dl","ptr":"edx","bool":"edx"}
    sizesreg = {"int32": "eax","int16":"ax","int8":"al","int":"eax","string":"eax","char":"eax","ptr":"eax","bool":"eax"}
    var_index = 8
    methods = {}
    classes = {}
    asms = {}
    code = ""
    bss = ""
    data = ""
    Vars = {}
    externed = []
    lab_index = 0
    strs = {r'%d': "numfmt",r'%s':"strfmt"}
    str_index = 0
    Functions = {}
    Consts = {}
    breaks = []
    callstack = []

    @cache
    def __init__(self):
        lg = LexerGenerator()
        lg.add("STRING",r"\"(\\.|[^\"\\])*\"")
        lg.add("CHAR",r"\'(\\.|[^\"\\])*\'")
        lg.add("NUMBER",r"-?\d+")
        lg.add("+",r"\+")
        lg.add("NL",r"\n")
        lg.add("{",r"\{")
        lg.add("}",r"\}")
        lg.add("->","->")
        lg.add(">",r"\>")
        lg.add("<",r"\<")
        lg.add("NOT","not")
        lg.add("==","==")
        lg.add("=",r"\=")
        lg.add("TYPE", r"type\[[a-zA-Z0-9]+\]")
        lg.add("TYPE", r"type\[[a-zA-Z0-9]\]")
        lg.add("[",r"\[")
        lg.add("]",r"\]")
        lg.add("CLASS","class")
        lg.add("OBJECT","object")
        lg.add("CONST","#def")
        lg.add("ATTR","__stdattr__")
        lg.add("INCLUDE",r"\#include")
        lg.add("BREAK","break")
        lg.add("CEXTERN","cextern")
        lg.add("LOCAL","local")
        lg.add("WHILE","while")
        lg.add("CALL",r"\$")
        lg.add("DEF","def")
        lg.add("FOF","fieldof")
        lg.add("FSET","FieldSet")
        lg.add("TYPE","int32")
        lg.add("TYPE","int")
        lg.add("TYPE","string")
        lg.add("TYPE", "void")
        lg.add("TYPE", "ptr")
        lg.add("TYPE", "bool")
        lg.add("ARRAY", "array")
        lg.add("FOR","for")
        lg.add("IF","if")
        lg.add("@","@")
        lg.add("ELSE","else")
        lg.add("ASM","__asm__")
        lg.add("GET",r"\%")
        lg.add("BOOL","true")
        lg.add("BOOL","false")
        lg.add(";",r"\;")
        lg.add("ADR",r"\&")
        lg.add(",",r"\,")
        lg.add("CASTP","__cast_p")
        lg.add("CAST","__s_cast")
        lg.add("FIELD","field")
        lg.add("RETURN","return")
        lg.add(":",r"\:")
        lg.add("-",r"\-")
        lg.add("/",r"\/")
        lg.add("*",r"\*")
        lg.add("(",r"\(")
        lg.add(")",r"\)")
        lg.add("CALL_METHOD",r"[a-zA-Z_][a-zA-Z0-9_]+\.[a-zA-Z_][a-zA-Z0-9_]+")
        lg.add("CALL_METHOD",r"[a-zA-Z0-9]\.[a-zA-Z_][a-zA-Z0-9_]+")
        lg.add("CALL_METHOD",r"[a-zA-Z_][a-zA-Z0-9_]+\.[a-zA-Z0-9]")
        lg.add("CALL_METHOD",r"[a-zA-Z0-9]\.[a-zA-Z0-9]")
        lg.add("ID",r"[a-zA-Z_][a-zA-Z0-9_]+")
        lg.add("ID",r"[a-zA-Z0-9]")
        lg.ignore(" ")
        lg.ignore("\t")
        self.Lexer = lg.build()
        pg = ParserGenerator(["STRING","NUMBER","+",
                            "-","/","*","(",")",
                            "{","ID","RETURN","NL","}",
                            "DEF","TYPE",
                            ",",":","ASM","=","GET",
                            "ADR","BOOL","IF","->","==","<",
                            ">","CALL",
                            "WHILE","[","]","CHAR",
                            "ELSE","BREAK",
                            "INCLUDE","ATTR","NOT","CONST","CASTP",
                            "ARRAY","FOR",";","CAST","OBJECT","CLASS",
                            "FIELD","CEXTERN","CALL_METHOD","FOF","FSET",
                            "@"
                            ],
        precedence=[
            ("left", ["{","}"]),
            ("nonassoc", ["NL"]),
            ("right", ["FOR"]),
            ("nonassoc", [";"]),
            ("right", ["ID"]),
            ("right", ["ATTR"]),
            ("left", ["ARRAY"]),
            ("left", ["TYPE","OBJECT","@"]),
            ("left", ["RETURN","FIELD"]),
            ("right", ["ASM","BREAK","CEXTERN","FSET"]),
            ("right", ["IF"]),
            ("right", ["ELSE"]),
            ("right", ["WHILE"]),
            ("left", ["CALL","CALL_METHOD"]),
            ("right", ["NOT"]),
            ("nonassoc", ["BOOL"]),
            ("left", ["=="]),
            ("right", ["CASTP"]),
            ("right", ["INCLUDE"]),
            ("right", ["CONST"]),
            ("right", ["DEF"]),
            ("right", ["CLASS"]),
            ("left", ["[","]"]),
            ("left", [",",":"]),
            ("left", ["+", "-"]),
            ("left", ["*", "/"]),
            ("right", ["CAST","->","FOF"]),
            ("right", ["GET","ADR"])
            ]
        )
        
        
        @pg.production("expr : NUMBER")
        def number_expr(p):
            return ast.Integer({'value': int(p[0].value)})

        @pg.production("expr : CHAR")
        def number_expr(p):
            return ast.Char({'value': p[0].value[1:-1]})

        @pg.production("expr : STRING")
        def string_expr(p):
            return ast.String({'value': p[0].value[1:-1]})

        @pg.production("expr : * * expr")
        def string_expr(p):
            return ast.GetP({'adr': p[2],'type': ""})

        @pg.production("expr : BOOL",precedence="BOOL")
        def bool_expr(p):
            return ast.Bool({'value': p[0].value})

        @pg.production("expr : NOT expr",precedence="NOT")
        def not_expr(p):
            return ast.Not({'condition': p[1]})

        @pg.production("expr : ID",precedence="GET")
        def getvar(p):
            return ast.GetVar({'name': p[0].value})

        @pg.production("expr : CAST < TYPE > expr",precedence="CAST")
        def cast_expr(p):
            return ast.S_cast({'type': p[2].value,'obj':p[4]}).eval()

        @pg.production("expr : CALL ID expr",precedence="CALL")
        def func_call_expr(p):
            if not isinstance(p[2],list):
                return ast.FuncCall({'name': p[1].value,'args': [p[2]]})
            return ast.FuncCall({'name': p[1].value,'args': p[2]})

        @pg.production("expr : ADR ID",precedence="ADR")
        def getvaradr(p):
            return ast.GetAdr({'name': p[1].value})

        @pg.production("expr : ( TYPE )",precedence="ADR")
        def noargs_expr(p):
            if not p[1].value == "void":
                inter.error("expression ( TYPE ) except void type")
            return []

        @pg.production("expr : ID [ expr ]",precedence="[")
        def getitem_expr(p):
            return ast.GetArrItem({'name':p[0].value,'index':p[2]})

        @pg.production("expr : ID [ expr ] = expr",precedence="[")
        def setitem_expr(p):
            return ast.SetArrItem({'name':p[0].value,'index':p[2],'value':p[5]})
            
        @pg.production("expr : ( expr )")
        def bracket_expr(p):
            return p[1]

        @pg.production("expr : CASTP expr",precedence="CASTP")
        def castp_expr(p):
            return ast.Ptr({'value': p[1]})

        @pg.production("expr : ID : TYPE",precedence=":")
        def annot_expr(p):
            return (p[0].value, p[2].value)

        @pg.production("expr : FOF expr",precedence="FOF")
        def field_of_expr(p):
            return ast.FieldOf({'ptr': p[1][0],'field':p[1][1]['value'],'class':p[1][2]['value']})

        @pg.production("expr : FSET expr",precedence="FOF")
        def field_set_expr(p):
            return ast.SetField({'ptr': p[1][0],'value': p[1][1],'field':p[1][2]['value'],'class':p[1][3]['value']})

        @pg.production("expr : @ CALL_METHOD = expr",precedence="@")
        def field_set_auto_expr(p):
            name = p[1].value.split(".")[0]
            field = p[1].value.split(".")[1]
            return ast.SetFieldAuto({'name': name,'value': p[3],'field':field})

        @pg.production("expr : expr , expr",precedence=",")
        def dot_expr(p):
            if isinstance(p[0],list):
                if isinstance(p[2],list):
                    return p[0] + p[2]
                else:
                    p[0].append(p[2])
                    return p[0]
            elif isinstance(p[2],list):
                if isinstance(p[0],list):
                    return p[2] + p[0]
                else:
                    p[2].append(p[0])
                    return p[2]
            else:
                return [p[0],p[2]]

        @pg.production("expr : expr ; expr ; expr",precedence=";")
        def dot_expr(p):
            return [p[0],p[2],p[4]]
        
        @pg.production("expr : expr / expr")
        @pg.production("expr : expr * expr")
        @pg.production("expr : expr - expr")
        @pg.production("expr : expr + expr")
        @pg.production("expr : expr == expr")
        @pg.production("expr : expr < expr")
        @pg.production("expr : expr > expr")
        def math_operations(p):
            one = p[0]
            two = p[2]
            res = 0
            op = p[1].value
            if isinstance(one,ast.Integer) and isinstance(two,ast.Integer):
                if op == "/":
                    res = str(eval(f'one["value"] // two["value"]'))
                else:
                    res = str(eval(f'one["value"] {op} two["value"]'))
                    if "." in res:
                        res = int(res.split(".")[0])
                    elif isinstance(eval(res),bool):
                        res = res
                    else:
                        res = int(res)
            if op == "+": return ast.Add(one, two, res)
            elif op == "-": return ast.Sub(one, two, res)
            elif op == "*": return ast.Mul(one, two, res)
            elif op == "/": return ast.Div(one, two, res)
            elif op == "==": return ast.Equal(one,two,res)
            elif op == "<": return ast.Less(one,two,res)
            elif op == ">": return ast.Above(one,two,res)

        @pg.production("expr : CEXTERN STRING",precedence="CEXTERN")
        def cextern_stmnt(p):
            return ast.Cextern({'func':p[1].value[1:-1]})

        @pg.production("expr : ATTR expr",precedence="ATTR")
        def attr_stmnt(p):
            return p[1]

        @pg.production("expr : FIELD ID = expr",precedence="FIELD")
        def field_decl(p):
            return ast.Field({'name': p[1].value,'initval': p[3]})

        @pg.production("expr : OBJECT ID GET ID expr",precedence="OBJECT")
        def create_obj_stmnt(p):
            if isinstance(p[4],list):
                return ast.Object({'name': p[1].value,'class': p[3].value,
                'args': p[4]})
            else:
                return ast.Object({'name': p[1].value,'class': p[3].value,
                'args': [p[4]]})

        @pg.production("expr : ARRAY TYPE [ expr ] ID",precedence="ARRAY")
        def array_create_stmnt(p):
            return ast.Array({'name': p[5].value,'type': p[1].value,
                'size': p[3]})

        @pg.production("expr : CONST ID = expr",precedence="CONST")
        def const_expr(p):
            return ast.Const({'name':p[1].value,'value': p[3]})

        @pg.production("expr : FOR expr { expr }",precedence="FOR")
        def for_stmnt(p):
            return ast.For({'init': p[1][0],'condition': p[1][1],
                'end': p[1][2],'block': p[3]})

        @pg.production("expr : CLASS ID { expr }",precedence="CLASS")
        def class_decl_stmnt(p):
            return ast.Class({'name': p[1].value,'block': p[3]})

        @pg.production("expr : expr -> expr ",precedence="->")
        def getclassitem(p):
            return ast.GetField({'obj': p[0],'item': p[2]})

        @pg.production("expr : CALL_METHOD expr",precedence="CALL_METHOD")
        def call_classmethod(p):
            obj = p[0].value.split(".")[0]
            m = p[0].value.split(".")[1]
            if isinstance(p[1],list):
                return ast.CallMethod({'obj': obj,'item': m,'args': p[1]})
            else:
                return ast.CallMethod({'obj': obj,'item': m,'args': [p[1]]})


        @pg.production("expr : DEF ID expr -> TYPE { expr }",precedence="DEF")
        def func_decl(p):
            if not isinstance(p[2],list):
                return ast.FuncDecl({'block': p[6],'type': p[4].value,
                                'args': [p[2]],'name': p[1].value})
            return ast.FuncDecl({'block': p[6],'type': p[4].value,
                                'args': p[2],'name': p[1].value})

        @pg.production("expr : INCLUDE CALL_METHOD",precedence="INCLUDE")
        def include_stmnt(p):
            return ast.Include({'file': p[1].value})

        @pg.production("expr : BREAK",precedence="BREAK")
        def break_stmnt(p):
            return ast.Break({})

        @pg.production("expr : expr + = expr",precedence="CALL")
        def inc_var_statement(p):
            return ast.Inc({'adr': p[0],'value': p[3]})

        @pg.production("expr : expr - = expr",precedence="CALL")
        def dec_var_statement(p):
            return ast.Dec({'adr': p[0],'value': p[3]})

        @pg.production("expr : IF expr { expr }",precedence="IF")
        def if_stmnt(p):
            return ast.If({'condition': p[1],'block': p[3],'else': None})

        @pg.production("expr : IF expr { expr } ELSE { expr }",precedence="ELSE")
        def if_stmnt(p):
            return ast.If({'condition': p[1],'block': p[3],'else': p[7]})

        @pg.production("expr : IF expr { expr } NL ELSE { expr }",precedence="IF")
        def if_stmnt(p):
            return ast.If({'condition': p[1],'block': p[3],'else': p[8]})

        @pg.production("expr : WHILE expr { expr }",precedence="WHILE")
        def while_stmnt(p):
            return ast.While({'condition': p[1],'block': p[3]})

        @pg.production("expr : ASM STRING",precedence="ASM")
        def asm_stmnt(p):
            return ast.Asm({'code': p[1].value[1:-1]})

        @pg.production("expr : TYPE ID = expr",precedence="TYPE")
        def decl_var(p):
            return ast.DeclareVar({'name': p[1].value,'type':p[0].value,'value': p[3]})

        @pg.production("expr : ID = expr",precedence="TYPE")
        def assign_var(p):
            return ast.AssignVar({'name': p[0].value,'value':p[2]})


        @pg.production("expr : RETURN expr",precedence="RETURN")
        def return_stmnt(p):
            return ast.Return({'value': p[1]})
            
                        
        @pg.production("expr : expr expr")
        def block_expr(p):
            if isinstance(p[1],ast.Statement):
                #print(p)
                 return p[0]
            elif isinstance(p[0],ast.Block) and isinstance(p[1],ast.Block):
                p[0].append(p[1])
                return p[0]
            elif isinstance(p[0],ast.Block):
                p[0].append(p[1])
                #print(p[0])
                return p[0]
            elif isinstance(p[1],ast.Block):
                p[1].append(p[0])
                #print(p[1])
                return p[1]
            else:
                b = ast.Block({})
                b.append(p[0])
                b.append(p[1])
                #print(b.get())
                return b
            
        @pg.production("expr : NL expr")
        def pass_expr(p):
            return p[1]
            
        @pg.production("expr : expr NL",precedence="NL")
        def parse_block(p):
            b = ast.Block({})
            b.append(p[0])
            return b
            
        self.Parser = pg.build()
        
        @pg.error
        def error(p):
            error("error at: "+str(p))
       
    def compare(self,code):
        res = ""
        for line in code.split("\n"):
            if not line.replace(" ","").replace("\t","") == "":
                res += line + "\n"

        arr2 = re.findall(r"\;[a-zA-Z0-9\<\>\\/\\\ \=\-\+\-\*\$\%\t\[\]\,\.\?\^\)\(\!\~\:\;\|]+\;",res)
        for c,i in enumerate(arr2):
            content = i.split(";")[1]
            res = res.replace(i,f";({content});")

        arr = re.findall(r"\#[a-zA-Z0-9_\/\\\ \t\+\-\*\[\]\.\,\?\^\)\(\!\~\:\;\|]+\#",res)
        for i in arr:
            res = res.replace(i,"")

        sn = SyntaxChecker(self.Lexer.lex(res))

        sn.check()

        return self.Parser.parse(self.Lexer.lex(res))

    def compare_lib(self,code,libname):
        res = ""
        for line in code.split("\n"):
            if not line.replace(" ","").replace("\t","") == "":
                res += line + "\n"

        arr2 = re.findall(r"\;[a-zA-Z0-9\<\>\\/\\\ \=\-\+\-\*\$\%\t\[\]\?\^\)\(\!\~\:\;\|]+\;",res)
        for c,i in enumerate(arr2):
            content = i.split(";")[1]
            res = res.replace(i,f";({content});")

        arr = re.findall(r"\#[a-zA-Z0-9_\/\\\ \t\+\-\*\[\]\.\,\?\^\)\(\!\~\:\;\|]+\#",res)
        for i in arr:
            res = res.replace(i,"")

        sn = SyntaxChecker(self.Lexer.lex(res),lib=libname)

        sn.check()

        return self.Parser.parse(self.Lexer.lex(res))

    def block_has(self,block):
        res = {}
        for el in block.get():
            if isinstance(el,ast.Statement):
                tmp = self.block_has(el.get_block())
                for i in tmp:
                    res[i] = tmp[i]
            elif isinstance(el,ast.DeclareVar):
                res[el["name"]] = inter.sizes[el["type"]]
            elif isinstance(el,ast.Array):
                res[el["name"]] = el["size"]["value"]*inter.sizes[el["type"]]
            elif isinstance(el,ast.Object):
                res[el["name"]] = 4
        return res

    def output(self,value):
        self.code += value + "\n"

    def init_text(self):
        self.code += r"""section .text

global main

"""

    def init_data(self):
        self.code += "\nsection .data\n" + self.data

    def init_bss(self):
        if not self.bss == "":
            self.code += "\nsection .bss\n" + self.bss

    def _add_data(self, val):
        self.data += val + "\n"

    def _add_bss(self, val):
        self.bss += val + "\n"

    def compile(self,filename,args):
        linkeds = ""
        linked_list = ["stdhl"]
        comp_options = None
        for i in linked_list:
            linkeds += f"libs_o/{i}.o "
        if args.output:
            comp_options = (f"NASM/nasm.exe --gprefix _ -f win32 ./{filename} -o ./out.o",
                        f"MinGW/bin/gcc.exe ./out.o {linkeds}-o ./{args.output} -m32")
        else:
            comp_options = (f"NASM/nasm.exe --gprefix _ -f win32 ./{filename} -o ./out.o",
                            f"MinGW/bin/gcc.exe ./out.o {linkeds}-o ./a.exe -m32")
        for el in comp_options:
            subprocess.run(el)
        if not args.asm:
            os.remove("output.asm")
        os.remove("out.o")
        print("compiled")

    def save_asm(self):
        open("output.asm","w").write(self.code)

    def error(self,err):
        fname = globals()["curfunc"]
        ftype = self.Functions[fname]["type"]
        res = f"in    def {ftype} {fname}(...):\n"
        res += "\t" + err + "\n"
        print(res)
        sys.exit(0)

    def classof(self,varname):
        return self.classes[self.Vars[varname]["type"].split("[")[1].split("]")[0]]


inter = Inter()

prs = argparse.ArgumentParser(prog="helloLang")
prs.add_argument("filename")
prs.add_argument("-o","--output")
prs.add_argument("-a","--asm",action="store_true")

inter.init_text()
prog = inter.compare(open(prs.parse_args().filename,"r").read())
prog.eval()
inter._add_data('\t' + r'numfmt: db "%d",0')
inter._add_data('\t' + r'charfmt: db "%c",0')
inter._add_data('\t' + r'strfmt: db "%s",0')
inter._add_data('\t' + r'newline: db 10,0')
inter.init_data()
inter.init_bss()

inter.save_asm()
inter.compile("output.asm",prs.parse_args())

sys.exit(0)
