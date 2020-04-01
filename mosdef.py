#!/usr/bin/env python
"""
MOSDEF (pronounced mos' def!) is a compiler from C->shellcode
Copyright Dave Aitel 2003
"""
import sys,os
import getopt
import atandtscan
import atandtparse
import cparse

class MOSDEFCompiler:
    def __init__(self):
        pass
    
    def setParser(self,parser):
        self.parser=parser
        
    def setScanner(self,scanner):
        self.scanner=scanner
        
    def compile(self,data):
        """
        takes in a string of data, compiles it to object code, returns that object code or
        an error message
        """
        tokens=self.scanner(data)
        print tokens
        parsed=self.parser(tokens)
        return 0,None,"yo"
        
def compile(data,arch,remoteresolver):
    tokens=cparse.scan(data)
    myparser=cparse.cparser()
    myparser.setRemoteResolver(remoteresolver)
    myparser.parse(tokens)
    #convert2asm=cparse.getil2asm(arch)
    
    return ""
    
def assemble(data,arch):
    """
    assembles a given block of data into bytecodes
    """
    if arch=="X86":
        data=atandtparse.atandtpreprocess(data)
        tokens=atandtscan.scan(data)
        tree=atandtparse.parse(tokens)
        x=atandtparse.x86generate(tree)
        return x.value
    
    print "Unknown arch: %s"%arch
    return None
def usage():
    print "Usage: "+sys.argv[0]+" -f filename"
    sys.exit(1)
    
if __name__=="__main__":
    try:
        (opts,args)=getopt.getopt(sys.argv[1:],"f:")
    except getopt.GetoptError:
        #print help
        usage()

    filename=""
    for o,a in opts:
        if o in ["-f"]:
            filename=a
    
    if filename=="":
        usage()
        
    mycompiler=MOSDEFCompiler()
    data=open(filename).read()
    mycompiler.setScanner(atandtscan.scan)
    mycompiler.setParser(atandtparse.parse)
    err,errmsg,output=mycompiler.compile(data)
    if err:
        print errmsg
        sys.exit(1)
    
    
    