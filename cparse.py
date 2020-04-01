#!/usr/bin/env python
from spark import GenericScanner

from spark import GenericParser
from spark import GenericASTBuilder
from spark import GenericASTTraversal

from ast import AST

def IsInt( str ):
    """
    Checks for integer, hex or no
    """
    try:
        num = int(str,0)
        return 1
    except ValueError:
        return 0
    
class Token:
        def __init__(self, type, attr=None, lineno='???'):
            self.type = type
            self.attr = attr
            self.lineno = lineno

        def __cmp__(self, o):
            return cmp(self.type, o)
        ###
        def __repr__(self):
            return str(self.type)
        #So we can use this as a leaf - see release notes for SPARK
        def __getitem__(self, i):	
            raise IndexError
        
        
class CScanner(GenericScanner):
        """
        Scans for a minimized version of C code. Anything not recognized is a "label"
        """
        def __init__(self):
            self.tokens=[]
            GenericScanner.__init__(self)
            self.lineno=1
            
        def tokenize(self, input):
            self.tokens = []
            GenericScanner.tokenize(self, input)
            return self.tokens

        ###EVERYTHING ELSE
        def t_while(self,s):
            r'while'
            t=Token(type='while',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
        def t_as(self,s):
            r'as'
            t=Token(type='as',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
            
        def t_import(self,s):
            r'\#import'
            t=Token(type='#import',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
            
        def t_newline(self,s):
            r'[\n]'
            t=Token(type='newline',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            self.lineno+=1

        def t_default(self,s):
            r'[a-zA-Z_][a-zA-Z0-9_]*'
            #print "Default Matched: *%s*"%s
            t=Token(type='name',attr=s,lineno=self.lineno)
            self.tokens.append(t)   
        
        def t_comment(self,s):
            r'//.*?\n'
            self.lineno+=1

        def t_whitespace(self, s):
            r'\s+'
            self.lineno+=s.count("\n")

        
        def t_star(self,s):
            #these are used in front of calls, but we can just ignore them...
            r'\*'
            pass
        
        def t_decnumber(self, s):
            r'(?!0x)\d+'
            t = Token(type='decnumber', attr=s,lineno=self.lineno)
            self.tokens.append(t)

        def t_hexnumber(self,s):
            r'0x[a-fA-F0-9]+'
            t = Token(type='hexnumber', attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
        def t_colon(self,s):
            r':'
            t = Token(type=':', attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
        def t_dollarsign(self,s):
            r'\$'
            t=Token(type='$',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
        def t_comma(self,s):
            r','
            t=Token(type=',',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
        def t_lparen(self,s):
            r'\('
            t=Token(type='(',attr=s,lineno=self.lineno)
            self.tokens.append(t)

        def t_rparen(self,s):
            r'\)'
            t=Token(type=')',attr=s,lineno=self.lineno)
            self.tokens.append(t)

            
        def t_plus(self,s):
            r'\+'
            t=Token(type='+',attr=s,lineno=self.lineno)
            self.tokens.append(t)


        def t_minus(self,s):
            r'\-'
            t=Token(type='-',attr=s,lineno=self.lineno)
            self.tokens.append(t)

        def t_semicolon(self,s):
            r';'
            t=Token(type=';',attr=s,lineno=self.lineno)
            self.tokens.append(t)

        def t_equal(self,s):
            r'='
            t=Token(type='=',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
        def t_quotedstring(self,s):
            r'".*?"'
            t=Token(type='quotedstring',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
            
        def t_leftbracket(self,s):
            r'\{'
            t=Token(type='{',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
        def t_rightbracket(self,s):
            r'\}'
            t=Token(type='}',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
        def t_leftsquarebracket(self,s):
            r'\['
            t=Token(type='[',attr=s,lineno=self.lineno)
            self.tokens.append(t)

        def t_rightsquarebracket(self,s):
            r'\]'
            t=Token(type=']',attr=s,lineno=self.lineno)
            self.tokens.append(t)
            
            
#common bugs when writing these things
# forgetting a space such as: blah::= 
#
class cparser(GenericASTBuilder):
        def p_start(self, args):
            '''
            file_input ::= file_contents
            file_contents ::= file_contents stmt 
            file_contents ::= file_contents newline
            file_contents ::=
            stmt ::= directive 
            stmt ::= functiondeclare
            statements ::= insidestmt ; whitespace statements
            statements ::= insidestmt ;
            statements ::=
            functiondeclare ::= type whitespace name ( argumentlist ) whitespace blockstart whitespace statements whitespace blockend whitespace
            blockstart ::= {
            blockend ::= }
            insidestmt ::= variabledeclare
            insidestmt ::= functioncall
            insidestmt ::= leftvalue op rightvalue
            op ::= =
            op ::= *
            op ::= /
            op ::= +
            op ::= -
            op ::= <<
            op ::= >>
            op ::= ~
            op ::= ^
            leftvalue ::= * name
            leftvalue ::= name
            rightvalue ::= number
            rightvalue ::= functioncall
            rightvalue ::= name
            functioncall ::= name ( functioncallarglist )
            functioncallarglist ::= arg
            functioncallarglist ::= arg , functioncallarglist
            functioncallarglist ::= 
            arg ::= name
            arg ::= number
            variabledeclare ::= type name arrayvals
            arrayvals ::= [ number ]
            arrayvals ::=
            whitespace ::= newline
            whitespace ::= whitespace newline
            whitespace ::= 
            argumentlist ::= argpair
            argumentlist ::= argumentlist , argpair
            argumentlist ::= 
            argpair ::= type name
            type ::= name
            directive ::= importdirective
            importdirective ::= #import quotedstring , quotedstring as quotedstring 
            number ::= hexnumber
            number ::= decnumber 
            
            '''
        
        def typestring(self, token):
            return token.type
        
        def error(self, token):
            print "Syntax error at `%s' of type %s (line %s)" % (token.attr, token.type,token.lineno)
            print "Often this is because the line contains a mnemonic we don't have in our list yet."
            raise SystemExit

        
        
class vartree:
        """
        This class is a tree to hold variables in and maps them to labels
        The top level is the global level
        When queried, we return the lowest variable
        Currently it only handles one level of tree-ness, which is lame, but if we need it
        later we can flesh it out
        """
        def __init__(self):
            self.tree={}
            self.tree["globals"]={}
            self.current="globals"
            self.tree["globals"]["variables"]={}
            self.tree["globals"]["functions"]={}


        def addvar(self,label,varname,type):
            self.tree[self.current]["variables"][varname]=(label,type)
            
        def addfunction(self,label,functionname):
            self.tree[self.current]["functions"][varname]=label        
            
        def down(self,label):
            "called when a block starts"
            self.current+="."+label
            self.tree[self.current]={}
            self.tree[self.current]["variables"]={}
            self.tree[self.current]["functions"]={}
        
        def up(self):
            self.current=".".join(self.current.split(".")[:-1])
            
        def getvar(self,variable):
            current=self.current
            while current!="":
                next=".".join(current.split(".")[:-1])
                if self.tree[current]["variables"].has_key(variable):
                        return (current,self.tree[current]["variables"][variable])
                current=next
            return (None,None)
        
        
#we're actually defining another language here as we go along
#GETPC - generates the code that puts the current location of eip in %ebx
# on x86, this is just call getip:
#Calling a function. On RISC we need to know the arguments place(0-6), on x86, we just push
# pusharg argplace, argument
#archalign aligns to words on sparc and does nothing on x86

class ilgenerate(GenericASTTraversal):
        def __init__(self,ast,remoteresolver=None,variableresolver=None):
            self.labels={}
            self.redoList={}
            self.value=""
            self.currentMN=""
            self.currentAL=[]
            self.currentVL=[]
            self.vartree=vartree()
            self.remoteresolver=None
            self.newlabel=0
            self.variableresolver=None
            self.vartypes={}
            self.initvartypes()
            self.stackaddr=0
            self.argumentlist=None
            #used for statements before we have a function
            self.value2=""
            
            self.setRemoteResolver(remoteresolver)
            self.setVariableResolver(variableresolver)
            
            GenericASTTraversal.__init__(self, ast)
            
            self.value+="GETPC\n"
            #we always call main, which takes no args
            self.value+="call main\n"
            self.value+="ret 0\n"
            
            self.postorder()
            return

        def logerror(self,message):
            print "ERROR: %s"%message
            raise LookupError
        
        def initvartypes(self):
            #self.vartypes[typename]=[signed/unsigned,size]
            self.vartypes["int"]=[1,4]
            self.vartypes["pointer"]=[0,4]
            self.vartypes["uint"]=[0,4]
            self.vartypes["uint32"]=[0,4]
            self.vartypes["short"]=[1,2]


        def getTypeSize(self,type):
            if self.vartypes.has_key(type):
                return self.vartypes[type][1]
            else:
                self.logerror("Had no type information for %s"%type)
            
        def setVariableResolver(self,resolver):
            self.variableresolver=resolver

        def getLocalVariable(self,variable):
            if self.variableresolver==None:
                self.logerror("No variable resolver!")
            return self.variableresolver(variable)
            
        def setRemoteResolver(self,resolver):
            self.remoteresolver=resolver

        def getRemoteFunction(self,functionname):
            if self.remoteresolver==None:
                self.logerror("No remote function resolver!")
            return self.remoteresolver(functionname)
        
        def getLabel(self):
            self.newlabel+=1
            return "LABEL%d"%self.newlabel

        
        def addfunction(self,label,function):
            self.vartree.addfunction(label,function)
        
        def addvariable(self,label,variable,type):
            self.vartree.addvar(label,variable,type)
        
        def setcurrentfunction(self,function):
            #self.vartree.setfunction(function)
            pass
            
        def allocateStackSpace(self,size):
            tmp=self.stackaddr
            self.stackaddr+=size
            return tmp
        
        def loadarg(self,argname):
            """
            for any given value, load it into the accumulator
            """
            if IsInt(argname):
                self.value2+="loadconst %s"%argname
                return
            (current, arg)=self.vartree.getvar(argname)
            if current==None:
                self.logerror("Could not find variable %s"%argname)
            print "[%s] arg [%s]"%(current,arg)
            argtype=arg[1]
            if argtype=="array":
                #we need to send the ADDRESS of the array, not the contents
                if current=="globals":
                    return "loadglobaladdress %s\n"%(arg[0])
                else:
                    return "locallocaladddress %s\n"%(arg[0])
            if current=="globals":
                #global argument, need to set up a LABLE-geteip(%ebx) type device
                # on solaris we just use add %o7, label-called+4, register
                # register is determined by argnum
                # we actually need to mov it into eax then push it
                # here is GCC pushing a short
                #0x8048339 <main+19>:	movswl 0xfffffffe(%ebp),%eax
                #0x804833d <main+23>:	push   %eax
                #0x804833e <main+24>:	call   0x804830c <func>
                return "loadglobal %s %s\n"%(arg[0],self.getTypeSize(arg[1]))
            else:
                #local argument
                # on x86 we need to push the stackoffset
                # on sparc we need to ld [ %sp + argnum*4], %l0
                return "loadlocal %s %s\n"%(arg[0],self.getTypeSize(arg[1]))
            
        def pusharg(self,argname,argnum):
            """
            For any given argument, figure out how to push it onto the argument stack
            """
            tmp=self.loadarg(argname)
            #arg just loads eax/l0 into the argument list
            tmp+="arg %d\n"%argnum
            return tmp
            
            
        def resolveArgList(self):
            """
            takes the current argument list and gets the arguments for it as space on the stack
            or as a register or whatever
            """
            if self.argumentlist==None:
                return
            i=0
            for arg in self.argumentlist.args:
                print "Node.name=%s node.type=%s"%(arg[1],arg[0])
                name=arg[1]
                type=arg[0]
                #we reserve the variable lables: in0-256 as input variables
                self.addvariable("in%d"%i,name,type)
                i+=1
                #self.addvariable(addr,node.name,node.type)       
            
            
        #########################################
        def n_type(self,node):
            node.attr=node[0].attr
            
        def n_rightvalue(self,node):
            node.exprType="rightvalue"
            print "rightvalue" 
            if node[0].type=="number":
                #loads eax with the integer
                self.value2+="loadint %d\n"%int(node[0].attr,0)
            elif node[0].type=="functioncall":
                #eax should already be loaded with the results after our call
                pass
            elif node[0].type=="name":
                #need to load a variable
                self.value2+=self.loadarg(node[0].attr)
                
            else:
                print "rightvalue type = %s"%node[0].type
            
            
        def n_leftvalue(self,node):
            #load whatever's in the accumulator into the variable
            print "leftvalue"
            argname=node[0].attr
            print "loading variable %s"%argname
            
            (current, arg)=self.vartree.getvar(argname)
            if current==None:
                self.logerror("Could not find variable %s"%argname)
            print "[%s] arg [%s]"%(current,arg)
            if current=="globals":
                node.attr="accumulator2memoryglobal %s %s\n"%(arg[0], self.getTypeSize(arg[1]))
            else:
                node.attr="accumulator2memorylocal %s %s\n"%(arg[0], self.getTypeSize(arg[1]))

        def n_insidestmt(self,node):
            print "insidestatement"
            if node[0].type=="functioncall":
                pass
            elif node[0].type=="leftvalue":
                self.value2+=node[0].attr
                
        def n_number(self,node):
            node.exprType="number"
            node.attr=node[0].attr
            
        def n_arg(self,node):
            node.exprType="arg"
            node.type="arg"
            node.attr=node[0].attr
            
            
        def n_blockstart(self,node):
            #starts a block, and if there is an argument list, resolves that into variables
            print "Block started"
            label=self.getLabel()
            self.vartree.down(label)
            if self.argumentlist!=None:
                self.resolveArgList()
                self.argumentlist=None
            
        def n_blockend(self,node):
            self.vartree.up()
            
        def n_variabledeclare(self,node):
            print "Variable declare found"
            print "TYPE: %s"%node[0][0].attr
            print "name: %s"%node[1].attr
            node.type=node[0][0].attr
            node.name=node[1].attr
            if not self.vartypes.has_key(node.type):
                self.logerror("Don't have the type %s in our typelist!"%node.type)
            else:
                print "Found a %s defined"%node.type
            varsize=self.vartypes[node.type][1]
            #now that we know what it is, we need to add this to the current function's size
            addr=self.allocateStackSpace(varsize)
            self.addvariable(addr,node.name,node.type)
        
        def n_functioncallarglist(self,node):
            print "Arglist found"
            node.exprType="functioncallarglist"
            node.attr=[]
            for n in node:
                if n.type=="arg":
                        node.attr+=[n.attr]
                if n.type=="functioncallarglist":
                        node.attr+=n.attr
            
            
        def n_functioncall(self,node):
            print "Functioncall"
            functionname=node[0].attr
            arglist=node[2]
            length=len(arglist.attr)
            for i in range(length-1,-1,-1):
                print "length=%d i=%d"%(length,i)
                print "Argument[%d]=%s"%(i,arglist.attr[i])
                self.value2+=self.pusharg(arglist.attr[i],i)
            print "Functionname is %s"%functionname
            #if this is a remote function, then we need to call it the hard way
            # with mov LABEL-geteip(%ebx), %eax
            # call eax
            # but if this is a local function
            # we can just call it
            (current,var)=self.vartree.getvar(functionname)
            if current==None:
                #we have a local function call
                self.value2+="call %s\n"%functionname
            else:
                #global function pointer
                #load a word from the offset from the LABEL-geteip(%ebx)
                self.value2+="loadglobal %s %s\n"%(var[0],self.getTypeSize("pointer"))
                #call the accumulator %eax or %l0
                self.value2+="callaccum\n"
            
        def n_stmt(self,node):
            print "Statement found"

        
        def n_functiondeclare(self,node):
            print "Found function declare"
            name=node[2].attr
            self.setcurrentfunction(name)
            self.value+="labeldefine %s\n"%name
            self.value+="functionprelude\n"
            if self.stackaddr!=0:
                self.value+="getstackspace %d\n"%self.stackaddr

            self.value+=self.value2
            self.value2=""
            self.value+="freestackspace %d\n"%self.stackaddr
            print "Type [4] is %s"%node[4].type
            argsize=node[4].argsize
            self.value+="ret %s\n"%argsize
            self.stackaddr=0

        def n_argpair(self,node):
            #ok, need to get argpair done and added to variable list
            #TODO
            pass
            
        def n_argumentlist(self,node):
            print "argumentlist"
            node.args=[]
            if len(node)==0:
                node.argsize=0
                return
            node.argsize=0
            if node[0].type=="argpair":
                type=node[0][0].attr
                name=node[0][1].attr
                node.argsize=4
                print "%s %s"%(type,name)
                node.args+=[(type,name)]
            elif node[0].type=="argumentlist":
                print "Previous node's size is %d"%node[0].argsize
                node.argsize+=node[0].argsize
                node.args+=node[0].args
            else:
                print "Eh? type==%s"%node[0].type
            if len(node)==3:
                print "node[2].type=%s"%node[2].type
                if node[2].type=="argumentlist":
                    node.argsize+=node[2].argsize
                    node.args+=node[2].args
                elif node[2].type=="argpair":
                    node.argsize+=4
                    node.args+=[(node[2][0].attr,node[2][1].attr)]
                    
            print "New argsize=%d new args=%s"%(node.argsize,node.args)
            #set this so when we start a block we can resolve all the variables
            self.argumentlist=node
            
        def n_importdirective(self,node):
            print "Import directive found"
            #[1:-1] is to strip off the quotes
            importtype=node[1].attr[1:-1]
            importname=node[3].attr[1:-1]
            importdest=node[5].attr[1:-1]
            importlabel=self.getLabel()
            #ok, now we need to add a global variable
            self.value+="labeldefine %s\n"%importlabel
            if importtype=="remote":
                self.addvariable(importlabel,importdest,"functionpointer")
                self.value+="longvar 0x%8.8x\n"%self.getRemoteFunction(importname)
            elif importtype=="string":
                self.addvariable(importlabel,importdest,"array")
                self.value+="ascii %s\n"%self.getLocalVariable(importname)
                self.value+="databytes 0\n"
                self.value+="archalign\n"
            else:
                print "Import type unknown: %s"%importtype
                
                
                
def preprocess(data):
        return data

def scan(data):
        myscanner=CScanner()
        tokens = myscanner.tokenize(data)
        return tokens

def parse(tokens):
        parser = cparser(AST,'file_input')
        tree=parser.parse(tokens)
        return tree

def dummyfunctionresolver(function):
        return 0x01020304

def dummyvariableresolver(variable):
        return "BOB"

def generate(tree):
        generator=ilgenerate(tree,remoteresolver=dummyfunctionresolver,variableresolver=dummyvariableresolver)
        return generator


def showtree(node, depth=0):
        if hasattr(node, 'attr'):
            print "%2d" % depth, " "*depth, '<<'+node.type+'>>',
            try:
                if len(node.attr) > 50:
                        print node.attr[:50]+'...'
                else: 
                        print node.attr
            except:
                print ""
                print "Error: attr=%s"%str(node.attr)
        else:
            print "%2d" %depth, "-"*depth, '<<'+node.type+'>>'
            for n in node._kids:
                showtree(n, depth+1)


if __name__=="__main__":
        filename="lcreat.c"
        data=open(filename).read()
        data=preprocess(data)
        tokens=scan(data)
        #print tokens
        print "-"*50
        tree=parse(tokens)
        #print "-"*50
        #print "Showing tree"
        #showtree(tree)
        print "-"*50
        
        print "-"*50
        #Typecheck is basically useless since we do real checking when we generate it...
        #print "Doing typecheck"
        #typecheck=typecheck(tree)

        print "Doing Generation of Code"
        x=generate(tree)
        print "-"*50
        print "IL code: \n%s"%(x.value)
        #transform into AT&T style x86 assembly
        #then run through at&t x86 assembler
        #then done!
        
        
        
        
        
        