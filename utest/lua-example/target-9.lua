-- https://github.com/FloydaGithub/LuaFormat/issues/4
function perm:app (a, n)
    if n == 0 then
        coroutine.yield(a)
    else
        for i = 1, n do
            -- put i-th element as the last one
            a[n], a[i] = a[i], a[n]

            -- generate all permutations of the other elements
            permgen(a, n - 1)

            -- restore i-th element
            a[n], a[i] = a[i], a[n]
        end
    end
end
