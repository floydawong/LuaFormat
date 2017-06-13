import sublime

if sublime.version().startswith('3'):
    from .LuaFormat import lua_format
    from .settings import get_package_settings
else:
    from LuaFormat import lua_format
    from settings import get_package_settings

__all__ = ['lua_format', 'get_package_settings']
