from nltk.tree import Tree
import bisect
import functools


#  set this constant to true if you want to ignore the treebank's
#  secondary tags. i.e. the tag 'UTT+np' will be used as 'UTT'
IGNORE_DETAILED_TAGS = True

def getTag(tag):
    tag.replace('"','\\"')
    if IGNORE_DETAILED_TAGS:
        pos = [tag.index(ch) for ch in set(tag).intersection(set("+-<>"))]
        if len(pos)>0:
            i = min(pos)
            if i == 0:
                pos.remove(0)
                if len(pos)>0:
                    tag = tag[1:min(pos)]
                else:
                    tag = tag[1:]
            else:
                tag = tag[:i]
        return tag
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
        self.frequency = 1
        self.prob = 0.0

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
        print ("  %.2f" % self.prob)

# the Grammar has a set of rules. I separated the rules that have terminals 
# in the right hand side from the other formed only by Variables.
class Grammar(object):
    def __init__(self, rules):
        self.rules = []
        self.terminalRules = []
        self.variablesFreq = {}

    def hasRule(self, rule):
        if rule in self.rules:
            self.rules[self.rules.index(rule)].frequency += 1
            return True
        else:
            return False
    
    def hasTerminalRule(self, rule):
        if rule in self.terminalRules:
            self.terminalRules[self.terminalRules.index(rule)].frequency += 1
            return True
        else:
            return False

    def addRule(self, newRule):
        self.addVar(newRule.left.tag)
        if newRule.right[0].type == Symbol.Terminal:
            if not self.hasTerminalRule(newRule):
                bisect.insort(self.terminalRules, newRule)
        else:
            if not self.hasRule(newRule):
                bisect.insort(self.rules, newRule)

    def addVar(self, var):
        if not var in self.variablesFreq:
            self.variablesFreq[var] = 1
        else:
            self.variablesFreq[var] += 1

    def calculateProbs(self):
        for rule in self.rules:
            rule.prob = rule.frequency / self.variablesFreq[rule.left.tag]
        for rule in self.terminalRules:
            rule.prob = rule.frequency / self.variablesFreq[rule.left.tag]

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
    i = 0
    for sentence in treebank:
        print("processing sentence %d" % i)
        i = i+1
        processSentence(grammar, sentence, True)
    
    grammar.calculateProbs()

    return grammar


# recursive function that read each sentence and add the rules to
# the grammar
def processSentence(grammar, tree, first):
    if first: # first iteration (first variable in the parse tree)
        s = Symbol( getTag(tree.label()) , Symbol.StartSymbol )
    else:
        s = Symbol( getTag(tree.label()) , Symbol.Variable )
    rightSide = []
    
    #  the function runs over each child of the current node
    for subTree in tree:
        
        # this is the recursive case. the function finds that the node's child
        # is another tree so it calls itself again to process this tree
        if isinstance(subTree, Tree):
            # if (getTag(subTree.label()).isalpha()):
            if any(c.isalpha() for c in getTag(subTree.label()) ):
                rightSide.append( Symbol( getTag(subTree.label()), Symbol.Variable ) )
                processSentence(grammar,subTree, False)
        
        # the first base case actually handles malformed trees where
        # the terminals are tuples instead of strings
        elif isinstance(subTree,tuple):
            # if (getTag(subTree[1]).isalpha()):
            if any(c.isalpha() for c in getTag(subTree[1])):
                v = Symbol( getTag(subTree[1]), Symbol.Variable )
                t = Symbol( subTree[0], Symbol.Terminal )
                rightSide.append( Symbol( getTag(subTree[1]), Symbol.Variable ) )
                grammar.addRule(Rule(v, [t]))
        
        # the base case. the function finds a terminal which is a string
        elif isinstance(subTree,str):
            rightSide.append( Symbol(subTree, Symbol.Terminal) )
                
    if len(rightSide)>0:
        r = Rule(s, rightSide)
        grammar.addRule(r)

    








