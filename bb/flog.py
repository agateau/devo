# encoding: utf-8
"""
Fancy log
"""
import colors
import sys

def h1(txt, *args):
    _heading(1, txt, *args)

def h2(txt, *args):
    _heading(2, txt, *args)

def error(txt, *args):
    print colors.RESET + colors.RED + (txt % args) + colors.RESET

def p(txt, *args):
    print txt % args

def li(txt, *args):
    print "•", txt % args

def _heading(level, txt, *args):
    sys.stdout.write(colors.BOLD)
    sys.stdout.write(colors.GREEN)
    if level == 1:
        print colors.BOLD
    print "#" * level, txt % args
    print colors.RESET
