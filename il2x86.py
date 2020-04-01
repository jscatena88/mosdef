#!/usr/bin/env python
"""
Converts a IL file (or buffer) into AT&T syntax x86
"""

def generate(data):
        out=""
        lines=data.split("\n")
        for line in lines:
                if line=="":
                        continue
                words=line.split(" ")
                if words[0]=="GETPC":
                        out+="call RESERVED_getpc\n"
                        out+="RESERVED_getpc:\n"
                        out+="pop %ebx\n"
                elif words[0]=="call":
                        out+="call %s\n"%words[1]
                elif words[0]=="ret":
                        if words[1]!="0":
                                out+="ret $%d\n"%int(words[1],0)
                        else:
                                out+="ret\n"
                elif words[0]=="callaccum":
                        out+="call *%eax\n"
                elif words[0]=="labeldefine":
                        out+="%s:\n"%words[1]
                elif words[0]=="longvar":
                        out+=".long %s\n"%words[1]
                elif words[0]=="ascii":
                        out+=".ascii \"%s\"\n"%words[1]
                elif words[0]=="databytes":
                        out+=".byte %s\n"%words[1]
                elif words[0]=="archalign":
                        out+=""
                elif words[0]=="functionprelude":
                        out+="pushl %ebp\nmovl %esp,%ebp\n"
                elif words[0]=="getstackspace":
                        out+="sub $%d,%%esp\n"%(int(words[1],0))
                elif words[0]=="freestackspace":
                        out+="movl %ebp,%esp\npopl %ebp\n"
                        
                elif words[0]=="loadint":
                        out+="movl $%d,%%eax\n"%int(words[1],0)
                elif words[0]=="accumulator2memorylocal":
                        if words[2]=="4":
                                out+="movl %%eax, 0x%8.8x(%%ebp)\n"%(-(int(words[1])+1)*4)
                        elif words[2]=="2":
                                out+="movs %%ax, 0x%8.8x(%%ebp)\n"%(-(int(words[1])+1)*4)
                        elif words[2]=="1":
                                out+="movb %%al, 0x%8.8x(%%ebp)\n"%(-(int(words[1])+1)*4)
                elif words[0]=="loadlocal":
                        size=int(words[2])
                        if words[1][:2]=="in":
                                #input register on sparc, stack arg on x86
                                argnum=int(words[1][2:])
                                end="0x%8.8x(%%ebp)"%((argnum*4)+8)
                        else:
                                #local stack variable
                                argnum=int(words[1])
                                #out+="argnum = %s\n"%argnum
                                end="0x%8.8x(%%ebp)"%(-(argnum+1)*4)
                        if words[2]=="4":
                                out+="movl %s, %%eax\n"%(end)
                        elif words[2]=="2":
                                out+="movs %s, %%ax\n"%(end)
                        elif words[2]=="1":
                                out+="movb %s, %%al\n"%(end)
                elif words[0]=="arg":
                        out+="pushl %eax\n"
                elif words[0]=="loadglobaladdress":
                        out+="lea %s-RESERVED_getpc(%%ebx), %%eax\n"%(words[1])
                elif words[0]=="loadlocaladdress":
                        out+="lea 0x%8.8x(%%ebp), %%eax\n"%(-1*(int(words[1])+1)*4)
                elif words[0]=="loadglobal":
                        if words[2]=="4":
                                out+="movl %s-RESERVED_getpc(%%ebx), %%eax\n"%(words[1])
                        elif words[2]=="2":
                                out+="movs %s-RESERVED_getpc(%%ebx), %%ax\n"%(words[1])
                        elif words[2]=="1":
                                out+="movb %s-RESERVED_getpc(%%ebx), %%al\n"%(words[1])
        return out
                        
                        
                
                        

if __name__=="__main__":
        filename="lcreat.il"
        data=open(filename).read()
        print "-"*50
        print "x86 code: \n%s"%(generate(data))
        #transform into AT&T style x86 assembly
        #then run through at&t x86 assembler
        #then done!