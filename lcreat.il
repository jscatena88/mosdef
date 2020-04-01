GETPC
call main
ret 0
labeldefine LABEL1
longvar 0x01020304
labeldefine LABEL2
ascii BOB
databytes 0
archalign
labeldefine sendint
functionprelude
getstackspace 4
loadint 2
accumulator2memorylocal 0 4
loadlocal in1 4
accumulator2memorylocal 0 4
freestackspace 4
ret 8
labeldefine main
functionprelude
getstackspace 4
loadglobaladdress LABEL2
arg 0
loadglobal LABEL1 4
callaccum
accumulator2memorylocal 0 4
loadlocal 0 4
arg 1
loadlocal 0 4
arg 0
call sendint
freestackspace 4
ret 0
