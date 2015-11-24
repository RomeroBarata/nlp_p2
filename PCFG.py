from nltk.tree import Tree
import bisect
import functools


#  set this constant to true if you want to ignore the treebank's
#  secondary tags. i.e. the tag 'UTT+np' will be used as 'UTT'
IGNORE_DETAILED_TAGS = True

def getTag(tag):
    if IGNORE_DETAILED_TAGS:
        if '+' in tag:
            tag = tag[:tag.index('+')]
        elif '-' in tag:
            tag = tag[:tag.index('-')]
        return ''.join(c for c in tag if c.isalpha())
    else:
        return tag

# the class Symbol represents a symbol in a grammar rule, it
# can be a StartSymbol, a Variable or a Terminal
class Symbol():
    
    StartSymbol = 1
    Variable = 2
    Terminal = 3

    def __init__(self,tag,stype):
        self.tag = tag
        self.type = stype

    def __eq__(self, other):
    	return self.type == other.type and self.tag == other.tag

    def __lt__(self, other):
        if self.type == Symbol.StartSymbol:
            if other.type == Symbol.StartSymbol:
                return self.tag < other.tag
            else:
                return True
        elif self.type == Symbol.Variable:
            if other.type == Symbol.Variable:
                return self.tag < other.tag
            else:
                return other.type == Symbol.Terminal
        else:
            if other.type == Symbol.Terminal:
                return self.tag < other.tag
            else:
                return False


# a Rule has a symbol representing the left hand side of a grammar rule and
# a list of symbols representing the right hand side
@functools.total_ordering
class Rule(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return (self.left == other.left and self.right == other.right)
        else:
            return False

    def __lt__(self,other):
    	if self.left < other.left:
    	    return True
    	elif self.left == other.left:
    		return self.right < other.right
    	else:
    		return False

    def printRule(self):
        print (self.left.tag + ' -> ', end="")
        for rightSymbol in self.right:
            print (rightSymbol.tag + ' ', end="")
        print ("")

# the Grammar has a set of rules. I separated the rules that have terminals 
# in the right hand side from the other formed only by Variables.
class Grammar(object):
    def __init__(self, rules):
        self.rules = []
        self.terminalRules = []

    def hasRule(self, rule):
        for r in self.rules:
            if r == rule:
                return True
        return False
    
    def hasTerminalRule(self, rule):
        for r in self.terminalRules:
            if r == rule:
                return True
        return False

    def addRule(self, newRule):
    	if newRule.right[0].type == Symbol.Terminal:
    	    if not self.hasTerminalRule(newRule):
                bisect.insort(self.terminalRules, newRule)
    	else:    
    	    if not self.hasRule(newRule):
    		    bisect.insort(self.rules, newRule)

    # print the grammar
    def show(self):
        for r in self.rules:
            r.printRule()
    
    # print the grammar including the terminal rules
    def showAll(self):
        self.show()
        for r in self.terminalRules:
            r.printRule()


# receives a list of sentences and constructs the grammar
def constructPCFG(treebank):
    grammar = Grammar([])

    for sentence in treebank:
        processSentences(grammar, sentence, True)
    
    return grammar


# recursive function that read each sentence and add the rules to
# the grammar
def processSentences(grammar, tree, first):
    if first: # first iteration (first variable in the parse tree)
        s = Symbol( getTag(tree.label()) , Symbol.StartSymbol )
    else:
        s = Symbol( getTag(tree.label()) , Symbol.Variable )
    rightSide = []
    for subTree in tree:
        if isinstance(subTree, Tree):
            if (subTree.label() != '.' and subTree.label() != ','):
                rightSide.append( Symbol( getTag(subTree.label()), Symbol.Variable ) )
                processSentences(grammar,subTree, False)
        else:
            rightSide.append( Symbol(subTree, Symbol.Terminal) )
    r = Rule(s, rightSide)
    grammar.addRule(r)

    








