--string and comment
local x = 1 --Hello World

print('----- string and comment -----')
-- print('----- string and comment -----')

content = [[
    "Hello World"
    "God is a 'girl'"
    "He's age is 25"
    local cc='aa'..'bb'
    local a=a+1
    restore i-th element
    restore i - th element
]]
local a = a + 1
local cc = 'aa' .. 'bb'
print(content)

for i = 1, 10 do
    print("He's age is", i)
end

print('test')--[[
for i = 1, 10 do
    print("He's age is", i)
    print(content)
end]]print('test')

print('test') -- for i = 1, 10 do
print('test') --     print("He's age is", i)
print('test') --     print(content)
print('test') -- end

print('test') -- for i = 1, 10 do
print('test') -- print("He's age is", i)
print('test') -- print(content)
print('test') -- end

-- restore i-th element
-- restore i - th element
