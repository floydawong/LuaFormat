# -*- coding:utf-8 -*-

_node_entry = None
_lines = []
_setting = {}


# ----------------------------------------------------------
# Const
# ----------------------------------------------------------
class NodeType:
    WORD = 0
    BLANK = 1
    OPERATOR = 2
    SEPARATOR = 3
    EQUAL = 4
    BRACKET = 5
    REVERSE_BRACKET = 6
    ENTER = 7
    STRING = 8
    COMMENT_SINGLE = 9
    COMMENT_MULTI = 10


NodePattern = {
    NodeType.WORD: [],
    NodeType.BLANK: [' '],
    NodeType.OPERATOR: ['+', '-', '*', '/', '^', '%'],
    NodeType.SEPARATOR: [','],
    NodeType.EQUAL: ['=', '~', '>', '<'],
    NodeType.BRACKET: ['(', '{', '['],
    NodeType.REVERSE_BRACKET: [')', '}', ']'],
    NodeType.ENTER: ['\r\n', '\n', '\r'],
    NodeType.STRING: ['"', "'"],
    NodeType.COMMENT_SINGLE: [],
    NodeType.COMMENT_MULTI: [],
}

CommentType = [
    NodeType.STRING, NodeType.COMMENT_SINGLE, NodeType.COMMENT_MULTI
]

IndentKeyword = [
    'function',
    'for',
    'repeat',
    'while',
    'if',
]

UnindentKeyword = ['end', 'until']


# ----------------------------------------------------------
# Line
# ----------------------------------------------------------
class Line():
    def __init__(self):
        self._nodes = []
        self._indent = 0

    def __str__(self):
        r = ''
        for node in self._nodes:
            r += str(node)
        return ' ' * _settings.get('tab_size') * self._indent + r.strip(' ')

    def add(self, node):
        self._nodes.append(node)

    def get_nodes(self):
        return self._nodes

    def set_indent(self, indent):
        self._indent = indent

    def get_indent(self):
        return self._indent

    def add_indent(self, indent):
        self._indent += indent


def create_line():
    line = Line()
    _lines.append(line)
    return line


# ----------------------------------------------------------
# Node
# ----------------------------------------------------------
class NodeIterator():
    def __init__(self):
        self.node = _node_entry

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if not self.node:
            raise StopIteration()
        node = self.node
        self.node = self.node.next
        return node


class Node():
    def __init__(self, c):
        self._str = c

    def __str__(self):
        if self.type is NodeType.BLANK:
            return ' '
        if self.type in CommentType:
            return self._str
        elif self._str == '\t':
            return ' '
        return self._str.strip(' ')

    def add(self, c):
        if self.type is NodeType.STRING:
            if c == '\n':
                self._str += '\\n'
                return
            if c == '\t':
                self._str += ' '
                return
        self._str += c

    def make_property(attr):
        def set_attr():
            def inner(self, value):
                setattr(self, "_" + attr, value)

            return inner

        def get_attr():
            def inner(self):
                try:
                    return getattr(self, "_" + attr)
                except:
                    return None

            return inner

        return property(get_attr(), set_attr())

    type = make_property("type")
    prev = make_property("prev")
    next = make_property("next")
    del make_property


def create_node(c, ctype):
    node = Node(c)
    node.type = ctype
    return node


def insert_blank_node(node):
    bn = create_node(' ', NodeType.BLANK)
    bn.prev = node.prev
    bn.next = node
    node.prev.next = bn
    node.prev = bn


def merge_prev_node(node):
    if not node.prev: return
    lnode = node.prev
    lnode.add(str(node))

    if node.next:
        node.next.prev = lnode
        lnode.next = node.next
    else:
        lnode.next = None
    del node
    return lnode


def delete_node(node):
    if node.prev and node.next:
        node.prev.next = node.next
        node.next.prev = node.prev
    elif node.next == None:
        node.prev.next = None
    elif node.prev == None:
        node.next.prev = None
    return node.next


def delete_forward_blank(node):
    while True:
        if node and node.type == NodeType.BLANK:
            node = delete_node(node)
        else:
            return
        node = node.prev


def delete_backward_blank(node):
    while True:
        if node and node.type == NodeType.BLANK:
            node = delete_node(node)
        else:
            return


def get_forward_char(node, count):
    r = ''
    while True:
        if not node: return r[::-1]
        r += str(node)[::-1]
        if len(r) >= count: return r[::-1][-count:]
        node = node.prev


def get_forward_type(node):
    pnode = node.prev
    if pnode:
        return pnode.type
    return None


def get_forward_type_for_negative(node):
    while True:
        if node is None: return None
        if node.type == NodeType.BLANK:
            node = node.prev
            continue
        return node.type


# ----------------------------------------------------------
# Format
# ----------------------------------------------------------
def get_char_type(c):
    for i in range(len(NodePattern)):
        pattern = NodePattern[i]
        if c in pattern:
            return i
    return NodeType.WORD


def foreach_char(content):
    global _node_entry
    prev_node = None

    for c in content:
        ctype = get_char_type(c)
        node = create_node(c, ctype)

        if prev_node:
            if c == '-':
                # negative number
                # 负号
                pntype = get_forward_type_for_negative(prev_node)
                if pntype != NodeType.WORD and pntype != NodeType.REVERSE_BRACKET:
                    node.type = NodeType.WORD

                # scientific notation
                # 科学计数法
                if str(prev_node)[-1].lower() == 'e' and str(
                        prev_node.prev)[-1] in [str(x) for x in range(10)]:
                    node.type = NodeType.WORD

            prev_node.next = node
            node.prev = prev_node
        else:
            _node_entry = node

        prev_node = node


def foreach_node():
    current_type = None
    string_key = ''

    for node in NodeIterator():
        char = str(node)

        # Check String Finish
        if current_type == NodeType.STRING:
            merge_prev_node(node)
            if string_key == char:
                current_type = None
                string_key = ''
            elif get_forward_char(node, 2) == ']]' and string_key == '[[':
                current_type = None
                string_key = ''

        # Check Comment Single Finish
        elif current_type == NodeType.COMMENT_SINGLE:
            if node.type == NodeType.ENTER:
                current_type = None
                string_key = ''
            elif get_forward_char(node, 4) == '--[[':
                current_type = NodeType.COMMENT_MULTI
                string_key = ''
                node = merge_prev_node(node)
                node.type = NodeType.COMMENT_MULTI
            else:
                merge_prev_node(node)

        # Check Comment Multi Finish
        elif current_type == NodeType.COMMENT_MULTI:
            node = merge_prev_node(node)
            if get_forward_char(node, 2) == ']]':
                current_type = None
                string_key = ''

        # Check String Or Comment Begin.
        elif current_type == None:
            if node.type == NodeType.STRING:
                current_type = NodeType.STRING
                string_key = char
            elif get_forward_char(node, 2) == '--':
                current_type = NodeType.COMMENT_SINGLE
                string_key = ''
                node = merge_prev_node(node)
                node.type = NodeType.COMMENT_SINGLE
            elif get_forward_char(node, 2) == '[[':
                current_type = NodeType.STRING
                string_key = '[['


def foreach_blank():
    for node in NodeIterator():
        if node.prev and node.type == node.prev.type == NodeType.BLANK:
            merge_prev_node(node)


def foreach_string_connect():
    for node in NodeIterator():
        if get_forward_char(node, 2) == '..' and \
        get_forward_char(node, 3) != '...' and \
        str(node.next) != '.' :
            node = merge_prev_node(node)
            node.type = NodeType.OPERATOR


def foreach_operator():
    for node in NodeIterator():
        if node.type == NodeType.OPERATOR:
            if _settings.get('special_symbol_split'):
                if node.prev.type is not NodeType.BLANK:
                    insert_blank_node(node)
                if node.next.type is not NodeType.BLANK:
                    insert_blank_node(node.next)


def foreach_separator():
    for node in NodeIterator():
        if node.type == NodeType.SEPARATOR:
            delete_forward_blank(node.prev)
            delete_backward_blank(node.next)
            if _settings.get('special_symbol_split'):
                if node.next.type is not NodeType.BLANK:
                    insert_blank_node(node.next)


def foreach_equal():
    for node in NodeIterator():
        if node.type == NodeType.EQUAL:
            if node.prev and node.prev.type is NodeType.EQUAL:
                merge_prev_node(node)

    for node in NodeIterator():
        if node.type == NodeType.EQUAL:
            delete_forward_blank(node.prev)
            delete_backward_blank(node.next)
            if _settings.get('special_symbol_split'):
                if node.prev.type is not NodeType.BLANK:
                    insert_blank_node(node)
                if node.next.type is not NodeType.BLANK:
                    insert_blank_node(node.next)


def foreach_bracket():
    for node in NodeIterator():
        if node.type == NodeType.BRACKET:
            delete_backward_blank(node.next)
            if _settings.get('bracket_split'):
                insert_blank_node(node.next)

        if node.type == NodeType.REVERSE_BRACKET:
            delete_forward_blank(node.prev)
            if _settings.get('bracket_split'):
                insert_blank_node(node)





def foreach_word():
    for node in NodeIterator():
        if node.prev and node.prev.type == node.type == NodeType.WORD:
            merge_prev_node(node)


def tidy_indent():
    global line_indent
    global indent
    line_indent = 0
    indent = 0
    line = create_line()
    line_key_dict = {}
    bracket_key_dict = {}

    def deal_indent(line, delta=0):
        line.set_indent(indent + delta)

    def inc_indent(delta):
        global line_indent
        global indent
        if line_indent + delta > 1:
            return
        if line_indent + delta < -1:
            return
        line_indent += delta
        indent += delta
        if indent < 0:
            indent = 0

    for node in NodeIterator():
        line.add(node)
        key = str(node)

        line_key_dict[key] = line_key_dict.get(key, 0) + 1
        if node.type is NodeType.BRACKET or node.type is NodeType.REVERSE_BRACKET:
            bracket_key_dict[key] = bracket_key_dict.get(key, 0) + 1

        if node.type is NodeType.ENTER:
            inc_indent(1 if line_key_dict.get('(', 0) > line_key_dict.get(
                ')', 0) else 0)
            inc_indent(1 if line_key_dict.get('{', 0) > line_key_dict.get(
                '}', 0) else 0)
            inc_indent(1 if line_key_dict.get('[', 0) > line_key_dict.get(
                ']', 0) else 0)

            if line_key_dict.get('(', 0) < line_key_dict.get(')', 0):
                inc_indent(-1)
                deal_indent(line)
            if line_key_dict.get('{', 0) < line_key_dict.get('}', 0):
                inc_indent(-1)
                deal_indent(line)
            if line_key_dict.get('[', 0) < line_key_dict.get(']', 0):
                inc_indent(-1)
                deal_indent(line)

            if line_key_dict.get('do') == line_key_dict.get('end') == 1:
                indent += 1
                deal_indent(line)
                line = create_line()
            else:
                line = create_line()
                deal_indent(line)
            line_indent = 0
            line_key_dict = {}

        if str(node) == 'else' or str(node) == 'elseif':
            deal_indent(line, -1)

        if str(node) in IndentKeyword:
            inc_indent(1)

        if str(node) in UnindentKeyword:
            inc_indent(-1)
            deal_indent(line)


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
def purge():
    global _node_entry
    global _lines
    global _settings
    _node_entry = None
    _lines = []
    _settings = {}


def _lua_format(content, setting=None):
    purge()
    global _settings
    _settings = setting

    # deal content
    content = content.replace('\t', '')
    content += '\n'

    foreach_char(content)
    foreach_node()

    foreach_blank()
    foreach_string_connect()
    foreach_word()
    foreach_operator()
    foreach_separator()
    foreach_equal()
    foreach_bracket()

    tidy_indent()


# return a string
def lua_format(content, settings):
    _lua_format(content, settings)
    r = ''
    for line in _lines:
        r += str(line)
    r = r[:-1]
    return r


# return a list of string for CudeText.
def lua_format_by_cudatext(content,
                           tab_size=4,
                           separator_exclude=True,
                           operator_exclude=True,
                           bracket_exclude=False):
    settings = {}
    settings['tab_size'] = tab_size
    settings['special_symbol_split'] = separator_exclude
    settings['bracket_split'] = bracket_exclude

    _lua_format(content, settings)

    r = []
    for line in _lines:
        r.append[line]
    return r
