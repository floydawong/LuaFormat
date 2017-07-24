import os

if os.sys.version.startswith('3'):
    from .LuaFormat import lua_format
else:
    from LuaFormat import lua_format
