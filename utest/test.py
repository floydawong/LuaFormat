import os
os.sys.path.append(os.path.abspath('..'))

if os.sys.version.startswith('3'):
    from .core import lua_format
else:
    from core import lua_format


def read_file(path):
    with open(path, 'r') as fp:
        content = fp.read()
        fp.close()
        return content


def compare_file(index):
    src = read_file('./lua-example/%d.lua' % index)
    target = read_file('./lua-example/target-%d.lua' % index)
    return lua_format(src) == target


def test_example():
    assert (compare_file(2))


if __name__ == '__main__':
    test_example()
