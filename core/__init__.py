import os

if os.sys.version.startswith('3'):
    from LuaFormat.core.LuaFormat import lua_format
else:
    from core.LuaFormat import lua_format
