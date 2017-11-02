-- indent
function foo(...)
    print(...)
end

function wrap(func, a, b)
    if func then func(a, b) end
end

wrap(function(func, b)
    func(b)
end, function(x)
    print(x)
end, 3)

wrap(function(a, b)
    print(a, b)
    if a > b then 
        print(a - b)
    else
        return wrap(function(a, b)
            print(a + b)
        end, a, b)
    end
end, 11, 3)
