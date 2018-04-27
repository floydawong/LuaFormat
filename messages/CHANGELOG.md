# Change Log


## 0.1.5
- Unfolding code before run `lua format`
- Optimize shortcut keys to prevent conflicts with other packages
- Change default setting of `auto_format_on_save` to False
- Delete redundant blank lines


## 0.1.3
- Remove the space before the newline
- Fixes can not delete blank around the operator when setting:special_symbol_split is false


## 0.1.2
- Fix #14
- Fix failure to \n\r in the string 


## 0.1.1
- Fix #12
- Fix `--[=[comment]=]` can not recognized as comment
- Fix `[=[string]=]` can not recognized as string
- Fix the indentation error `do .. end` after `if then` or `for do`


## 0.1.0
> The basic functionality has been done
- Automatic indentation
- Separation of special characters
- Tab size via settings
- Main menu(settings/key bindings)
- Commands via `ctrl + shift + p`
- Utest module


## 0.0.12
- Fix strings and comment priority bugs
- Fix nested bugs in string
- Fix the bug for comment movement


## 0.0.8
- Fix #6: scientific notation(Ex: 1234e-4)
- The separation of minus(Ex: local x = - 1)


## 0.0.4
- Added default setting
- Run `lua format` when set `auto_format_on_save` in settings
- Set the format of the symbols in the settings
