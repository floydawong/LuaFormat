-- https://github.com/FloydaGithub/LuaFormat/issues/12
local MainMission = {}
function MainMission:recData(sub, data)
    if sub == 'Start' then
        local scene = SM.getRunningScene()
        scene:runAction(cc.Sequence:create(cc.DelayTime:create(2), 
            cc.CallFunc:create(function(...)
                return self:gameStart(data)
            end
        )))
    else
        return self:outCard(data)
    end
end
