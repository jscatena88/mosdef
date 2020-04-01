#!/usr/bin/env python
"""
makeexe.py

Copywrite: Dave Aitel, 2003

"""


NOTES="""
See this article for information on create a minimal ELF file on Linux
http://www.muppetlabs.com/~breadbox/software/tiny/teensy.html
  BITS 32
  
                org     0x08048000
  
  ehdr:                                                 ; Elf32_Ehdr
                db      0x7F, "ELF", 1, 1, 1            ;   e_ident
        times 9 db      0
                dw      2                               ;   e_type
                dw      3                               ;   e_machine
                dd      1                               ;   e_version
                dd      _start                          ;   e_entry
                dd      phdr - $$                       ;   e_phoff
                dd      0                               ;   e_shoff
                dd      0                               ;   e_flags
                dw      ehdrsize                        ;   e_ehsize
                dw      phdrsize                        ;   e_phentsize
                dw      1                               ;   e_phnum
                dw      0                               ;   e_shentsize
                dw      0                               ;   e_shnum
                dw      0                               ;   e_shstrndx
  
  ehdrsize      equ     $ - ehdr
  
  phdr:                                                 ; Elf32_Phdr
                dd      1                               ;   p_type
                dd      0                               ;   p_offset
                dd      $$                              ;   p_vaddr
                dd      $$                              ;   p_paddr
                dd      filesize                        ;   p_filesz
                dd      filesize                        ;   p_memsz
                dd      5                               ;   p_flags
                dd      0x1000                          ;   p_align
  
  phdrsize      equ     $ - phdr
  
  _start:
  
  ; your program here
  
  filesize      equ     $ - $$

"""

import sys


#returns a binary version of the string
def binstring(instring):
    result=""
    #erase all whitespace
    tmp=instring.replace(" ","")
    tmp=tmp.replace("\n","")
    tmp=tmp.replace("\t","")
    tmp=tmp.replace("\r","")
    tmp=tmp.replace(",","")
    
    
    if len(tmp) % 2 != 0:
        print "tried to binstring something of illegal length: %d: *%s*"%(len(tmp),prettyprint(tmp))
        return ""

    while tmp!="":
        two=tmp[:2]
        #account for 0x and \x stuff
        if two!="0x" and two!="\\x":
            result+=chr(int(two,16))
        tmp=tmp[2:]

    return result

#int to intelordered string conversion
def intel_order(myint):
    str=""
    a=chr(myint % 256)
    myint=myint >> 8
    b=chr(myint % 256)
    myint=myint >> 8
    c=chr(myint % 256)
    myint=myint >> 8
    d=chr(myint % 256)
    
    str+="%c%c%c%c" % (a,b,c,d)

    return str

def makelinuxexe(data,filename=""):
        """
        Makes a linux executable from the data bytes (shellcode) in "data"
        Should be close to optimally small
        0x08048054 is where our shellcode will start, if you want to debug it with gdb
        """
        tmp=""
        tmp+=binstring("7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00")
        tmp+=binstring("02 00 03 00 01 00 00 00");
        tmp+=binstring("54 80 04 08"); #memory segment for start of first .text page backwards
        tmp+=binstring("34 00 00 00") #phdr - $$
        tmp+=binstring("00"*8)
        
        tmp+=binstring("34 00 20 00 01 00 ");
        tmp+=binstring("00 00")
        tmp+=binstring("00 00 00 00 01 00 00 00 00 00 00 00 00 80 04 08")
        tmp+=binstring("00 80 04 08") #memseg again
        tmp+=intel_order(54+len(data))*2 
        tmp+=binstring("05 00 00 00 00 10 00 00")
        tmp+=data
        if filename!="":
            try:
                fd=open(filename,"w")
                fd.write(tmp)
                fd.close()
                import os
                os.chmod(filename, 0775)
            except:
                print "Couldn't open, write or chmod outfile"
        return tmp
    

    

def usage():
        print "%s inputfile outputfile"%sys.argv[0]
        sys.exit(1)
        
if __name__=="__main__":
        try:
                #data=open(sys.argv[1]).read()
                data="\xcc"
        except:
                print "Couldn't open file to read in."
                usage()

        filedata=makelinuxexe(data)
        try:
                fd=open(sys.argv[2],"w")
                fd.write(filedata)
                fd.close()
                import os
                os.chmod(sys.argv[2], 0775)
        except:
                print "Couldn't open, write or chmod outfile"
                sys.exit(1)
        

        
