
# coder : Floyda
# date  : 2016-12-7

DEBUG = False

# ----------------------------------------------------------
# Const
# ----------------------------------------------------------
class TagType():
    BRACKET_CHUNK = 0
    
class NodeType():
    WORD            = 0
    BLANK           = 1
    OPERATOR_BOTH   = 2
    OPERATOR_AFTER  = 3
    EQUAL           = 4
    BRACKET         = 5
    REVERSE_BRACKET = 6
    ENTER           = 7
    STRING          = 8
    COMMENT_SINGLE  = 9
    COMMENT_MULTI   = 10

NodePattern = {
    NodeType.WORD            : [],
    NodeType.BLANK           : [' '],
    NodeType.OPERATOR_BOTH   : ['+', '-', '*', '/', '^'],
    NodeType.OPERATOR_AFTER  : [','],
    NodeType.EQUAL           : ['=', '~'],
    NodeType.BRACKET         : ['(', '{', '['],
    NodeType.REVERSE_BRACKET : [')', '}', ']'],
    NodeType.ENTER           : ['\n'],
    NodeType.STRING          : [],
    NodeType.COMMENT_SINGLE  : [],
    NodeType.COMMENT_MULTI   : [],
}

CommentTypeList = [
    NodeType.STRING,
    NodeType.COMMENT_SINGLE,
    NodeType.COMMENT_MULTI
]

IndentKeyword = [
    'function',
    'for',
    'repeat',
    'while',
    'if',
    # 'else',
    # 'elseif'
]

UnindentKeyword = [
    'end',
    'until'
]

# ----------------------------------------------------------
# Line
# ----------------------------------------------------------
debug_Index = 0
_lines = []

class Line():
    def __init__(self):
        self._nodes = []
        self._indent = 0

    def __str__(self):
        s = ''
        for node in self._nodes: 
            s += str(node)
        return s

    def concat(self, node):
        if DEBUG:
            global debug_Index
            debug_Index += 1
            print('[id]:%d' % debug_Index, str(node), '[type]:%d' % node.get_type())
        if len(self._nodes) == 0 and node.get_type() == NodeType.BLANK:
            return
        last_node = self._nodes[-1:]
        if len(last_node) > 0:
            last_node = last_node[0]
            if last_node.get_type() == node.get_type() == NodeType.BLANK:
                return

        self._nodes.append(node)

    def get_nodes(self):
        return self._nodes

    def set_indent(self, indent):
        self._indent = indent

    def get_indent(self):
        return self._indent


def create_line():
    line = Line()
    _lines.append(line)
    return line

def foreach_line():
    def is_comment(node):
        return node.get_type() in CommentTypeList

    indent = 0
    for line in _lines:
        line.set_indent(indent)
        for node in line.get_nodes():
            if str(node) == 'else' or str(node) == 'elseif':
                line.set_indent(indent - 1)
            else:
                if is_comment(node) is False and str(node) in IndentKeyword:
                    indent += 1
                if is_comment(node) is False and str(node) in UnindentKeyword:
                    indent -= 1
                    line.set_indent(indent)

    result = ''
    for line in _lines:
        result += ' ' * 4 * line.get_indent() + str(line)
    return result

# ----------------------------------------------------------
# Node
# ----------------------------------------------------------
_nodes = []

class Node():
    def __init__(self, char='', ctype=0):
        self._str = char
        self._ctype = ctype
        self._tag = []

    def __str__(self):
        if self._str == ' ': return ' '
        return self._str.strip(' ')

    def set_type(self, ctype=''):
        self._ctype = ctype

    def get_type(self):
        return self._ctype

    def set_tag(self, tag):
        self._tag.append(tag)

    def get_tag(self):
        return self._tag

    def concat(self, c):
        if self._str == c == ' ': return
        self._str += c


def create_node(c, ctype):
    node = Node(c, ctype)
    _nodes.append(node)
    return node

def create_node_blank():
    return create_node(' ', NodeType.BLANK)

def foreach_node():
    line = create_line()
    index = 0
    while index < len(_nodes):
        node = _nodes[index]
        last_node = None
        if index - 1 >= 0:
            last_node = _nodes[index - 1]

        # w: word
        # b: blank
        def deal_node_bwb():
            if last_node.get_type() != NodeType.BLANK:
                blank_node = create_node_blank()
                line.concat(blank_node)
            line.concat(node)
            blank_node = create_node_blank()
            line.concat(blank_node)

        def deal_node_wb():
            line.concat(node)
            blank_node = create_node_blank()
            line.concat(blank_node)

        def deal_node_ws():
            blank_node = create_node_blank()
            line.concat(blank_node)
            line.concat(node)

        ntype = node.get_type()

        if ntype is NodeType.WORD:
            line.concat(node)
        elif ntype is NodeType.BLANK:
            line.concat(node)
        elif ntype is NodeType.OPERATOR_BOTH:
            deal_node_bwb()
        elif ntype is NodeType.OPERATOR_AFTER:
            deal_node_wb()
        elif ntype is NodeType.EQUAL:
            deal_node_bwb()
        elif ntype is NodeType.BRACKET:
            line.concat(node)
        elif ntype is NodeType.REVERSE_BRACKET:
            line.concat(node)
        elif ntype is NodeType.ENTER:
            line.concat(node)
            line = create_line()
        elif ntype is NodeType.STRING:
            if last_node and last_node.get_type() == NodeType.WORD:
                deal_node_ws()
            else:
                line.concat(node)
        elif ntype is NodeType.COMMENT_SINGLE:
            line.concat(node)
        elif ntype is NodeType.COMMENT_MULTI:
            line.concat(node)

        index += 1

# ----------------------------------------------------------
# Comment
# ----------------------------------------------------------
COMMENT_SINGLE_PRIORITY = 4
COMMENT_MULTI_PRIORITY = 2
STRING_SINGLE_PRIORITY = 1
STRING_DOUBLE_PRIORITY = 1

string_flag_single  = False
string_flag_double  = False
comment_flag_single = False
comment_flag_multi  = False

def is_comment_status():
    return string_flag_single or string_flag_double or comment_flag_single or comment_flag_multi

def check_comment(node, c):
    def _check_string(pattern, flag):
        if comment_flag_single or comment_flag_multi : return
        global node
        if flag:
            if c == pattern:
                flag = False
            else:
                node.concat(c)
        else:
            if c == pattern:
                node = create_node(c, NodeType.STRING)
                flag = True
        return flag

    def check_string():
        global string_flag_single
        global string_flag_double
        string_flag_single = _check_string("'", string_flag_single)
        string_flag_double = _check_string('"', string_flag_double)
        return string_flag_single or string_flag_double

    def check_comment_single():
        global comment_flag_single
        if comment_flag_single:
            if c == '\n':
                comment_flag_single = False
            else:
                node.concat(c)
        elif c == '-' and str(node)[-1:] == '-':
            node.concat(c)
            node.set_type(NodeType.COMMENT_SINGLE)
            comment_flag_single = True
        return comment_flag_single

    def check_comment_multi():
        global comment_flag_multi
        global comment_flag_single
        if c == ']' and str(node)[-1:] == ']':
            comment_flag_multi = False
        if comment_flag_multi:
            node.concat(c)
        elif c == '[' and str(node)[-3:] == '--[':
            node.concat(c)
            node.set_type(NodeType.COMMENT_MULTI)
            comment_flag_single = False
            comment_flag_multi = True
        return comment_flag_multi

    flag = False
    flag = flag or check_string()
    flag = flag or check_comment_multi()
    flag = flag or check_comment_single()

    return flag, node

# ----------------------------------------------------------
# Char
# ----------------------------------------------------------
def foreach_char(node, c):
    ctype = 0
    for i in range(len(NodePattern)):
        pattern = NodePattern[i]
        if c in pattern:
            ctype = i
            break
    else:
        ctype = NodeType.WORD

    while True:
        if not node:
            node = create_node(c, ctype)
            break

        flag, node = check_comment(node, c)
        if flag:
            break
        if ctype == node.get_type():
            node.concat(c)
            break

        node = create_node(c, ctype)
        break

    return node

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
def purge():
    global _lines
    global _nodes
    _lines = []
    _nodes = []

def format(content):
    purge()
    node = None
    for c in content:
        if c != '\t':
            node = foreach_char(node, c)
    foreach_node()
    return foreach_line()

# Debug
if __name__ == '__main__':
    content = """
.
    """
    print(format(content))
