import datetime

from django.db.models import Q


# Token types
AND, OR, LPAREN, RPAREN, EXPRESSION, EOF = (
    'AND', 'OR', '(', ')', 'EXPR', 'EOF'
)
EQ, NE = ('eq', 'ne')
OPERATORS = [EQ, NE, "gt", "gte", "lt", "lte"]


class ParsingException(Exception):
    pass


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


class Lexer:
    """This class performs lexical analysis on a search expression.
    It breaks the expression into tokens that will be further evaluated by
    the parser.
    """
    def __init__(self, text):
        self.pos = 0
        self.tokens = self.tokenize(text)
        self.current_token = self.tokens[self.pos]

    def error(self):
        raise ParsingException('Invalid character')

    @staticmethod
    def tokenize(expr):
        """Creates a list of tokens from the input expression.
        Tokens are: "(", ")", "AND", "OR", EXPRESSIONS
        EXPRESSIONS: $field_name $operator $value
        
        Example
        -------
        input: ((date lt 2020-03-20) AND city eq budapest) OR (time gte 600)
        output: ["(", "(", "date lt 2020-03-20", ")", "AND",
                 "city eq budapest", ")", "OR", "(", "time", 'gte', "600"]
        """
        if not expr:
            return []
        tokens = []
        pos = 0
        len_expr = len(expr)
        curr_char = expr[pos]

        while pos < len_expr:
            curr_char = expr[pos]
            if curr_char in [LPAREN, RPAREN]:
                tokens.append(curr_char)
                pos += 1
                continue
            elif curr_char == ' ':
                pos += 1
                # Skip empty chars.
                continue
            else:
                word = curr_char
                pos += 1
                while pos < len_expr and expr[pos] not in [LPAREN, RPAREN]:
                    word = "{}{}".format(word, expr[pos])
                    pos += 1

                # Make sure to further split by AND and OR tokens.
                word_list = word.strip().split(" ")
                word = ''
                for curr in word_list:
                    if curr.upper() in [AND, OR]:
                        if word:
                            tokens.append(word)
                        tokens.append(curr)
                        word = ""
                        continue
                    if not word:
                        word = curr
                    else:
                        word = "{} {}".format(word, curr)
                if word:
                    tokens.append(word)

        return tokens

    def advance(self):
        """Moves the current position index into the tokens list."""
        self.pos += 1
        if self.pos >= len(self.tokens):
            self.current_token = None  # Indicates end of input
        else:
            self.current_token = self.tokens[self.pos]

    def expression(self):
        expr = self.current_token
        self.advance()
        return expr

    def get_next_token(self):
        while self.current_token is not None:
            if self.current_token.upper() == AND:
                self.advance()
                return Token(AND, '&')
            elif self.current_token.upper() == OR:
                self.advance()
                return Token(OR, '|')
            elif self.current_token.lower() == LPAREN:
                self.advance()
                return Token(LPAREN, '(')
            elif self.current_token.lower() == RPAREN:
                self.advance()
                return Token(RPAREN, ')')
            else:
                return Token(EXPRESSION, self.expression())

        return Token(EOF, None)


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST:
    pass


class BinOp(AST):
    """Class that defines AND and OR operations."""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class LookupExpression(AST):
    """Class that defines a simple expression.

    The supported format is: $field_name $operator $value
    Example: date eq 2020-04-17 , time gte 300
    Supported Operators: eq, ne, lte, lt, gte, gt

    Raises
    ------
    ParsingException if the format is not recognized.
    """
    def __init__(self, token, allowed_fields):
        self.token = token
        expr = token.value
        tokens = expr.split(" ")
        if len(tokens) != 3:
            raise ParsingException("Invalid expression: {}".format(expr))

        self.field, self.op, self.value = tokens[0], tokens[1].lower(), tokens[2]
        if self.op not in OPERATORS:
            raise ParsingException(
                "Operator not supported: {}"
                .format(self.op))

        if self.field not in allowed_fields:
            raise ParsingException(
                "Search field not supported: {}"
                .format(self.field))

        field_type = allowed_fields[self.field]
        if field_type == datetime.date:
            try:
                self.value = datetime.datetime.strptime(
                    self.value, "%Y-%m-%d").date()
            except ValueError as e:
                raise ParsingException(
                    "Invalid date format {}. Supported format is yyyy-mm-dd."
                    .format(self.value))
        else:
            try:
                self.value = field_type(self.value)
            except ValueError as e:
                raise ParsingException(
                    "Invalid value {} for field {}. Type must be {}."
                    .format(self.value, self.field, field_type))


class Parser:
    """ Builds AST from tokens(lexer) that helps finding the precedence of the
    operators.
    """
    def __init__(self, lexer, allowed_fields):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.allowed_fields = allowed_fields

    def error(self):
        raise ParsingException('Invalid syntax')

    def eat(self, token_type):
        """Advances the current token if the previous one is the assumed one."""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def term(self):
        """Term format : LookupExpression | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == EXPRESSION:
            self.eat(EXPRESSION)
            return LookupExpression(token, self.allowed_fields)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    def expr(self):
        """Expr format: term ((AND | OR) term)* """
        node = self.term()

        while self.current_token.type in [AND, OR]:
            token = self.current_token
            if token.type == AND:
                self.eat(AND)
            elif token.type == OR:
                self.eat(OR)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()


###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise ParsingException('No visit_{} method'.format(type(node).__name__))


class QueryFilterBuilder(NodeVisitor):
    """Creates a django ORM query filter from a string expression, by viziting
    expression's AST (Parser output tree).
    """
    def __init__(self, tree):
        self.tree = tree

    def visit_BinOp(self, node):
        if node.op.type == AND:
            return (self.visit(node.left) & self.visit(node.right))
        elif node.op.type == OR:
            return (self.visit(node.left) | self.visit(node.right))

    def visit_LookupExpression(self, node):
        field = node.field
        if node.op not in [EQ, NE]:
            field = "{}__{}".format(field, node.op)

        args = {field: node.value}
        if node.op == NE:
            return ~Q(**args)
        return Q(**args)

    def build(self):
        return self.visit(self.tree)


def parse_search(filter_expr, allowed_fields):
    """Transforms a search string expression into a django query filter object.

    Parameters
    ----------
    filter_expr (str): expression to be parsed.
    allowed_fields (dict): dictionary with the allowed fields and their type.
                           If the expression contains a field that is not
                           allowed, the function raises a ParsingException
                           exception.
    Example
    --------
    input: (date eq 2016-05-01) OR ((distance gte 5000) AND  (distance lte 10000))
    output: Q(date='2016-05-01') | (Q(distance__gte=5000) & Q(distance__lte=10000))
    """
    if not filter_expr or not filter_expr.strip() or not allowed_fields:
        return None

    lexer = Lexer(filter_expr)
    parser = Parser(lexer, allowed_fields)
    data_node = parser.parse()

    qf_builder = QueryFilterBuilder(data_node)
    return qf_builder.build()
