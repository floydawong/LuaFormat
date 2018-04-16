-- separator
function foo( )
    local a, b, c, d;
    a = 1; b = 2; c = 3; d = 4;
    return a, b, c, d;
end;

a, b, c, d = foo( );
print( a, b, c, d );

a, b, c, d = foo( ); print( a, b, c, d );
