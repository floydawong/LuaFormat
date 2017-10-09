import os

core_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
os.sys.path.append(core_directory)

if sys.version_info < (3, 0):
    from core.LuaFormat import lua_format
else:
    from LuaFormat.core.LuaFormat import lua_format

EXAMPLE_PATH = './lua-example'


def read_file(path):
    with open(path, 'r') as fp:
        content = fp.read()
        fp.close()
        return content
    return ''

def compare_file(index):
    src_path = os.path.join(EXAMPLE_PATH, str(index) + '.lua')
    target_path = os.path.join(EXAMPLE_PATH, 'target-' + str(index) + '.lua')
    src = read_file(src_path)
    target = read_file(target_path)

    print('Example %d is %s' % (index, lua_format(src) == target))
    assert(lua_format(src) == target)

def test_example(index=1):
    fname = str(index) + '.lua'
    fpath = os.path.join(EXAMPLE_PATH, fname)
    if os.path.exists(fpath):
        compare_file(index)
        test_example(index + 1)

if __name__ == '__main__':
    test_example()
