#!/usr/bin/env python

# From: https://gist.github.com/zyga/5534776#gistcomment-3742655

#
# parsing pactl list
#

from pyparsing import *
import os
from subprocess import check_output
import sys

indentStack = [1]
stmt = Forward()
NL = LineEnd()

identifier = Word(alphas, alphanums+"-_.").setName("identifier").setDebug()

sect_def = Group(Group(identifier) + Suppress("#") + Group(Word(nums)))
inner_section = indentedBlock(stmt, indentStack)
section = (sect_def + inner_section)

value_label = originalTextFor(OneOrMore(identifier))
value = Group(value_label
              + Suppress(":")
              + Optional(~NL + Group(Combine(ZeroOrMore(Word(alphanums+'-/=_.') | quotedString(), stopOn=NL)))))
prop_name = Literal("Properties:")
prop_section = indentedBlock(stmt, indentStack)
prop_val_value = Combine(OneOrMore(Word(alphas, alphanums+'-/.') | quotedString(), stopOn=NL))
prop_val = Group(identifier + Suppress("=") + Group(prop_val_value))
prop = (prop_name + prop_section)

stmt << ( section | prop | value | prop_val )

syntax = OneOrMore(stmt)

env = os.environ.copy()
env['LANG'] = 'C'
data = check_output(
    ['pactl', 'list'], universal_newlines=True, env=env)

if len(sys.argv) == 1:
  count = -1
else:
  count = int(sys.argv[1])

if count == -1:
  partial = data
else:
  partial = '\n'.join(data.split('\n')[:count])
print(partial)
parseTree = syntax.parseString(partial)
parseTree.pprint()
#print(parseTree.dump())
