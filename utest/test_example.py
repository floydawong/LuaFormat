import os
import json

core_directory = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..')
os.sys.path.append(core_directory)
from core.LuaFormat import lua_format

EXAMPLE_PATH = './lua-example'
CHECK_LIST = [
    'operator',
    'separator',
    'negative',
    'string',
    'comment',
]


def load_content(fpath):
    with open(fpath, 'r') as fp:
        content = fp.read()
        return content
    return ''


def load_lines(fpath):
    lines = []
    with open(fpath, 'r') as fp:
        for line in fp.readlines():
            line = line[:-1]
            lines.append(line)
        fp.close()
        return lines
    return []


def fake_setting(flag):
    settings = {}
    settings['tab_size'] = 4
    settings['special_symbol_split'] = flag
    settings['bracket_split'] = flag
    return settings


def compare_file(keyword):
    origin = os.path.join(EXAMPLE_PATH, keyword + '.lua')
    originT = os.path.join(EXAMPLE_PATH, keyword + 'T.lua')
    originF = os.path.join(EXAMPLE_PATH, keyword + 'F.lua')
    if not os.path.exists(origin):
        print('not exists : %s' % origin)
        return
    if not os.path.exists(originT):
        print('not exists : %s' % originT)
        return
    if not os.path.exists(originF):
        print('not exists : %s' % originF)
        return

    content_origin = load_lines(origin)
    content_originT = load_content(originT)
    content_originF = load_content(originF)
    fmt_resultT = lua_format(content_origin, fake_setting(True))
    fmt_resultF = lua_format(content_origin, fake_setting(False))

    if content_originT != fmt_resultT:
        print('------------ %s ------------' % (keyword + 'T'))
        print(fmt_resultT)
        print('------------ %s ------------' % (keyword + 'T'))
        return False
    if content_originF != fmt_resultF:
        print('------------ %s ------------' % (keyword + 'F'))
        print(fmt_resultF)
        print('------------ %s ------------' % (keyword + 'F'))
        return False

    print("Check Successful: %s" % keyword)
    return True


# For Utest
def test_all_example():
    for fname in CHECK_LIST:
        assert compare_file(fname)


def debug_all_example():
    for fname in CHECK_LIST:
        compare_file(fname)


if __name__ == '__main__':
    debug_all_example()
