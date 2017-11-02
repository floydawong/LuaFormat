-- chunk
local a = {
    1, 2, 3
}

local b = {
    1, 2, 3, 
    {1, 2, 3}, 
    '123', 
    foo = function()
        print('a.foo(')
    end
}

local c = {{
    1, 2, 3, 
    {
        'content'
    }, 
}, 4, 5}
