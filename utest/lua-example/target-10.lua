-- https://github.com/FloydaGithub/LuaFormat/issues/9

--抽象类声名
__DebugAbstract__()
class "AbstractClass" (function(_ENV)
    --加上__DebugRequire__()属性，子类不实现会报错
    __DebugRequire__() 
    function AbstractFuctionName(self, ...)
    end
end)

--普通基类
class "BaseClass" (function(_ENV)
    
    ----------------------------------------------
    ----------------- Constructor ----------------
    ----------------------------------------------    
    
    __DebugArguments__{--[[Type]]}
    function BaseClass(self, ...) 
    end
    
    ----------------------------------------------
    ------------------- Method -------------------
    ----------------------------------------------
    
    --虚方法，约定重写的标记virtual
    --[[virtual]]
    __DebugArguments__{--[[Type]]}
    function VirtualFuctionName(self, ...)
        -- body
    end
    
end)
