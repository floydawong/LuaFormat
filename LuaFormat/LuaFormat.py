# -*- coding:utf-8 -*-
# ----------------------------------------------------------
# Coder : Floyda
# Date  : 2016-12-8
# ----------------------------------------------------------

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
    WORD            = 0
    BLANK           = 1
    OPERATOR        = 2
    SEPARATOR       = 3
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
    NodeType.OPERATOR        : ['+', '-', '*', '/', '^'],
    NodeType.SEPARATOR       : [','],
    NodeType.EQUAL           : ['=', '~', '>', '<'],
    NodeType.BRACKET         : ['(', '{', '['],
    NodeType.REVERSE_BRACKET : [')', '}', ']'],
    NodeType.ENTER           : ['\r\n', '\n', '\r'],
    NodeType.STRING          : ['"', "'"],
    NodeType.COMMENT_SINGLE  : [],
    NodeType.COMMENT_MULTI   : [],
}

CommentType = [
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
]

UnindentKeyword = [
    'end',
    'until'
]

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
class IterNode():
    """ Node迭代器 """

    def __init__(self, node):
        self.node = node

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if not self.node :
            raise StopIteration()
        node = self.node
        self.node = self.node.next
        return node


class Node():
    def __init__(self, c):
        self._str = c

    def __str__(self):
        if self.type is NodeType.BLANK :
            return ' '
        if self.type in CommentType :
            return self._str
        elif self._str == '\t':
            return ' ' * SETTING_TAB_SIZE
        return self._str.strip(' ')

    def add(self, c):
        if self.type is NodeType.STRING :
            if c == '\n' : self._str += '\\n'; return
            # if c == '\t' : self._str += '\\t'; return
            if c == '\t' : self._str += ' ' * SETTING_TAB_SIZE; return
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
    last = make_property("last")
    next = make_property("next")
    del make_property


def create_node(c, ctype):
    node = Node(c)
    node.type = ctype
    return node


def insert_blank_node(node):
    bn = create_node(' ', NodeType.BLANK)
    bn.last = node.last
    bn.next = node
    node.last.next = bn
    node.last = bn


def merge_last_node(node):
    if not node.last : return
    lnode = node.last
    lnode.add(str(node))

    if node.next :
        node.next.last = lnode
        lnode.next = node.next
    else:
        lnode.next = None
    del node
    return lnode


def string_forward_blank(node):
    while True:
        if node.last == None or node.last.type == NodeType.ENTER:
            return
        if node.last.type != NodeType.BLANK:
            return
        node = merge_last_node(node)
        node.type = NodeType.COMMENT_SINGLE


def get_forward_node(node, count):
    r = ''
    while True:
        if not node : return r[::-1]
        r += str(node)[::-1]
        if len(r) >= count: return r[::-1][-count:]
        node = node.last

# ----------------------------------------------------------
# Format
# ----------------------------------------------------------
def deal_char(content):
    global _node_entry
    last_node = None

    for c in content :
        ctype = 0
        for i in range(len(NodePattern)):
            pattern = NodePattern[i]
            if c in pattern:
                ctype = i
                break
        else:
            ctype = NodeType.WORD

        node = create_node(c, ctype)
        if not _node_entry :
            _node_entry = node
        if last_node :
            last_node.next = node
            node.last = last_node
        last_node = node


def foreach_string():
    string_tag = []

    def create_tag(node):
        string_tag.append(str(node))

    def remove_tag():
        string_tag.pop()

    for node in IterNode(_node_entry):
        if len(string_tag) > 0 :
            merge_last_node(node)

        if str(node) in NodePattern[NodeType.STRING]:
            current_tag = string_tag[-1:]
            while True:
                if len(current_tag) == 0 :
                    create_tag(node)
                    break
                current_tag = current_tag[0]
                if current_tag == str(node) :
                    remove_tag()
                    break
                create_tag(node)
                break


def foreach_string_connect():
    """ 处理字符串连接符 '..' """
    for node in IterNode(_node_entry) :
        if get_forward_node(node, 2) == '..' and \
        get_forward_node(node, 3) != '...' and \
        str(node.next) != '.' :
            node = merge_last_node(node)
            node.type = NodeType.OPERATOR


def foreach_comment_multi():
    comment_flag = False
    for node in IterNode(_node_entry) :
        if get_forward_node(node, 2) == ']]' :
            comment_flag = False
            merge_last_node(node)

        if comment_flag:
            merge_last_node(node)

        if get_forward_node(node, 4) == '--[[' :
            comment_flag = True
            node = merge_last_node(node)
            node = merge_last_node(node)
            node = merge_last_node(node)
            node.type = NodeType.COMMENT_MULTI


def foreach_comment_single():
    comment_flag = False
    for node in IterNode(_node_entry) :
        if node.type == NodeType.ENTER and comment_flag == True:
            comment_flag = False

        if comment_flag:
            merge_last_node(node)

        # 不是第一个Node
        # 前一个Node不是'-'
        # 不是多行注释里的一部分
        # 和前面一个Node加起来正好是'--'
        if node.last != None and \
         node.last.type != NodeType.COMMENT_SINGLE and \
         node.type != NodeType.COMMENT_MULTI and \
         get_forward_node(node, 2) == '--' :

            comment_flag = True
            node = merge_last_node(node)
            node.type = NodeType.COMMENT_SINGLE
            string_forward_blank(node)


def foreach_operator():
    for node in IterNode(_node_entry):
        if node.type == NodeType.OPERATOR :
            if SETTING_OPERATOR_EXCLUDE :
                if node.last.type is not NodeType.BLANK :
                    insert_blank_node(node)
                if node.next.type is not NodeType.BLANK :
                    insert_blank_node(node.next)


def foreach_separator():
    for node in IterNode(_node_entry):
        if node.type == NodeType.SEPARATOR :
            if SETTING_SEPARATOR_EXCLUDE :
                if node.next.type is not NodeType.BLANK :
                    insert_blank_node(node.next)


def foreach_equal():
    for node in IterNode(_node_entry):
        if node.type == NodeType.EQUAL :
            if node.last and node.last.type is NodeType.EQUAL:
                merge_last_node(node)

    for node in IterNode(_node_entry):
        if node.type == NodeType.EQUAL :
            if SETTING_OPERATOR_EXCLUDE :
                if node.last.type is not NodeType.BLANK :
                    insert_blank_node(node)
                if node.next.type is not NodeType.BLANK :
                    insert_blank_node(node.next)


def foreach_bracket():
    for node in IterNode(_node_entry):
        if SETTING_BRACKET_EXCLUDE :
            if node.type == NodeType.BRACKET :
                    if not node.next.type in [NodeType.BLANK, NodeType.REVERSE_BRACKET]:
                        insert_blank_node(node.next)
            if node.type == NodeType.REVERSE_BRACKET :
                    if not node.last.type in [NodeType.BLANK, NodeType.BRACKET]:
                        insert_blank_node(node)


def foreach_word():
    for node in IterNode(_node_entry) :
        if node.last and node.last.type == node.type == NodeType.WORD :
            merge_last_node(node)


def foreach_enter():
    indent = 0
    line = create_line()
    keywordDict = {}

    def deal_indent(line, delta=0):
        line.set_indent(indent + delta)

    for node in IterNode(_node_entry):
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
        if delta > 0 :
            indent += 1
        deal_indent(line)
        delta = 0
        for node in line.get_nodes():
            if node.type is NodeType.BRACKET :
                delta += 1
            if node.type is NodeType.REVERSE_BRACKET :
                delta -= 1
        if delta < 0 :
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


def format(content):
    purge()
    deal_char(content)
    foreach_string()
    foreach_comment_multi()
    foreach_comment_single()
    foreach_string_connect()

    foreach_word()
    foreach_operator()
    foreach_separator()
    foreach_equal()
    foreach_bracket()
    foreach_enter()
    foreach_chunk()

    r = ''
    for line in _lines:
        r += str(line)
    return r

# ----------------------------------------------------------
# Debug
# ----------------------------------------------------------
content = """
"""
# print(format(content))
