import sublime


def get_package_settings():
    setting_name = 'Default.sublime-settings'
    settings = sublime.load_settings(setting_name)
    return settings


def get_settings_param(view, param_name, default=None):
    settings = get_package_settings()
    project_settings = view.settings()
    return project_settings.get(param_name, settings.get(param_name, default))
