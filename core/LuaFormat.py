# -*- coding:utf-8 -*-

_node_entry = None
_lines = []

# ----------------------------------------------------------
# Setting
# ----------------------------------------------------------
SETTING_TAB_SIZE = 4
SETTING_SEPARATOR_EXCLUDE = True
SETTING_OPERATOR_EXCLUDE = True
SETTING_BRACKET_EXCLUDE = False


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
        return ' ' * SETTING_TAB_SIZE * self._indent + r.strip(' ')

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


def string_forward_blank(node):
    while True:
        if node.prev == None or node.prev.type == NodeType.ENTER:
            return
        if node.prev.type != NodeType.BLANK:
            return
        node = merge_prev_node(node)
        node.type = NodeType.COMMENT_SINGLE


def get_forward_node(node, count):
    r = ''
    while True:
        if not node: return r[::-1]
        r += str(node)[::-1]
        if len(r) >= count: return r[::-1][-count:]
        node = node.prev


# ----------------------------------------------------------
# Format
# ----------------------------------------------------------
def deal_char(content):
    global _node_entry
    prev_node = None

    for c in content:
        ctype = 0
        for i in range(len(NodePattern)):
            pattern = NodePattern[i]
            if c in pattern:
                ctype = i
                break
        else:
            ctype = NodeType.WORD

        node = create_node(c, ctype)
        if not _node_entry:
            _node_entry = node
        if prev_node:
            prev_node.next = node
            node.prev = prev_node
        prev_node = node


def foreach_string():
    string_tag = []

    def create_tag(node):
        string_tag.append(str(node))

    def remove_tag():
        string_tag.pop()

    for node in NodeIterator():
        if node.type == NodeType.COMMENT_MULTI or node.type == NodeType.COMMENT_SINGLE:
            break

        if len(string_tag) > 0:
            merge_prev_node(node)

        if str(node) in NodePattern[NodeType.STRING]:
            current_tag = string_tag[-1:]
            while True:
                if len(current_tag) == 0:
                    create_tag(node)
                    break
                current_tag = current_tag[0]
                if current_tag == str(node):
                    remove_tag()
                    break
                create_tag(node)
                break


def foreach_string_connect():
    for node in NodeIterator():
        if get_forward_node(node, 2) == '..' and \
        get_forward_node(node, 3) != '...' and \
        str(node.next) != '.' :
            node = merge_prev_node(node)
            node.type = NodeType.OPERATOR


def foreach_comment_multi():
    comment_flag = False
    for node in NodeIterator():
        if comment_flag == True and get_forward_node(node, 2) == ']]':
            comment_flag = False
            merge_prev_node(node)

        if comment_flag:
            merge_prev_node(node)

        if get_forward_node(node, 4) == '--[[':
            comment_flag = True
            node = merge_prev_node(node)
            node = merge_prev_node(node)
            node = merge_prev_node(node)
            node.type = NodeType.COMMENT_MULTI


def foreach_comment_single():
    comment_flag = False
    for node in NodeIterator():
        if node.type == NodeType.ENTER and comment_flag == True:
            comment_flag = False

        if comment_flag:
            merge_prev_node(node)

        if node.prev != None and \
         node.prev.type != NodeType.COMMENT_SINGLE and \
         node.type != NodeType.COMMENT_MULTI and \
         get_forward_node(node, 2) == '--' :

            comment_flag = True
            node = merge_prev_node(node)
            node.type = NodeType.COMMENT_SINGLE
            string_forward_blank(node)


def foreach_operator():
    for node in NodeIterator():
        if node.type == NodeType.OPERATOR:
            if SETTING_OPERATOR_EXCLUDE:
                if node.prev.type is not NodeType.BLANK:
                    insert_blank_node(node)
                if node.next.type is not NodeType.BLANK:
                    insert_blank_node(node.next)


def foreach_separator():
    for node in NodeIterator():
        if node.type == NodeType.SEPARATOR:
            if SETTING_SEPARATOR_EXCLUDE:
                if node.next.type is not NodeType.BLANK:
                    insert_blank_node(node.next)


def foreach_equal():
    for node in NodeIterator():
        if node.type == NodeType.EQUAL:
            if node.prev and node.prev.type is NodeType.EQUAL:
                merge_prev_node(node)

    for node in NodeIterator():
        if node.type == NodeType.EQUAL:
            if SETTING_OPERATOR_EXCLUDE:
                if node.prev.type is not NodeType.BLANK:
                    insert_blank_node(node)
                if node.next.type is not NodeType.BLANK:
                    insert_blank_node(node.next)


def foreach_bracket():
    for node in NodeIterator():
        if SETTING_BRACKET_EXCLUDE:
            if node.type == NodeType.BRACKET:
                if not node.next.type in [
                        NodeType.BLANK, NodeType.REVERSE_BRACKET
                ]:
                    insert_blank_node(node.next)
            if node.type == NodeType.REVERSE_BRACKET:
                if not node.prev.type in [NodeType.BLANK, NodeType.BRACKET]:
                    insert_blank_node(node)


def foreach_word():
    for node in NodeIterator():
        if node.prev and node.prev.type == node.type == NodeType.WORD:
            merge_prev_node(node)


def foreach_enter():
    indent = 0
    line = create_line()
    keywordDict = {}

    def deal_indent(line, delta=0):
        line.set_indent(indent + delta)

    for node in NodeIterator():
        line.add(node)
        keywordDict[str(node)] = keywordDict.get(str(node), 0)
        keywordDict[str(node)] += 1

        if node.type is NodeType.ENTER:
            if keywordDict.get('do') == keywordDict.get('end') == 1:
                indent += 1
                deal_indent(line)
                line = create_line()
            else:
                line = create_line()
                deal_indent(line)
            keywordDict = {}
        if str(node) == 'else' or str(node) == 'elseif':
            deal_indent(line, -1)
        if str(node) in IndentKeyword:
            indent += 1
        if str(node) in UnindentKeyword:
            indent -= 1
            deal_indent(line)


def foreach_chunk():
    indent = 0
    delta = 0

    def deal_indent(line):
        line.add_indent(indent)

    for line in _lines:
        if delta > 0:
            indent += 1
        deal_indent(line)
        delta = 0
        for node in line.get_nodes():
            if node.type is NodeType.BRACKET:
                delta += 1
            if node.type is NodeType.REVERSE_BRACKET:
                delta -= 1
        if delta < 0:
            indent -= 2
            deal_indent(line)
            indent += 1


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
def purge():
    global _node_entry
    global _lines
    _node_entry = None
    _lines = []


def _lua_format(content,
               tab_size=4,
               separator_exclude=True,
               operator_exclude=True,
               bracket_exclude=False):

    # init format setting
    global SETTING_TAB_SIZE
    global SETTING_SEPARATOR_EXCLUDE
    global SETTING_OPERATOR_EXCLUDE
    global SETTING_BRACKET_EXCLUDE

    SETTING_TAB_SIZE = tab_size
    SETTING_SEPARATOR_EXCLUDE = separator_exclude
    SETTING_OPERATOR_EXCLUDE = operator_exclude
    SETTING_BRACKET_EXCLUDE = bracket_exclude

    # deal content
    content = content.replace('\t', '')
    purge()
    deal_char(content)
    # foreach_string()
    foreach_comment_multi()
    foreach_comment_single()
    foreach_string_connect()
    foreach_word()
    foreach_string()
    foreach_operator()
    foreach_separator()
    foreach_equal()
    foreach_bracket()
    foreach_enter()
    foreach_chunk()

# return a string by default
def lua_format(content,
               tab_size=4,
               separator_exclude=True,
               operator_exclude=True,
               bracket_exclude=False):

    _lua_format(content, tab_size, separator_exclude, operator_exclude, bracket_exclude)
    r = ''
    for line in _lines:
        r += str(line)
    return r

# return a list of string for CudeText.
def lua_format_by_cudatext(content,
               tab_size=4,
               separator_exclude=True,
               operator_exclude=True,
               bracket_exclude=False):

    _lua_format(content, tab_size, separator_exclude, operator_exclude, bracket_exclude)
    r = []
    for line in _lines:
        r.append[line]
    return r
