"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        self.tokenizer = input_stream
        self.vm_writer = VMWriter(output_stream)
        self.symbol_table = SymbolTable()
        self.current_class = ""
        self.label_counter = 0
        self.tokenizer.advance()

    # -------------------------
    # Helpers
    # -------------------------

    def _get_segment(self, kind: str) -> str:
        """Translates SymbolTable kinds to VM segments."""
        if not kind:
            return "NONE"
        kind = kind.upper()
        if kind == "VAR": return "LOCAL"
        if kind == "ARG": return "ARG"
        if kind == "FIELD": return "THIS"
        if kind == "STATIC": return "STATIC"
        return "NONE"

    def _generate_label(self, prefix: str) -> str:
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label

    # -------------------------
    # CLASS
    # -------------------------

    def compile_class(self) -> None:
        self.tokenizer.advance()  # class
        self.current_class = self.tokenizer.identifier()
        self.tokenizer.advance()  # className
        self.tokenizer.advance()  # {

        while self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ("STATIC", "FIELD"):
            self.compile_class_var_dec()

        while self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ("CONSTRUCTOR", "FUNCTION", "METHOD"):
            self.compile_subroutine()

        self.tokenizer.advance()  # }

    # -------------------------
    # VAR DECL
    # -------------------------

    def compile_class_var_dec(self) -> None:
        kind = self.tokenizer.keyword().upper()  # STATIC or FIELD
        self.tokenizer.advance()

        if self.tokenizer.token_type() == "IDENTIFIER":
            v_type = self.tokenizer.identifier()
        else:
            v_type = self.tokenizer.keyword().lower()
        self.tokenizer.advance()  # type

        v_name = self.tokenizer.identifier()
        self.symbol_table.define(v_name, v_type, kind)
        self.tokenizer.advance()  # varName

        while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
            self.tokenizer.advance()  # ,
            v_name = self.tokenizer.identifier()
            self.symbol_table.define(v_name, v_type, kind)
            self.tokenizer.advance()  # varName

        self.tokenizer.advance()  # ;

    def compile_var_dec(self) -> None:
        self.tokenizer.advance()  # var

        if self.tokenizer.token_type() == "IDENTIFIER":
            v_type = self.tokenizer.identifier()
        else:
            v_type = self.tokenizer.keyword().lower()
        self.tokenizer.advance()  # type

        v_name = self.tokenizer.identifier()
        self.symbol_table.define(v_name, v_type, "VAR")
        self.tokenizer.advance()  # varName

        while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
            self.tokenizer.advance()  # ,
            v_name = self.tokenizer.identifier()
            self.symbol_table.define(v_name, v_type, "VAR")
            self.tokenizer.advance()  # varName

        self.tokenizer.advance()  # ;

    # -------------------------
    # SUBROUTINES
    # -------------------------

    def compile_subroutine(self) -> None:
        self.symbol_table.start_subroutine()

        func_type = self.tokenizer.keyword().upper()
        self.tokenizer.advance()  # constructor/function/method

        if func_type == "METHOD":
            self.symbol_table.define("this", self.current_class, "ARG")

        self.tokenizer.advance()  # void/type

        func_name = self.tokenizer.identifier()
        self.tokenizer.advance()  # subroutineName

        self.tokenizer.advance()  # (
        self.compile_parameter_list()
        self.tokenizer.advance()  # )
        
        self.compile_subroutine_body(func_name, func_type)

    def compile_subroutine_body(self, func_name: str, func_type: str):
        self.tokenizer.advance()  # {

        while self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "VAR":
            self.compile_var_dec()

        # Write VM function declaration now that we know the number of local variables
        n_locals = self.symbol_table.var_count("VAR")
        self.vm_writer.write_function(f"{self.current_class}.{func_name}", n_locals)

        # Set up 'this' pointer
        if func_type == "METHOD":
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)
        elif func_type == "CONSTRUCTOR":
            n_fields = self.symbol_table.var_count("FIELD")
            self.vm_writer.write_push("CONST", n_fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)

        self.compile_statements()
        self.tokenizer.advance()  # }

    def compile_parameter_list(self):
        if not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")"):
            if self.tokenizer.token_type() == "IDENTIFIER":
                v_type = self.tokenizer.identifier()
            else:
                v_type = self.tokenizer.keyword().lower()
            self.tokenizer.advance()  # type

            v_name = self.tokenizer.identifier()
            self.symbol_table.define(v_name, v_type, "ARG")
            self.tokenizer.advance()  # varName

            while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.tokenizer.advance()  # ,

                if self.tokenizer.token_type() == "IDENTIFIER":
                    v_type = self.tokenizer.identifier()
                else:
                    v_type = self.tokenizer.keyword().lower()
                self.tokenizer.advance()  # type

                v_name = self.tokenizer.identifier()
                self.symbol_table.define(v_name, v_type, "ARG")
                self.tokenizer.advance()  # varName

    # -------------------------
    # STATEMENTS
    # -------------------------

    def compile_statements(self):
        while self.tokenizer.token_type() == "KEYWORD":
            kw = self.tokenizer.keyword()
            if kw == "LET":
                self.compile_let()
            elif kw == "IF":
                self.compile_if()
            elif kw == "WHILE":
                self.compile_while()
            elif kw == "DO":
                self.compile_do()
            elif kw == "RETURN":
                self.compile_return()
            else:
                break

    def compile_do(self):
        self.tokenizer.advance()  # do
        self._compile_subroutine_call()
        self.tokenizer.advance()  # ;
        self.vm_writer.write_pop("TEMP", 0)  # Discard return value

    def compile_let(self):
        self.tokenizer.advance()  # let
        var_name = self.tokenizer.identifier()
        self.tokenizer.advance()  # varName
        
        kind = self.symbol_table.kind_of(var_name)
        index = self.symbol_table.index_of(var_name)
        segment = self._get_segment(kind)
        
        is_array = False
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
            is_array = True
            self.tokenizer.advance()  # [
            self.compile_expression()
            self.tokenizer.advance()  # ]
            
            # Array index calculation
            self.vm_writer.write_push(segment, index)
            self.vm_writer.write_arithmetic("ADD")

        self.tokenizer.advance()  # =
        self.compile_expression()
        self.tokenizer.advance()  # ;
        
        if is_array:
            # Pop value to TEMP 0, pop address to POINTER 1, push TEMP 0 to THAT 0
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            self.vm_writer.write_pop(segment, index)

    def compile_while(self):
        label_exp = self._generate_label("WHILE_EXP")
        label_end = self._generate_label("WHILE_END")

        self.vm_writer.write_label(label_exp)
        self.tokenizer.advance()  # while
        self.tokenizer.advance()  # (
        self.compile_expression()
        self.tokenizer.advance()  # )

        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(label_end)

        self.tokenizer.advance()  # {
        self.compile_statements()
        self.tokenizer.advance()  # }

        self.vm_writer.write_goto(label_exp)
        self.vm_writer.write_label(label_end)

    def compile_return(self):
        self.tokenizer.advance()  # return

        if not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ";"):
            self.compile_expression()
        else:
            self.vm_writer.write_push("CONST", 0)  # void functions return 0

        self.tokenizer.advance()  # ;
        self.vm_writer.write_return()

    def compile_if(self):
        label_true = self._generate_label("IF_TRUE")
        label_false = self._generate_label("IF_FALSE")
        label_end = self._generate_label("IF_END")

        self.tokenizer.advance()  # if
        self.tokenizer.advance()  # (
        self.compile_expression()
        self.tokenizer.advance()  # )

        self.vm_writer.write_if(label_true)
        self.vm_writer.write_goto(label_false)

        self.vm_writer.write_label(label_true)
        self.tokenizer.advance()  # {
        self.compile_statements()
        self.tokenizer.advance()  # }

        if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "ELSE":
            self.vm_writer.write_goto(label_end)
            self.vm_writer.write_label(label_false)
            self.tokenizer.advance()  # else
            self.tokenizer.advance()  # {
            self.compile_statements()
            self.tokenizer.advance()  # }
            self.vm_writer.write_label(label_end)
        else:
            self.vm_writer.write_label(label_false)

    # -------------------------
    # EXPRESSIONS
    # -------------------------

    def compile_expression(self):
        self.compile_term()

        while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in "+-*/&|<>=":
            op = self.tokenizer.symbol()
            self.tokenizer.advance()  # operator
            self.compile_term()
            
            if op == '+': self.vm_writer.write_arithmetic("ADD")
            elif op == '-': self.vm_writer.write_arithmetic("SUB")
            elif op == '*': self.vm_writer.write_call("Math.multiply", 2)
            elif op == '/': self.vm_writer.write_call("Math.divide", 2)
            elif op == '&': self.vm_writer.write_arithmetic("AND")
            elif op == '|': self.vm_writer.write_arithmetic("OR")
            elif op == '<': self.vm_writer.write_arithmetic("LT")
            elif op == '>': self.vm_writer.write_arithmetic("GT")
            elif op == '=': self.vm_writer.write_arithmetic("EQ")

    def compile_term(self):
        ttype = self.tokenizer.token_type()

        if ttype == "INT_CONST":
            self.vm_writer.write_push("CONST", self.tokenizer.int_val())
            self.tokenizer.advance()

        elif ttype == "STRING_CONST":
            val = self.tokenizer.string_val()
            self.vm_writer.write_push("CONST", len(val))
            self.vm_writer.write_call("String.new", 1)
            for char in val:
                self.vm_writer.write_push("CONST", ord(char))
                self.vm_writer.write_call("String.appendChar", 2)
            self.tokenizer.advance()

        elif ttype == "KEYWORD":
            kw = self.tokenizer.keyword()
            if kw == "TRUE":
                self.vm_writer.write_push("CONST", 1)
                self.vm_writer.write_arithmetic("NEG")  # True is -1
            elif kw in ("FALSE", "NULL"):
                self.vm_writer.write_push("CONST", 0)
            elif kw == "THIS":
                self.vm_writer.write_push("POINTER", 0)
            self.tokenizer.advance()

        elif ttype == "SYMBOL":
            sym = self.tokenizer.symbol()
            if sym == "(":
                self.tokenizer.advance()  # (
                self.compile_expression()
                self.tokenizer.advance()  # )
            elif sym in ("-", "~", "^", "#"):
                self.tokenizer.advance()  # unary operator
                self.compile_term()
                if sym == '-': self.vm_writer.write_arithmetic("NEG")
                elif sym in ('~', '^'): self.vm_writer.write_arithmetic("NOT")
                # '#' might be specific shift extension in some versions of course

        elif ttype == "IDENTIFIER":
            # Peek ahead to see if it's an array or a subroutine call
            name = self.tokenizer.identifier()
            self.tokenizer.advance()
            
            if self.tokenizer.token_type() == "SYMBOL":
                sym = self.tokenizer.symbol()
                
                if sym == "[": 
                    self.tokenizer.advance()  # [
                    self.compile_expression()
                    self.tokenizer.advance()  # ]
                    
                    kind = self.symbol_table.kind_of(name)
                    index = self.symbol_table.index_of(name)
                    self.vm_writer.write_push(self._get_segment(kind), index)
                    self.vm_writer.write_arithmetic("ADD")
                    self.vm_writer.write_pop("POINTER", 1)
                    self.vm_writer.write_push("THAT", 0)
                    
                elif sym in (".", "("):
                    # It's a subroutine call, we need to backtrack or handle inline
                    # To keep it clean without true backtracking, we pass the parsed name
                    self._compile_subroutine_call_tail(name, sym)
                else:
                    # Just a simple variable
                    kind = self.symbol_table.kind_of(name)
                    index = self.symbol_table.index_of(name)
                    self.vm_writer.write_push(self._get_segment(kind), index)
            else:
                # Just a simple variable
                kind = self.symbol_table.kind_of(name)
                index = self.symbol_table.index_of(name)
                self.vm_writer.write_push(self._get_segment(kind), index)

    def compile_expression_list(self) -> int:
        n_args = 0
        if not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")"):
            self.compile_expression()
            n_args += 1

            while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.tokenizer.advance()  # ,
                self.compile_expression()
                n_args += 1
                
        return n_args

    # -------------------------
    # Helper for subroutine calls (used in DO and TERM)
    # -------------------------
    
    def _compile_subroutine_call(self):
        first_name = self.tokenizer.identifier()
        self.tokenizer.advance()
        sym = self.tokenizer.symbol()
        self._compile_subroutine_call_tail(first_name, sym)

    def _compile_subroutine_call_tail(self, first_name: str, sym: str):
        if sym == "(":
            # Method call on the current object: funcName(args)
            self.tokenizer.advance()  # (
            self.vm_writer.write_push("POINTER", 0)  # push 'this'
            n_args = self.compile_expression_list()
            self.tokenizer.advance()  # )
            self.vm_writer.write_call(f"{self.current_class}.{first_name}", n_args + 1)
            
        elif sym == ".":
            # Method or function call: objName.funcName(args) or ClassName.funcName(args)
            self.tokenizer.advance()  # .
            method_name = self.tokenizer.identifier()
            self.tokenizer.advance()  # funcName
            self.tokenizer.advance()  # (
            
            kind = self.symbol_table.kind_of(first_name)
            if kind:
                # It's an instance, push it as the first argument
                index = self.symbol_table.index_of(first_name)
                self.vm_writer.write_push(self._get_segment(kind), index)
                
                obj_type = self.symbol_table.type_of(first_name)
                n_args = self.compile_expression_list()
                self.tokenizer.advance()  # )
                self.vm_writer.write_call(f"{obj_type}.{method_name}", n_args + 1)
            else:
                # It's a class (Static function or Constructor)
                n_args = self.compile_expression_list()
                self.tokenizer.advance()  # )
                self.vm_writer.write_call(f"{first_name}.{method_name}", n_args)