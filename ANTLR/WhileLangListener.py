# Generated from WhileLang.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .WhileLangParser import WhileLangParser
else:
    from WhileLangParser import WhileLangParser

# This class defines a complete listener for a parse tree produced by WhileLangParser.
class WhileLangListener(ParseTreeListener):

    # Enter a parse tree produced by WhileLangParser#program.
    def enterProgram(self, ctx:WhileLangParser.ProgramContext):
        pass

    # Exit a parse tree produced by WhileLangParser#program.
    def exitProgram(self, ctx:WhileLangParser.ProgramContext):
        pass


    # Enter a parse tree produced by WhileLangParser#stat.
    def enterStat(self, ctx:WhileLangParser.StatContext):
        pass

    # Exit a parse tree produced by WhileLangParser#stat.
    def exitStat(self, ctx:WhileLangParser.StatContext):
        pass


    # Enter a parse tree produced by WhileLangParser#condition.
    def enterCondition(self, ctx:WhileLangParser.ConditionContext):
        pass

    # Exit a parse tree produced by WhileLangParser#condition.
    def exitCondition(self, ctx:WhileLangParser.ConditionContext):
        pass


    # Enter a parse tree produced by WhileLangParser#expression.
    def enterExpression(self, ctx:WhileLangParser.ExpressionContext):
        pass

    # Exit a parse tree produced by WhileLangParser#expression.
    def exitExpression(self, ctx:WhileLangParser.ExpressionContext):
        pass


    # Enter a parse tree produced by WhileLangParser#term.
    def enterTerm(self, ctx:WhileLangParser.TermContext):
        pass

    # Exit a parse tree produced by WhileLangParser#term.
    def exitTerm(self, ctx:WhileLangParser.TermContext):
        pass


    # Enter a parse tree produced by WhileLangParser#body.
    def enterBody(self, ctx:WhileLangParser.BodyContext):
        pass

    # Exit a parse tree produced by WhileLangParser#body.
    def exitBody(self, ctx:WhileLangParser.BodyContext):
        pass


    # Enter a parse tree produced by WhileLangParser#assignment.
    def enterAssignment(self, ctx:WhileLangParser.AssignmentContext):
        pass

    # Exit a parse tree produced by WhileLangParser#assignment.
    def exitAssignment(self, ctx:WhileLangParser.AssignmentContext):
        pass


    # Enter a parse tree produced by WhileLangParser#comp_op.
    def enterComp_op(self, ctx:WhileLangParser.Comp_opContext):
        pass

    # Exit a parse tree produced by WhileLangParser#comp_op.
    def exitComp_op(self, ctx:WhileLangParser.Comp_opContext):
        pass


    # Enter a parse tree produced by WhileLangParser#logical_op.
    def enterLogical_op(self, ctx:WhileLangParser.Logical_opContext):
        pass

    # Exit a parse tree produced by WhileLangParser#logical_op.
    def exitLogical_op(self, ctx:WhileLangParser.Logical_opContext):
        pass



del WhileLangParser