-- https://github.com/denglf/FormatLua
local a="你好"
    local b
    function set_text(name,value)
            local doc=document:getElementsByName(name)
        if doc and #doc>0 then
        doc[1]:setPropertyByName("text",value)
    end
    end
    return b
