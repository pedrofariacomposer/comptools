"""
Module containing the LisParser class and its methods.
This class was found here: https://stackoverflow.com/a/58219006/11621264
"""


class LisParser:
    """class expecting a lisp program to recursively walk through."""

    def __init__(self, prog):
        self.program = prog
        self.sub_program_sep = "("
        self.program_stack = self._tokenize_program()
        self.atom_is_int = self._is_int
        self.atom_is_flt = self._is_flt
        self.recursive_unpack = self.recursive_unpack

    def _tokenize_program(self):
        """func that splits a lisp program on white spaces ensuring parentheses tokenisation."""

        # if accidental multiple spaces, join method collapses them before padding parentheses before and after.
        tokens = " ".join(self.program.split()).replace('(', ' ( ').replace(')', ' ) ')

        # user might have inputted lisp program as python string i.e. "program". If so, get rid of double quotes.
        return (self.program.startswith('"')
                and tokens.split()[1:-1]
                or tokens.split())

    @staticmethod
    def _walk_stack(stack):
        """func returning the popped element at index 0 of the stack."""
        return stack.pop(0)

    @staticmethod
    def _is_flt(atom):
        """func trying to turn an atom to an float, else throws error."""
        try:
            float(atom)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_int(atom):
        """func trying to turn an atom to an int, else throws error."""
        try:
            int(atom)
            return True
        except ValueError:
            return False

    def _to_py_type(self, atom):
        """func that trying to an atom to an int, then a float and finally a string."""
        return ((self.atom_is_int(atom) and int(atom)) or
                (self.atom_is_flt(atom) and float(atom)) or
                str(atom))

    def recursive_unpack(self):

        # _walk_stack pops the first element off the stack.
        stack_head = self._walk_stack(stack=self.program_stack)

        # if token is an atom, convert to python type.
        if stack_head != self.sub_program_sep:
            return self._to_py_type(atom=stack_head)

        # "(" starts a sub_program, needs to be in its own unit (list).
        # The nested lists will represent the ast of the lisp program.
        elif stack_head == self.sub_program_sep:
            ast = list()

            # recursion base case is the end of the sub_program with ")".
            while self.program_stack[0] != ")":
                ast.append(self.recursive_unpack())

            else:
                # remove the closing parent, so that walk_atom() will return the atom, not the closing paren.
                self.program_stack.remove(")")

            return ast



