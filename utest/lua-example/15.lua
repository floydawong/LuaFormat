-- https://github.com/floydawong/LuaFormat/issues/24

function test:check()
	if some == 1 then
	self:call(funA:create(funB(1),
		funC(
			function()
				if self.m_class == nil then
					self.m_class = classA.new(
					{
						a = 1,
						b = 2,
						c = 3
					}):addTo(self)
				else
					self.funD()
				end
			end)))
	else
	self:funE()
	end
end
