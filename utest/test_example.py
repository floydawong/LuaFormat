import os
import json

core_directory = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..')
os.sys.path.append(core_directory)
from core.LuaFormat import lua_format

EXAMPLE_PATH = './lua-example'


def read_file(path):
    with open(path, 'r') as fp:
        content = fp.read()
        fp.close()
        return content
    return ''


def compare_file(index, isDebug=False):
    src_path = os.path.join(EXAMPLE_PATH, str(index) + '.lua')
    target_path = os.path.join(EXAMPLE_PATH, 'target-' + str(index) + '.lua')
    src = read_file(src_path)
    target = read_file(target_path)

    with open('../LuaFormat.sublime-settings') as fp:
        s = ''
        for line in fp.readlines():
            if not '//' in line:
                s += line
        settings = json.loads(s)

    format_content = lua_format(src, settings)
    if isDebug:
        assert format_content == target
    else:
        if format_content == target:
            print('Example %d is OK' % index)
        else:
            print(format_content)


def test_all_example(index=1):
    fname = str(index) + '.lua'
    fpath = os.path.join(EXAMPLE_PATH, fname)
    if os.path.exists(fpath):
        compare_file(index, True)
        test_all_example(index + 1)


def debug_all_example(index=1):
    fname = str(index) + '.lua'
    fpath = os.path.join(EXAMPLE_PATH, fname)
    if os.path.exists(fpath):
        compare_file(index)
        debug_all_example(index + 1)

def debug_example(index=1):
    fname = str(index) + '.lua'
    fpath = os.path.join(EXAMPLE_PATH, fname)
    if os.path.exists(fpath):
        compare_file(index)


if __name__ == '__main__':
    # test_all_example()
    debug_all_example()
    # debug_example()
