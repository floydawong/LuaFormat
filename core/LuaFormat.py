# -*- coding:utf-8 -*-

_start_node = None
_end_node = None

_lines = []
_setting = {}


# ----------------------------------------------------------
# Const
# ----------------------------------------------------------
class NodeType:
    WORD = 'WORD'
    BLANK = 'BLANK'
    OPERATOR = 'OPERATOR'
    SEPARATOR = 'SEPARATOR'
    EQUAL = 'EQUAL'
    BRACKET = 'BRACKET'
    REVERSE_BRACKET = 'REVERSE_BRACKET'
    ENTER = 'ENTER'
    STRING = 'STRING'
    COMMENT_SINGLE = 'COMMENT_SINGLE'
    COMMENT_MULTI = 'COMMENT_MULTI'


NodePattern = {
    'WORD': [],
    'BLANK': [' '],
    'OPERATOR': ['+', '-', '*', '/', '^', '%'],
    'SEPARATOR': [',', ';'],
    'EQUAL': ['=', '~', '>', '<'],
    'BRACKET': ['(', '{', '['],
    'REVERSE_BRACKET': [')', '}', ']'],
    'ENTER': ['\r\n', '\n', '\r'],
    'STRING': ['"', "'"],
    'COMMENT_SINGLE': [],
    'COMMENT_MULTI': [],
}

SingletonType = [
    NodeType.BRACKET, NodeType.REVERSE_BRACKET, NodeType.STRING, NodeType.BLANK
]

CommentType = [
    NodeType.STRING, NodeType.COMMENT_SINGLE, NodeType.COMMENT_MULTI
]

IndentKeyword = [
    'function',
    'for',
    'repeat',
    'while',
    'if',
    'do',
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
        enter_pos = r.find('\n')
        r = r[:enter_pos].strip(' ') + r[enter_pos:]
        if r.strip(' ') == '\n': return '\n' #20
        return ' ' * _settings.get('tab_size') * self._indent + r

    def is_blank_line(self):
        for node in self._nodes:
            if node.type not in [NodeType.BLANK, NodeType.ENTER]:
                return False
        return True

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
        self.node = _start_node

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
            r = self._str
            r = r.replace(r'\\n', r'\n')
            r = r.replace(r'\\r', r'\r')
            return r
        return self._str.strip(' ')

    def add(self, c):
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


def create_node(content, type=None):
    global _start_node
    global _end_node

    node = Node(content)
    node.type = type

    if _start_node is None:
        _start_node = node

    if _end_node:
        node.last = _end_node
        _end_node.next = node

    _end_node = node
    return node


def insert_blank_node(node):
    bn = Node(' ')
    bn.type = NodeType.BLANK
    bn.last = node.last
    bn.next = node
    node.last.next = bn
    node.last = bn


def merge_prev_node(node):
    if not node.last: return node
    lnode = node.last
    lnode.add(str(node))

    if node.next:
        node.next.last = lnode
        lnode.next = node.next
    else:
        lnode.next = None
    del node
    return lnode


def delete_node(node):
    if node.last and node.next:
        node.last.next = node.next
        node.next.last = node.last
    elif node.next == None:
        node.last.next = None
    elif node.last == None:
        node.next.last = None
    return node.next


def delete_forward_blank(node):
    while True:
        node = node.last
        if node and node.type == NodeType.BLANK:
            node = delete_node(node)
        else:
            return


def delete_backward_blank(node):
    while True:
        node = node.next
        if node and node.type == NodeType.BLANK:
            node = delete_node(node)
            node = node.last
        else:
            return


def get_forward_char(node, count):
    r = ''
    while True:
        if not node: return r[::-1]
        r += str(node)[::-1]
        if len(r) >= count: return r[::-1][-count:]
        node = node.last


def get_forward_type(node):
    pnode = node.last
    if pnode:
        return pnode.type
    return None


def get_forward_type_for_negative(node):
    while True:
        node = node.last
        if node is None: return None
        if node.type != NodeType.BLANK:
            return node.type


# ----------------------------------------------------------
# Format
# ----------------------------------------------------------
def split_content(content, count=1):
    return content[:count], content[count:]


def get_char_type(c):
    for key in NodePattern:
        pattern = NodePattern[key]
        if c in pattern:
            return key
    return NodeType.WORD


def parse_node(content):
    node = None
    while content:
        c, content = split_content(content)
        ctype = get_char_type(c)
        if node is None:
            node = create_node(c, ctype)
            continue

        if ctype == node.type and not ctype in SingletonType:
            node.add(c)
        else:
            node = create_node(c, ctype)


def foreach_node():
    node = _start_node

    while node:
        if node.type == NodeType.STRING:
            char_key = str(node)
            while True:
                node = node.next
                if char_key == str(node) and get_forward_char(node,
                                                              2)[0] != '\\':
                    merge_prev_node(node)
                    break
                if not node.next:
                    break
                merge_prev_node(node)
        str_node = str(node)
        if str_node == len(str_node) * '=' and str(node.last) == '[' and str(
                node.next) == '[':
            end_flag = ']%s]' % (len(str_node) * '=')

            node = merge_prev_node(node)
            node.type = NodeType.COMMENT_SINGLE

            while True:
                node = node.next
                merge_prev_node(node)
                if get_forward_char(node, len(end_flag)) == end_flag:
                    break
                if not node.next:
                    break

        if get_forward_char(node, 2) == '[[':
            node = merge_prev_node(node)
            node.type = NodeType.STRING
            while True:
                node = node.next
                node.type = NodeType.STRING
                if get_forward_char(node, 2) == ']]':
                    node = merge_prev_node(node)
                    break
                merge_prev_node(node)
                if not node.next:
                    break
        if get_forward_char(node, 2) == '--':
            # COMMENT_SINGLE
            # node = merge_prev_node(node)
            node.type = NodeType.COMMENT_SINGLE
            while True:
                node = node.next
                if node.type == NodeType.ENTER:
                    break
                if not node.next:
                    break
                tmp = merge_prev_node(node)
                str_tmp = str(tmp)
                check_flag = '--[%s[' % ((len(str_tmp) - 4) * '=')
                end_flag = ']%s]' % ((len(str_tmp) - 4) * '=')

                if str(tmp) == check_flag:
                    node = tmp
                    # node.type == NodeType.COMMENT_MULTI
                    while True:
                        node = node.next
                        if get_forward_char(node, len(end_flag)) == end_flag:
                            merge_prev_node(node)
                            break
                        merge_prev_node(node)
                        if not node.next:
                            break
                    break

        node = node.next


def foreach_blank():
    for node in NodeIterator():
        if node.last and node.type == node.last.type == NodeType.BLANK:
            merge_prev_node(node)


def foreach_string_connect():
    for node in NodeIterator():
        if str(node) == '..':
            node.type = NodeType.OPERATOR


def foreach_operator():
    for node in NodeIterator():
        if str(node) == '-':
            # scientific notation
            # 科学计数法
            if node.last and str(node.last)[-1].lower() == 'e' and str(
                    node.last)[-2] in [str(x) for x in range(10)]:
                continue

            # negative number
            # 负号
            pntype = get_forward_type_for_negative(node)
            if not pntype in [
                    NodeType.WORD, NodeType.REVERSE_BRACKET, NodeType.STRING
            ]:
                delete_backward_blank(node)
                continue

        if node.type == NodeType.OPERATOR:
            delete_forward_blank(node)
            delete_backward_blank(node)
            if _settings.get('special_symbol_split'):
                if node.last and node.last.type is not NodeType.BLANK:
                    insert_blank_node(node)
                if node.next and node.next.type is not NodeType.BLANK:
                    insert_blank_node(node.next)


def foreach_separator():
    for node in NodeIterator():
        if node.type == NodeType.SEPARATOR:
            delete_forward_blank(node)
            delete_backward_blank(node)
            if _settings.get('special_symbol_split'):
                if node.next and node.next.type is not NodeType.BLANK:
                    insert_blank_node(node.next)


def foreach_equal():
    for node in NodeIterator():
        if node.type == NodeType.EQUAL:
            if node.last and node.last.type is NodeType.EQUAL:
                merge_prev_node(node)

    for node in NodeIterator():
        if node.type == NodeType.EQUAL:
            delete_forward_blank(node)
            delete_backward_blank(node)
            if _settings.get('special_symbol_split'):
                if node.last and node.last.type is not NodeType.BLANK:
                    insert_blank_node(node)
                if node.next and node.next.type is not NodeType.BLANK:
                    insert_blank_node(node.next)


def foreach_bracket():
    for node in NodeIterator():
        if node.type == NodeType.BRACKET:
            delete_backward_blank(node)
            if _settings.get('bracket_split'):
                if node.next and node.next.type != NodeType.BRACKET:
                    insert_blank_node(node.next)

        if node.type == NodeType.REVERSE_BRACKET:
            delete_forward_blank(node)
            if _settings.get('bracket_split'):
                if node.last and node.last.type != NodeType.REVERSE_BRACKET:
                    insert_blank_node(node)
            if node.last and node.last.last and node.last.type == NodeType.ENTER and node.last.last.type == NodeType.REVERSE_BRACKET:
                delete_node(node.last)


def foreach_word():
    for node in NodeIterator():
        if node.last and node.last.type == node.type == NodeType.WORD:
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

            do_count = line_key_dict.get('do', 0)
            end_count = line_key_dict.get('end', 0)

            if do_count > 0 and do_count <= end_count:
                indent += end_count - do_count
                deal_indent(line)
                line = create_line()
            else:
                line = create_line()
                deal_indent(line)
            line_indent = 0
            del line_key_dict
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
    global _start_node
    global _end_node
    global _lines
    global _settings
    _start_node = None
    _end_node = None
    _lines = []
    _settings = {}


def _lua_format(lines, setting=None):
    purge()
    global _settings
    _settings = setting

    # deal content
    content = ''
    for line in lines:
        line += '\n'
        content += line
    content += '\n'
    content = content.replace('\t', '')
    content = content.replace(r'\n', r'\\n')
    content = content.replace(r'\r', r'\\r')

    parse_node(content)
    foreach_node()
    # for node in NodeIterator():
    #     print(str(node), node.ty8e)
    # return ""
    # exit()

    foreach_blank()
    foreach_string_connect()
    foreach_word()

    foreach_bracket()

    foreach_operator()
    foreach_separator()
    foreach_equal()

    tidy_indent()


# return a string
def lua_format(lines, settings):
    _lua_format(lines, settings)

    r = ''
    blank_line_count = 0
    for line in _lines:
        if line.is_blank_line():
            blank_line_count += 1
            if blank_line_count >= 2: continue
        else:
            blank_line_count = 0
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
