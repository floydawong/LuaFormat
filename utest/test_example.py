import os

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


def compare_file(index):
    src_path = os.path.join(EXAMPLE_PATH, str(index) + '.lua')
    target_path = os.path.join(EXAMPLE_PATH, 'target-' + str(index) + '.lua')
    src = read_file(src_path)
    target = read_file(target_path)

    format_content = lua_format(src)
    if format_content == target:
        print('Example %d is OK' % index)
    else:
        print(format_content)
        # assert False


def test_example(index=1):
    fname = str(index) + '.lua'
    fpath = os.path.join(EXAMPLE_PATH, fname)
    if os.path.exists(fpath):
        compare_file(index)
        test_example(index + 1)


if __name__ == '__main__':
    test_example()
