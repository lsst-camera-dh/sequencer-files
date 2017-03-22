#
# Grammar for the REB3 sequencer language
# (sequencer with variables)
#
# Author: Laurent Le Guillou

import re

class SeqParser(object):

    #-----------------------------------------------------------------------

    # ZMSP ::= [ \t]* # zero or more spaces
    _p_zmsp = "([ \t]*)"

    # OMSP ::= [ \t]+ # one or more spaces
    _p_omsp = "([ \t]+)"

    # NEWLINE ::= (\n | \r\n | \r) # newline
    _p_newline = "(\n|\r\n|\r)"

    # COMMENT ::= '#' .*  [until NEWLINE]
    # _p_comment = "\#(\.*)$"
    _p_comment = "#(.*)"
    
    # INTEGER ::= [0-9]+
    _p_integer = "(\d+)"

    # ADDRESS ::= ((0x)?[0-9a-f]+)
    _p_address = "((0x)?[0-9a-f]+)"
    
    # NAME ::= [A-Za-z][0-9A-Za-z\_]*
    _p_name = "([A-Za-z][\dA-Za-z\_]*)"

    # DURATION_UNIT ::= ( 'ns' | 'us' | 'ms' | 's' )
    _p_duration_unit = "(ns|us|ms|s)"

    # FILE ::= [0-9A-Za-z\_\-\.\\\\]*
    _p_file = "([0-9A-Za-z\_\-\.\/]*)"

    #-----------------------------------------------------------------------

    def __init__(self, s, verbose=True):
        self.s = s
        self.length = len(self.s)
        self.verbose = verbose
        
        # compiling patterns
        self.p_zmsp =    re.compile("^" + self._p_zmsp)
        self.p_omsp =    re.compile("^" + self._p_omsp)
        self.p_newline = re.compile("^" + self._p_newline)
        self.p_comment = re.compile("^" + self._p_comment)
        self.p_integer = re.compile("^" + self._p_integer)
        self.p_address = re.compile("^" + self._p_address)
        self.p_name =    re.compile("^" + self._p_name)
        self.p_duration_unit = re.compile("^" + self._p_duration_unit)
        self.p_file = re.compile("^" + self._p_file)

    #=======================================================================

    #-----------------------------------------------------------------------
    # ZMSP ::= [ \t]* # zero or more spaces
    # OMSP ::= [ \t]+ # one or more spaces

    def m_zmsp(self, pos):
        if pos >= self.length:
            return pos

        # Always match, eat spaces
        matches = self.p_zmsp.search(self.s[pos:])
        if matches is None:
            return pos

        l = matches.end()
        pnext = pos + l
        return pnext


    def m_omsp(self, pos):
        # At least on space
        if pos >= self.length:
            return None
        
        matches = self.p_omsp.search(self.s[pos:])
        if matches == None:
            return None

        l = matches.end()
        pnext = pos + l
        return pnext
    
    #-----------------------------------------------------------------------
    # NEWLINE ::= (\n | \r\n | \r)

    def m_newline(self, pos):
        if pos >= self.length:
            return None

        matches = self.p_newline.search(self.s[pos:])
        if matches == None:
            return None

        # start = matches.start()
        l = matches.end()
        pnext = pos + l

        return pnext

    #-----------------------------------------------------------------------
    # COMMENT ::= \#(.*) [NEWLINE]

    def m_comment(self, pos):
        if pos >= self.length:
            return None

        matches = self.p_comment.search(self.s[pos:])
        if matches == None:
            return None

        # start = matches.start()
        l = matches.end()
        comment = matches.group(1)
        pnext = pos + l

        comment = comment.strip()
        
        return pnext, comment

    #-----------------------------------------------------------------------
    # EMPTY_LINE ::= SPACE* COMMENT? NEWLINE

    def m_empty_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r

        return pnext

    def m_empty_lines(self, pos):
        # always match, eat 'empty' (comments included) lines 
        pnext = pos

        while True:
            r = self.m_empty_line(pnext)
            if r == None:
                return pnext
            pnext = r

        return pnext
    
    #-----------------------------------------------------------------------
    # INTEGER ::= [0-9]+

    def m_integer(self, pos):
        pnext = pos

        matches = self.p_integer.search(self.s[pnext:])
        if matches == None:
            return None

        l = matches.end()
        integer = int(matches.group(1))
        pnext = pnext + l

        return (pnext, integer)

    #-----------------------------------------------------------------------
    # ADDRESS ::= ((0x)?[0-9a-f]+)

    def m_address(self, pos):
        pnext = pos

        matches = self.p_integer.search(self.s[pnext:])
        if matches == None:
            return None

        l = matches.end()
        address = int(matches.group(1), 16)
        pnext = pnext + l

        return (pnext, address)

    #-----------------------------------------------------------------------
    # NAME ::= [A-Za-z][0-9A-Za-z\_]*

    def m_name(self, pos):
        pnext = pos

        matches = self.p_name.search(self.s[pnext:])
        if matches == None:
            return None

        l = matches.end()
        name = matches.group(1)
        pnext = pnext + l

        return (pnext, name)

    #-----------------------------------------------------------------------
    # XXX_SECTION_MARKER = "[XXX]" SPACE* COMMENT? NEWLINE

    _p_section_marker = "[%s]"
    
    def m_section_marker(self, pos, section_name):
        pnext = pos

        s_section_marker = self._p_section_marker % section_name
        l = len(s_section_marker)
        
        if ( self.s[pnext:pnext+l] != s_section_marker ):
            return None

        pnext = pnext + l

        pnext = self.m_zmsp(pnext)
        
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, section_name

    #=======================================================================

    #-----------------------------------------------------------------------
    # DURATION_UNIT ::= ( 'ns' | 'us' | 'ms' | 's' )
    # DURATION_VALUE ::= INTEGER SPACE* DURATION_UNIT

    def m_duration_unit(self, pos):
        pnext = pos

        matches = self.p_duration_unit.search(self.s[pos:])
        if matches == None:
            return None

        l = matches.end()
        unit = matches.group(1)
        pnext = pos + l

        return pnext, unit


    def m_duration_value(self, pos):
        pnext = pos

        r = self.m_integer(pnext)
        if r == None:
            return None
        pnext, integer = r

        pnext = self.m_zmsp(pnext)

        r = self.m_duration_unit(pnext)
        if r == None:
            return None
        pnext, unit = r

        return pnext, (integer, unit)

    #=======================================================================

    #-----------------------------------------------------------------------
    # FILE_NAME ::= FILE
    # INCLUDE_DEF_LINE ::= SPACE* FILE_NAME SPACE* COMMENT? NEWLINE
    # INCLUDE_SECTION_MARKER ::= '[includes]' SPACE* COMMENT? NEWLINE

    def m_file_name(self,pos):
        pnext = pos

        matches = self.p_file.search(self.s[pnext:])
        if matches == None:
            return None

        l = matches.end()
        name = matches.group(1)
        pnext = pnext + l

        return (pnext, name)

    def m_include_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        r = self.m_file_name(pnext)
        if r == None:
            return None
        pnext, constant_name = r

        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r

        return pnext, (constant_name, comment)

    #-----------------------------------------------------------------------
    # INCLUDE_SECTION ::=
    #   INCLUDE_SECTION_MARKER ( EMPTY_LINE | INCLUDE_DEF_LINE )*

    def m_include_section(self, pos):
        pnext = pos

        include_defs = []

        r = self.m_section_marker(pnext, "includes")
        if r == None:
            return None
        pnext, section_name = r

        while True:
            r = self.m_empty_line(pnext)
            if r != None:
                pnext = r
                continue

            r = self.m_include_def_line(pnext)
            if r != None:
                pnext, constant_def = r
                include_defs.append(constant_def)
                continue

            break

        return pnext, include_defs

    #=======================================================================

    #-----------------------------------------------------------------------
    # CONSTANT_NAME ::= NAME
    # CONSTANT_VALUE ::= DURATION_VALUE | INTEGER
    # CONSTANT_DEF_LINE ::=
    #   SPACE* CONSTANT_NAME SPACE* ':' CONSTANT_VALUE SPACE* COMMENT? NEWLINE
    #
    # CONSTANT_SECTION_MARKER ::= '[constants]' SPACE* COMMENT? NEWLINE
    #
    # CONSTANT_SECTION ::=
    #   CONSTANT_SECTION_MARKER ( EMPTY_LINE | CONSTANT_DEF_LINE )*

    def m_constant_name(self, pos):
        return self.m_name(pos)

    def m_constant_value(self, pos):
        pnext = pos

        r = self.m_duration_value(pnext)
        if r != None:
            pnext, constant_value = r
            return pnext, constant_value

        r = self.m_integer(pnext)
        if r != None:
            pnext, integer = r
            return pnext, integer

        return None

    def m_constant_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        r = self.m_constant_name(pnext)
        if r == None:
            return None
        pnext, constant_name = r

        pnext = self.m_zmsp(pnext)

        if self.s[pnext] != ':':
            return None
        pnext += 1

        pnext = self.m_zmsp(pnext)

        r = self.m_constant_value(pnext)
        if r == None:
            return None
        pnext, constant_value = r

        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r

        return pnext, (constant_name, constant_value, comment)

    #-----------------------------------------------------------------------
    # CONSTANT_SECTION ::=
    #   CONSTANT_SECTION_MARKER ( EMPTY_LINE | CONSTANT_DEF_LINE )*

    def m_constant_section(self, pos):
        pnext = pos

        constant_defs = []

        r = self.m_section_marker(pnext, "constants")
        if r == None:
            return None
        pnext, section_name = r
        
        while True:
            r = self.m_empty_line(pnext)
            if r != None:
                pnext = r
                continue

            r = self.m_constant_def_line(pnext)
            if r != None:
                pnext, constant_def = r
                constant_defs.append(constant_def)
                continue

            break

        return pnext, constant_defs
                
    #=======================================================================

    #-----------------------------------------------------------------------
    # CLOCK_NAME ::= NAME
    # CLOCK_ID   ::= INTEGER
    # CLOCK_DEF_LINE  ::=
    #   SPACE* CLOCK_NAME SPACE* ':' CLOCK_ID SPACE* COMMENT? NEWLINE
    #
    # CLOCK_SECTION_MARKER ::= '[clocks]' SPACE* COMMENT? NEWLINE
    #
    # CLOCK_SECTION ::= CLOCK_SECTION_MARKER ( EMPTY_LINE | CLOCK_DEF_LINE )*
    #
    
    def m_clock_name(self, pos):
        return self.m_name(pos)

    def m_clock_id(self, pos):
        return self.m_integer(pos)

    def m_clock_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        r = self.m_clock_name(pnext)
        if r == None:
            return None
        pnext, clock_name = r

        pnext = self.m_zmsp(pnext)

        if self.s[pnext] != ':':
            return None
        pnext += 1

        pnext = self.m_zmsp(pnext)

        r = self.m_clock_id(pnext)
        if r == None:
            return None
        pnext, clock_id_s = r
        clock_id = int(clock_id_s)

        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, (clock_name, clock_id, comment)
    
    #-----------------------------------------------------------------------
    # CLOCK_SECTION ::= CLOCK_SECTION_MARKER ( EMPTY_LINE | CLOCK_DEF_LINE )*

    def m_clock_section(self, pos):
        pnext = pos

        clock_defs = []

        r = self.m_section_marker(pnext, "clocks")
        if r == None:
            return None
        pnext, section_name = r
        
        while True:
            r = self.m_empty_line(pnext)
            if r != None:
                pnext = r
                continue

            r = self.m_clock_def_line(pnext)
            if r != None:
                pnext, clock_def = r
                clock_defs.append(clock_def)
                continue

            break

        return pnext, clock_defs
                
    #=======================================================================
    #
    # REP_FUNC_NAME ::= NAME
    # REP_SUBR_NAME ::= NAME
    # PTR_FUNC_NAME ::= NAME
    # PTR_SUBR_NAME ::= NAME
    #
    
    def m_rep_func_name(self, pos):
        return self.m_name(pos)

    def m_rep_subr_name(self, pos):
        return self.m_name(pos)

    def m_ptr_func_name(self, pos):
        return self.m_name(pos)

    def m_ptr_subr_name(self, pos):
        return self.m_name(pos)

    #-----------------------------------------------------------------------
    # REP_FUNC_DEF_LINE ::=
    # SPACE* 'REP_FUNC' SPACE+ REP_FUNC_NAME SPACE+ INTEGER SPACE* COMMENT? NEWLINE
    # 

    _s_rep_func_def_keyword = "REP_FUNC"
    
    def m_rep_func_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        l = len(self._s_rep_func_def_keyword)
        
        if ( self.s[pnext:pnext+l] != self._s_rep_func_def_keyword ):
            return None
        pnext = pnext + l

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_rep_func_name(pnext)
        if r == None:
            return None
        pnext, rep_func_name = r

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_integer(pnext)
        if r == None:
            return None
        pnext, rep_func_value = r
        
        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, ('REP_FUNC', rep_func_name, rep_func_value, comment)

    #-----------------------------------------------------------------------
    # REP_SUBR_DEF_LINE ::=
    # SPACE* 'REP_SUBR' SPACE+ REP_SUBR_NAME SPACE+ INTEGER SPACE* COMMENT? NEWLINE
    # 

    _s_rep_subr_def_keyword = "REP_SUBR"
    
    def m_rep_subr_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        l = len(self._s_rep_subr_def_keyword)
        
        if ( self.s[pnext:pnext+l] != self._s_rep_subr_def_keyword ):
            return None
        pnext = pnext + l

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_rep_subr_name(pnext)
        if r == None:
            return None
        pnext, rep_subr_name = r

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_integer(pnext)
        if r == None:
            return None
        pnext, rep_subr_value = r
        
        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, ('REP_SUBR', rep_subr_name, rep_subr_value, comment)
    
    #-----------------------------------------------------------------------
    # PTR_FUNC_DEF_LINE ::=
    # SPACE* 'PTR_FUNC' SPACE+ PTR_FUNC_NAME SPACE+ (FUNC_NAME | FUNC_ID) SPACE* COMMENT? NEWLINE
    #

    _s_ptr_func_def_keyword = "PTR_FUNC"
    
    def m_ptr_func_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        l = len(self._s_ptr_func_def_keyword)
        if ( self.s[pnext:pnext+l] != self._s_ptr_func_def_keyword ):
            return None
        pnext = pnext + l

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_ptr_func_name(pnext)
        if r == None:
            return None
        pnext, ptr_func_name = r

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_func_name(pnext)
        if r != None:
            pnext, func = r
        else:
            r = self.m_func_id(pnext)
            if r == None:
                return None
            pnext, func = r
            
        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, ('PTR_FUNC', ptr_func_name, func, comment)
    

    #-----------------------------------------------------------------------
    # PTR_SUBR_DEF_LINE ::=
    # SPACE* 'PTR_SUBR' SPACE+ PTR_SUBR_NAME SPACE+ (SUBR_NAME | ADDRESS) SPACE* COMMENT? NEWLINE
    #

    _s_ptr_subr_def_keyword = "PTR_SUBR"
    
    def m_ptr_subr_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        l = len(self._s_ptr_subr_def_keyword)
        if ( self.s[pnext:pnext+l] != self._s_ptr_subr_def_keyword ):
            return None
        pnext = pnext + l

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_ptr_subr_name(pnext)
        if r == None:
            return None
        pnext, ptr_subr_name = r

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_subr_name(pnext)
        if r != None:
            pnext, subr = r
        else:
            r = self.m_address(pnext)
            if r == None:
                return None
            pnext, subr = r
            
        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, ('PTR_SUBR', ptr_subr_name, subr, comment)

    #-----------------------------------------------------------------------
    # MAIN_DEF_LINE ::=
    # SPACE* 'MAIN' SPACE+ PTR_SUBR_NAME SPACE+ (SUBR_NAME | ADDRESS) SPACE* COMMENT? NEWLINE
    #

    _s_main_def_keyword = "MAIN"

    def m_main_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        l = len(self._s_main_def_keyword)
        if ( self.s[pnext:pnext+l] != self._s_main_def_keyword ):
            return None
        pnext = pnext + l

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_ptr_subr_name(pnext)
        if r == None:
            return None
        pnext, ptr_subr_name = r

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r

        r = self.m_subr_name(pnext)
        if r != None:
            pnext, subr = r
        else:
            r = self.m_address(pnext)
            if r == None:
                return None
            pnext, subr = r

        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r

        return pnext, ('MAIN', ptr_subr_name, subr, comment)


    # PTR_SECTION_MARKER ::= '[pointers]' SPACE* COMMENT? NEWLINE
    #
    # PTR_SECTION ::=
    #   PTR_SECTION_MARKER ( EMPTY_LINE | PTR_DEF_LINE )*
    #
    # PTR_DEF_LINE ::=  ( REP_FUNC_DEF_LINE | REP_SUBR_DEF_LINE |
    #                     PTR_FUNC_DEF_LINE | PTR_SUBR_DEF_LINE )


    def m_ptr_section(self, pos):
        pnext = pos

        rep_func_defs = []
        rep_subr_defs = []
        ptr_func_defs = []
        ptr_subr_defs = []
        main_def = []

        r = self.m_section_marker(pnext, "pointers")
        if r == None:
            return None
        pnext, section_name = r
        
        while True:
            r = self.m_empty_line(pnext)
            if r != None:
                pnext = r
                continue

            r = self.m_rep_func_def_line(pnext)
            if r != None:
                pnext, rep_func_def = r
                rep_func_defs.append(rep_func_def)
                continue

            r = self.m_rep_subr_def_line(pnext)
            if r != None:
                pnext, rep_subr_def = r
                rep_subr_defs.append(rep_subr_def)
                continue

            r = self.m_ptr_func_def_line(pnext)
            if r != None:
                pnext, ptr_func_def = r
                ptr_func_defs.append(ptr_func_def)
                continue

            r = self.m_ptr_subr_def_line(pnext)
            if r != None:
                pnext, ptr_subr_def = r
                ptr_subr_defs.append(ptr_subr_def)
                continue
            
            r = self.m_main_def_line(pnext)
            if r != None:
                pnext, ptr_subr_def = r
                main_def.append(ptr_subr_def)
                continue
            break

        return pnext, (rep_func_defs, rep_subr_defs, ptr_func_defs, ptr_subr_defs, main_def)
    
    #=======================================================================
    #
    # FUNC_NAME ::= NAME
    #
    # FUNC_ID ::= INTEGER
    #
    # FUNC_NAME_DEF_LINE ::=
    #   SPACE* FUNC_NAME SPACE* ':' SPACE* COMMENT? NEWLINE
    #
    # FUNC_CLOCKS_MARKER ::= 'clocks'
    #
    # FUNC_CLOCKS_NAMES_LINE ::=
    #   SPACE* FUNC_CLOCKS_MARKER SPACE* ':'
    #   SPACE* CLOCK_NAME SPACE* (',' SPACE* CLOCK_NAME SPACE*)*
    #
    # FUNC_SLICES_MARKER ::= 'slices'
    # 
    # FUNC_SLICES_MARKER_LINE ::=
    #   SPACE* FUNC_SLICES_MARKER SPACE* ':' SPACE* COMMENT? NEWLINE
    #
    # FUNC_SLICE_DEF_LINE ::=
    #   SPACE* ( DURATION_VALUE | CONSTANT_NAME ) SPACE* '='
    #   SPACE* ( '0' | '1' ) SPACE* (',' SPACE* ( '0' | '1' ) SPACE* )*
    #   SPACE* COMMENT? NEWLINE
    # 
    # FUNC_SLICES_DEFS_BLOCK ::=
    #   FUNC_SLICES_MARKER_LINE
    #   EMPTY_LINE*
    #   FUNC_SLICE_DEF_LINE
    #   ( FUNC_SLICE_DEF_LINE | EMPTY_LINE )*
    #
    # FUNC_CONSTANTS_MARKER ::= 'constants'
    #
    # FUNC_CONSTANTS_DEFS_LINE ::=
    #   SPACE* FUNC_CONSTANTS_MARKER SPACE* ':'
    #   SPACE* CLOCK_NAME SPACE* '=' SPACE* ( '0' | '1' )
    #   (',' SPACE* CLOCK_NAME SPACE* '=' SPACE* ( '0' | '1' ) )*
    #   SPACE* COMMENT? NEWLINE
    # 
    # FUNC_DEF_BLOCK ::=
    #   FUNC_NAME_DEF_LINE
    #   EMPTY_LINE*
    #   FUNC_CLOCKS_NAMES_LINE
    #   EMPTY_LINE*
    #   FUNC_SLICES_DEFS_BLOCK
    #   EMPTY_LINE*
    #   FUNC_CONSTANTS_DEFS_LINE?
    #   EMPTY_LINE*
    #

    #-----------------------------------------------------------------------
    # FUNC_ID ::= INTEGER

    def m_func_id(self, pos):
        return self.m_integer(pos)

    #-----------------------------------------------------------------------
    # FUNC_NAME ::= NAME

    def m_func_name(self, pos):
        return self.m_name(pos)

    #-----------------------------------------------------------------------
    # FUNC_NAME_DEF_LINE ::=
    #   SPACE* FUNC_NAME SPACE* ':' SPACE* COMMENT? NEWLINE

    def m_func_name_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        r = self.m_func_name(pnext)
        if r == None:
            return None
        pnext, func_name = r

        pnext = self.m_zmsp(pnext)

        if self.s[pnext] != ':':
            return None
        pnext += 1

        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, (func_name, comment)

    #-----------------------------------------------------------------------
    # FUNC_CLOCKS_MARKER ::= 'clocks'
    #
    # FUNC_CLOCKS_NAMES_LINE ::=
    #   SPACE* FUNC_CLOCKS_MARKER SPACE* ':'
    #   SPACE* CLOCK_NAME SPACE* (',' SPACE* CLOCK_NAME SPACE*)*
    #

    _s_func_clocks_marker = "clocks"
    
    def m_func_clocks_names_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        l = len(self._s_func_clocks_marker)
        if self.s[pnext:pnext+l] != self._s_func_clocks_marker:
            return None
        pnext += l

        pnext = self.m_zmsp(pnext)

        if self.s[pnext] != ':':
            return None
        pnext += 1
        
        pnext = self.m_zmsp(pnext)

        clock_names = []
        
        r = self.m_clock_name(pnext)
        if r == None:
            return None
        pnext, clock_name = r
        clock_names.append(clock_name)
        
        while True:
            pnext = self.m_zmsp(pnext)

            if self.s[pnext] != ',':
                break
            pnext += 1
            
            pnext = self.m_zmsp(pnext)

            r = self.m_clock_name(pnext)
            if r == None:
                return None
            pnext, clock_name = r
            clock_names.append(clock_name)
    
        pnext = self.m_zmsp(pnext)
        if self.verbose:
            print pnext

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, clock_names
        
    #-----------------------------------------------------------------------
    # FUNC_SLICES_MARKER ::= 'slices'
    # 
    # FUNC_SLICES_MARKER_LINE ::=
    #   SPACE* FUNC_SLICES_MARKER SPACE* ':' SPACE* COMMENT? NEWLINE
    #
    # FUNC_SLICE_DEF_LINE ::=
    #   SPACE* ( DURATION_VALUE | CONSTANT_NAME ) SPACE* '='
    #   SPACE* ( '0' | '1' ) SPACE* (',' SPACE* ( '0' | '1' ) SPACE* )*
    #   SPACE* COMMENT? NEWLINE
    # 
    # FUNC_SLICES_DEFS_BLOCK ::=
    #   FUNC_SLICES_MARKER_LINE
    #   EMPTY_LINE*
    #   FUNC_SLICE_DEF_LINE
    #   ( FUNC_SLICE_DEF_LINE | EMPTY_LINE )*

    _s_func_slices_marker = "slices"

    def m_func_slices_marker_line(self, pos):
        if pos >= self.length:
            return None

        pnext = pos

        pnext = self.m_zmsp(pnext)

        l = len(self._s_func_slices_marker)
        if self.s[pnext:pnext+l] != self._s_func_slices_marker:
            return None
        pnext += l

        pnext = self.m_zmsp(pnext)

        if self.s[pnext] != ':':
            return None
        pnext += 1
        
        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext
    
    #-----------------------------------------------------------------------
    # FUNC_SLICE_DEF_LINE ::=
    #   SPACE* ( DURATION_VALUE | CONSTANT_NAME ) SPACE* '='
    #   SPACE* ( '0' | '1' ) SPACE* (',' SPACE* ( '0' | '1' ) SPACE* )*
    #   SPACE* COMMENT? NEWLINE

    def m_func_slice_def_line(self, pos):
        if pos >= self.length:
            return None

        pnext = pos

        pnext = self.m_zmsp(pnext)

        r = self.m_duration_value(pnext)
        if r != None:
            pnext, duration = r
        else:
            r = self.m_constant_name(pnext)
            if r == None:
                return None
            pnext, duration = r
        
        pnext = self.m_zmsp(pnext)

        if self.s[pnext] != '=':
            return None
        pnext += 1
        
        pnext = self.m_zmsp(pnext)

        clock_line_values = []
        
        if self.s[pnext] not in ['0', '1']:
            return None
        clock_line_value = int(self.s[pnext])
        clock_line_values.append(clock_line_value)
        pnext += 1

        while True:
            pnext = self.m_zmsp(pnext)

            if self.s[pnext] != ',':
                break
            pnext += 1
            
            pnext = self.m_zmsp(pnext)

            if self.s[pnext] not in ['0', '1']:
                return None
            clock_line_value = int(self.s[pnext])
            clock_line_values.append(clock_line_value)
            pnext += 1
    
        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, (duration, clock_line_values)

    #-----------------------------------------------------------------------
    # FUNC_SLICES_DEFS_BLOCK ::=
    #   FUNC_SLICES_MARKER_LINE
    #   EMPTY_LINE*
    #   FUNC_SLICE_DEF_LINE
    #   ( FUNC_SLICE_DEF_LINE | EMPTY_LINE )*

    def m_func_slices_defs_block(self, pos):
        pnext = pos

        slice_defs = []

        r = self.m_func_slices_marker_line(pnext)
        if r == None:
            return None
        pnext = r
        
        while True:
            r = self.m_empty_line(pnext)
            if r != None:
                pnext = r
                continue

            r = self.m_func_slice_def_line(pnext)
            if r != None:
                pnext, slice_def = r
                slice_defs.append(slice_def)
                continue

            break

        return pnext, slice_defs

    #-----------------------------------------------------------------------
    # FUNC_CONSTANTS_MARKER ::= 'constants'
    #
    # FUNC_CONSTANTS_DEFS_LINE ::=
    #   SPACE* FUNC_CONSTANTS_MARKER SPACE* ':'
    #   SPACE* CLOCK_NAME SPACE* '=' SPACE* ( '0' | '1' )
    #   (',' SPACE* CLOCK_NAME SPACE* '=' SPACE* ( '0' | '1' ) )*
    #   SPACE* COMMENT? NEWLINE

    _s_func_constants_marker = "constants"

    def m_func_constants_defs_line(self, pos):
        pnext = pos

        func_constants_defs = []

        pnext = self.m_zmsp(pnext)

        l = len(self._s_func_constants_marker)
        if self.s[pnext:pnext+l] != self._s_func_constants_marker:
            return None
        pnext += l

        pnext = self.m_zmsp(pnext)

        if self.s[pnext] != ':':
            return None
        pnext += 1
        
        pnext = self.m_zmsp(pnext)

        # ---------------------------------
        
        while True:
            pnext = self.m_zmsp(pnext)
        
            r = self.m_clock_name(pnext)
            if r == None:
                return None
            pnext, clock_name = r

            pnext = self.m_zmsp(pnext)

            if self.s[pnext] != '=':
                return None
            pnext += 1

            pnext = self.m_zmsp(pnext)

            if self.s[pnext] not in ['0', '1']:
                return None
            clock_line_value = int(self.s[pnext])
            func_constant_def = (clock_name, clock_line_value)
            func_constants_defs.append(func_constant_def)
            pnext += 1

            pnext = self.m_zmsp(pnext)
        
            if self.s[pnext] != ',':
                break
            pnext += 1
            
        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, func_constants_defs

    #-----------------------------------------------------------------------
    # FUNC_DEF_BLOCK ::=
    #   FUNC_NAME_DEF_LINE
    #   EMPTY_LINE*
    #   FUNC_CLOCKS_NAMES_LINE
    #   EMPTY_LINE*
    #   FUNC_SLICES_DEFS_BLOCK
    #   EMPTY_LINE*
    #   FUNC_CONSTANTS_DEFS_LINE?
    #   EMPTY_LINE*

    def m_func_def_block(self, pos):
        pnext = pos

        func = { 'name': None,
                 'comment': None,
                 'clocks': None,
                 'slices': None,
                 'constants': None }

        r = self.m_func_name_def_line(pnext)
        if r == None:
            return None
        pnext, (func_name, func_comment) = r

        pnext = self.m_empty_lines(pnext)
        
        r = self.m_func_clocks_names_line(pnext)
        if r == None:
            return None
        pnext, clock_names = r

        pnext = self.m_empty_lines(pnext)

        r = self.m_func_slices_defs_block(pnext)
        if r == None:
            return None
        pnext, slices_defs = r

        pnext = self.m_empty_lines(pnext)

        func_constants_defs = None
        r = self.m_func_constants_defs_line(pnext)
        if r != None:
            pnext, func_constants_defs = r

        pnext = self.m_empty_lines(pnext)
            
        func['name'] = func_name
        func['comment'] = func_comment
        func['clocks'] = clock_names
        func['slices'] = slices_defs
        func['constants'] = func_constants_defs

        return pnext, func
    
    #-----------------------------------------------------------------------
    # FUNC_SECTION ::= FUNC_SECTION_MARKER FUNC_DEF_BLOCK*

    def m_func_section(self, pos):
        pnext = pos

        funcs = []

        pnext = self.m_empty_lines(pnext)

        r = self.m_section_marker(pnext, "functions")
        if r == None:
            return None
        pnext, section_name = r
        
        while True:
            pnext = self.m_empty_lines(pnext)

            r = self.m_func_def_block(pnext)
            if r == None:
                break
            pnext, func = r
            funcs.append(func)

        return pnext, funcs
    
    #-----------------------------------------------------------------------

    #=======================================================================
    #
    # SUBR_NAME ::= NAME
    #
    # INSTR_CALL_LINE ::=
    #   SPACE* 'CALL' SPACE+ ( ( '@' PTR_FUNC ) | FUNC_ID | FUNC_NAME )
    #   ( SPACE+ 'repeat(' + SPACE* + ( ( '@' ( REP_FUNC | ADDRESS ) ) | CONSTANT_NAME | INTEGER | 'Inf' ) + SPACE* + ')' )
    #   SPACE* COMMENT? NEWLINE
    # 
    # INSTR_JSR_LINE ::=
    #   SPACE* 'JSR' SPACE+ ( ( '@' PTR_SUBR ) | SUBR_ADDR | SUBR_NAME )
    #   ( SPACE+ 'repeat(' + SPACE* + ( ( '@' ( REP_SUBR | ADDRESS ) ) | CONSTANT_NAME | INTEGER ) + SPACE* + ')' )
    #   SPACE* COMMENT? NEWLINE
    #
    # INSTR_RTS_LINE ::=
    #   SPACE* 'RTS' SPACE* COMMENT? NEWLINE
    #
    # INSTR_END_LINE ::=
    #   SPACE* 'END' SPACE* COMMENT? NEWLINE
    #
    # SUBR_NAME_DEF_LINE ::=
    #   SPACE* SUBR_NAME SPACE* ':' SPACE* COMMENT? NEWLINE
    #
    # SUBR_DEF_BLOCK ::=
    #   SUBR_NAME_DEF_LINE
    #   ( INSTR_CALL_LINE | INSTR_JSR_LINE )*
    #   INSTR_RTS_LINE 
    #
    # MAIN_DEF_BLOCK ::=
    #   SUBR_NAME_DEF_LINE
    #   ( INSTR_CALL_LINE | INSTR_JSR_LINE )*
    #   INSTR_END_LINE 
    # 
    #-----------------------------------------------------------------------
    # SUBR_NAME ::= NAME

    def m_subr_name(self, pos):
        return self.m_name(pos)

    #-----------------------------------------------------------------------
    # INSTR_CALL_FUNC_REF_PTR ::=  '@' ( PTR_FUNC_NAME | ADDRESS ) 
    # INSTR_CALL_FUNC_REF_DIR ::=  FUNC_ID | FUNC_NAME 
    # INSTR_CALL_FUNC_REF ::=  INSTR_CALL_FUNC_REF_PTR | INSTR_CALL_FUNC_REF_DIR
    
    def m_instr_call_func_ref_ptr(self, pos):
        pnext = pos

        if self.s[pnext] != '@':
            return None
        pnext += 1

        r = self.m_ptr_func_name(pnext)
        if r != None:
            pnext, ptr_func = r
            return pnext, ('PTR_FUNC', ptr_func)

        r = self.m_address(pnext)
        if r == None:
            return None
        pnext, address = r
        return pnext, ('ADDRESS', address)


    def m_instr_call_func_ref_dir(self, pos):
        pnext = pos

        r = self.m_func_id(pnext)
        if r != None:
            pnext, func_id = r
            return pnext, ('FUNC_ID', func_id)

        r = self.m_func_name(pnext)
        if r == None:
            return None
        pnext, func_name = r
        return pnext, ('FUNC_NAME', func_name)


    def m_instr_call_func_ref(self, pos):
        pnext = pos

        r = self.m_instr_call_func_ref_ptr(pnext)
        if r != None:
            pnext, func_ref = r
            return pnext, func_ref

        r = self.m_instr_call_func_ref_dir(pnext)
        if r == None:
            return None
        pnext, func_ref = r
        return pnext, func_ref
        
    #-----------------------------------------------------------------------
    # INSTR_CALL_REP_REF_PTR ::=  '@' ( REP_FUNC_NAME | ADDRESS ) 
    # INSTR_CALL_REP_REF_DIR ::=  CONSTANT_NAME | 'Inf' | INTEGER 
    # INSTR_CALL_REP_REF ::=  INSTR_CALL_REP_REF_PTR | INSTR_CALL_REP_REF_DIR
    # INSTR_CALL_REP ::= 'repeat(' SPACE* INSTR_CALL_REP_REF SPACE* ')'

    
    def m_instr_call_rep_ref_ptr(self, pos):
        pnext = pos

        if self.s[pnext] != '@':
            return None
        pnext += 1

        r = self.m_rep_func_name(pnext)
        if r != None:
            pnext, rep_func_name = r
            return pnext, ("REP_FUNC", rep_func_name)
    
        r = self.m_address(pnext)
        if r == None:
            return None
        pnext, address = r
        return pnext, ("ADDRESS", address)
        
    
    _s_inf = "infinity"

    def m_instr_call_rep_ref_dir(self, pos):
        pnext = pos

        l = len(self._s_inf)
        if self.s[pnext:pnext+l] == self._s_inf:
            pnext += l
            return pnext, ("INFINITY", "Inf")

        r = self.m_integer(pnext)
        if r != None:
            pnext, rep = r
            return pnext, ("INTEGER", rep)

        r = self.m_constant_name(pnext)
        if r != None:
            pnext, constant_name = r
            return pnext, ("CONSTANT_NAME", constant_name)

        return None

    
    def m_instr_call_rep_ref(self, pos):
        pnext = pos

        r = self.m_instr_call_rep_ref_ptr(pnext)
        if r != None:
            pnext, rep_ref = r
            return pnext, rep_ref

        r = self.m_instr_call_rep_ref_dir(pnext)
        if r != None:
            pnext, rep_ref = r
            return pnext, rep_ref

        return None
        
    #-----------------------------------------------------------------------
    
    _s_repeat_start = "repeat("
    _s_repeat_end = ")"

    def m_instr_call_rep(self, pos):
        pnext = pos

        l = len(self._s_repeat_start)
        if self.s[pnext:pnext+l] != self._s_repeat_start:
            return None
        pnext += l

        pnext = self.m_zmsp(pnext)
        
        r = self.m_instr_call_rep_ref(pnext)
        if r == None:
            return None
        pnext, rep = r

        pnext = self.m_zmsp(pnext)
        
        if self.s[pnext] != self._s_repeat_end:
            return None
        pnext += 1
        
        return pnext, rep
        
    #-----------------------------------------------------------------------
    # INSTR_CALL_LINE ::=
    #   SPACE* 'CALL' SPACE+ INSTR_CALL_FUNC_REF
    #   ( SPACE+ INSTR_CALL_REP )?
    #   SPACE* COMMENT? NEWLINE

    _s_instr_call_opname = "CALL"
    
    def m_instr_call_line(self, pos):
        pnext = pos

        call_instr = { 'opname': 'CALL', 'func': None, 'repeat': 1 }
        
        pnext = self.m_zmsp(pnext)
        # print [1], pnext
        
        l = len(self._s_instr_call_opname)
        if self.s[pnext:pnext+l] != self._s_instr_call_opname:
            return None
        pnext += l
        # print [2], pnext

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r
        # print [3], pnext
        
        r = self.m_instr_call_func_ref(pnext)
        if r == None:
            return None
        pnext, func_ref = r
        call_instr['func'] = func_ref
        # print [4], pnext, func_ref
        
        r = self.m_omsp(pnext)
        if r != None:
            pnext = r
            r = self.m_instr_call_rep(pnext)
            if r != None:
                pnext, func_rep = r
                call_instr['repeat'] = func_rep
                # print [5], pnext, func_rep

        pnext = self.m_zmsp(pnext)
        # print [6], pnext
        
        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r
        # print [7], pnext, comment

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        # print [8], pnext
        
        return pnext, call_instr



    #=======================================================================

    #-----------------------------------------------------------------------
    # INSTR_JSR_SUBR_REF_PTR ::=  '@' ( PTR_SUBR_NAME | ADDRESS ) 
    # INSTR_JSR_SUBR_REF_DIR ::=  SUBR_NAME | ADDRESS
    # INSTR_JSR_SUBR_REF ::=  INSTR_JSR_SUBR_REF_PTR | INSTR_JSR_SUBR_REF_DIR
    
    def m_instr_jsr_subr_ref_ptr(self, pos):
        pnext = pos

        if self.s[pnext] != '@':
            return None
        pnext += 1

        r = self.m_ptr_subr_name(pnext)
        if r != None:
            pnext, ptr_subr = r
            return pnext, ('PTR_SUBR', ptr_subr)

        r = self.m_address(pnext)
        if r == None:
            return None
        pnext, address = r
        return pnext, ('ADDRESS', address)


    def m_instr_jsr_subr_ref_dir(self, pos):
        pnext = pos

        r = self.m_subr_name(pnext)
        if r != None:
            pnext, subr_name = r
            return pnext, ('SUBR_NAME', subr_name)

        r = self.m_address(pnext)
        if r != None:
            pnext, address = r
            return pnext, ('ADDRESS', address)

        return None
    

    def m_instr_jsr_subr_ref(self, pos):
        pnext = pos

        r = self.m_instr_jsr_subr_ref_ptr(pnext)
        if r != None:
            pnext, subr_ref = r
            return pnext, subr_ref

        r = self.m_instr_jsr_subr_ref_dir(pnext)
        if r != None:
            pnext, subr_ref = r
            return pnext, subr_ref

        return None
        
    #-----------------------------------------------------------------------
    # INSTR_JSR_REP_REF_PTR ::=  '@' ( REP_SUBR_NAME | ADDRESS ) 
    # INSTR_JSR_REP_REF_DIR ::=  INTEGER | CONSTANT_NAME
    # INSTR_JSR_REP_REF ::=  INSTR_JSR_REP_REF_PTR | INSTR_JSR_REP_REF_DIR
    # INSTR_JSR_REP ::= 'repeat(' SPACE* INSTR_CALL_REP_REF SPACE* ')'
    
    def m_instr_jsr_rep_ref_ptr(self, pos):
        pnext = pos

        if self.s[pnext] != '@':
            return None
        pnext += 1

        r = self.m_rep_subr_name(pnext)
        if r != None:
            pnext, rep_subr_name = r
            return pnext, ("REP_SUBR", rep_subr_name)
    
        r = self.m_address(pnext)
        if r != None:
            pnext, address = r
            return pnext, ("ADDRESS", address)

        return None
    

    def m_instr_jsr_rep_ref_dir(self, pos):
        pnext = pos

        r = self.m_integer(pnext)
        if r != None:
            pnext, rep = r
            return pnext, ("INTEGER", rep)

        r = self.m_constant_name(pnext)
        if r != None:
            pnext, constant_name = r
            return pnext, ("CONSTANT_NAME", constant_name)

        return None

    
    def m_instr_jsr_rep_ref(self, pos):
        pnext = pos

        r = self.m_instr_jsr_rep_ref_ptr(pnext)
        if r != None:
            pnext, rep_ref = r
            return pnext, rep_ref

        r = self.m_instr_jsr_rep_ref_dir(pnext)
        if r != None:
            pnext, rep_ref = r
            return pnext, rep_ref

        return None
        
    #-----------------------------------------------------------------------
    
    _s_repeat_start = "repeat("
    _s_repeat_end = ")"

    def m_instr_jsr_rep(self, pos):
        pnext = pos

        l = len(self._s_repeat_start)
        if self.s[pnext:pnext+l] != self._s_repeat_start:
            return None
        pnext += l

        pnext = self.m_zmsp(pnext)
        
        r = self.m_instr_jsr_rep_ref(pnext)
        if r == None:
            return None
        pnext, rep = r

        pnext = self.m_zmsp(pnext)
        
        if self.s[pnext] != self._s_repeat_end:
            return None
        pnext += 1
        
        return pnext, rep
        
    #-----------------------------------------------------------------------
    # INSTR_JSR_LINE ::=
    #   SPACE* 'JSR' SPACE+ INSTR_JSR_FUNC_REF
    #   ( SPACE+ INSTR_JSR_REP )?
    #   SPACE* COMMENT? NEWLINE

    _s_instr_jsr_opname = "JSR"
    
    def m_instr_jsr_line(self, pos):
        pnext = pos

        jsr_instr = { 'opname': 'JSR', 'subr': None, 'repeat': 1 }
        
        pnext = self.m_zmsp(pnext)
        #print [1], pnext
        
        l = len(self._s_instr_jsr_opname)
        if self.s[pnext:pnext+l] != self._s_instr_jsr_opname:
            return None
        pnext += l
        #print [2], pnext

        r = self.m_omsp(pnext)
        if r == None:
            return None
        pnext = r
        #print [3], pnext
        
        r = self.m_instr_jsr_subr_ref(pnext)
        if r == None:
            return None
        pnext, subr_ref = r
        jsr_instr['subr'] = subr_ref
        #print [4], pnext, subr_ref
        
        r = self.m_omsp(pnext)
        if r != None:
            pnext = r
            r = self.m_instr_jsr_rep(pnext)
            if r != None:
                pnext, subr_rep = r
                jsr_instr['repeat'] = subr_rep
                #print [5], pnext, subr_rep

        pnext = self.m_zmsp(pnext)
        #print [6], pnext
        
        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r
        #print [7], pnext, comment

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        #print [8], pnext
        
        return pnext, jsr_instr
    
    #-----------------------------------------------------------------------
    # INSTR_RTS_LINE ::=
    #   SPACE* 'RTS' SPACE* COMMENT? NEWLINE

    _s_instr_rts_opname = "RTS"
    
    def m_instr_rts_line(self, pos):
        pnext = pos

        rts_instr = { 'opname': 'RTS' }
        
        pnext = self.m_zmsp(pnext)
        
        l = len(self._s_instr_rts_opname)
        if self.s[pnext:pnext+l] != self._s_instr_rts_opname:
            return None
        pnext += l

        pnext = self.m_zmsp(pnext)
        
        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, rts_instr
    
    #-----------------------------------------------------------------------
    # INSTR_END_LINE ::=
    #   SPACE* 'END' SPACE* COMMENT? NEWLINE

    _s_instr_end_opname = "END"
    
    def m_instr_end_line(self, pos):
        pnext = pos

        end_instr = { 'opname': 'END' }
        
        pnext = self.m_zmsp(pnext)
        
        l = len(self._s_instr_end_opname)
        if self.s[pnext:pnext+l] != self._s_instr_end_opname:
            return None
        pnext += l

        pnext = self.m_zmsp(pnext)
        
        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, end_instr
    
    #-----------------------------------------------------------------------
    # SUBR_NAME_DEF_LINE ::=
    #   SPACE* SUBR_NAME SPACE* ':' SPACE* COMMENT? NEWLINE
    #
    # SUBR_DEF_BLOCK ::=
    #   SUBR_NAME_DEF_LINE
    #   ( INSTR_CALL_LINE | INSTR_JSR_LINE | EMPTY_LINE )*
    #   INSTR_RTS_LINE 
    #
    # MAIN_DEF_BLOCK ::=
    #   SUBR_NAME_DEF_LINE
    #   ( INSTR_CALL_LINE | INSTR_JSR_LINE | EMPTY_LINE )*
    #   INSTR_END_LINE 

    def m_subr_name_def_line(self, pos):
        pnext = pos

        pnext = self.m_zmsp(pnext)

        r = self.m_subr_name(pnext)
        if r == None:
            return None
        pnext, subr_name = r

        pnext = self.m_zmsp(pnext)

        if self.s[pnext] != ':':
            return None
        pnext += 1

        pnext = self.m_zmsp(pnext)

        comment = ''
        r = self.m_comment(pnext)
        if r != None:
            pnext, comment = r

        r = self.m_newline(pnext)
        if r == None:
            return None
        pnext = r
        
        return pnext, (subr_name, comment)
    

    # SUBR_DEF_BLOCK ::=
    #   SUBR_NAME_DEF_LINE
    #   ( INSTR_CALL_LINE | INSTR_JSR_LINE | EMPTY_LINE )*
    #   INSTR_RTS_LINE 

    # MAIN_DEF_BLOCK ::=
    #   SUBR_NAME_DEF_LINE
    #   ( INSTR_CALL_LINE | INSTR_JSR_LINE | EMPTY_LINE )*
    #   INSTR_END_LINE 


    def m_subr_def_block(self, pos, main = False):
        pnext = pos

        subr_instrs = []

        r = self.m_subr_name_def_line(pnext)
        if r == None:
            return None
        pnext, (subr_name, comment) = r
        
        while True:
            r = self.m_empty_line(pnext)
            if r != None:
                pnext = r
                continue

            r = self.m_instr_call_line(pnext)
            if r != None:
                pnext, instr = r
                subr_instrs.append(instr)
                continue

            r = self.m_instr_jsr_line(pnext)
            if r != None:
                pnext, instr = r
                subr_instrs.append(instr)
                continue
            
            break

        if main:
            r = self.m_instr_end_line(pnext)
        else:
            r = self.m_instr_rts_line(pnext)

        if r == None:
            return None
        pnext, instr = r
        subr_instrs.append(instr)

        pnext = self.m_empty_lines(pnext)
        
        return pnext, { 'name': subr_name, 'comment': comment, 'instrs': subr_instrs }
    

    #-----------------------------------------------------------------------
    # SUBR_SECTION ::= SUBR_SECTION_MARKER SUBR_DEF_BLOCK*
    # MAIN_SECTION ::= MAIN_SECTION_MARKER MAIN_DEF_BLOCK*

    def m_subr_section(self, pos, main = False):
        pnext = pos

        subrs = []

        pnext = self.m_empty_lines(pnext)

        #print [1]
        if main:
            r = self.m_section_marker(pnext, "mains")
        else:
            r = self.m_section_marker(pnext, "subroutines")

        if r == None:
            return None
        pnext, section_name = r
        #print [2]
        
        while True:
            pnext = self.m_empty_lines(pnext)
            #print [3]

            r = self.m_subr_def_block(pnext, main = main)
            if r == None:
                break
            pnext, subr = r
            #print [4], subr
            subrs.append(subr)

        pnext = self.m_empty_lines(pnext)
            
        return pnext, subrs


    #=======================================================================
    # SEQ ::=
    #     CONSTANT_SECTION
    #     CLOCK_SECTION
    #     PTR_SECTION?
    #     FUNC_SECTION
    #     SUBR_SECTION?
    #     MAIN_SECTION

    def m_seq(self, pos):
        pnext = pos

        result = { 'includes': [],
                   'constants': [],
                   'clocks': [],
                   'pointers': [],
                   'functions': [],
                   'subroutines': [],
                   'mains': [] }

        pnext = self.m_empty_lines(pnext)

        if self.verbose:
            print "[includes]"
        r = self.m_include_section(pnext)
        if r == None:
            result['includes'] = []  # keep it optional
        else:
            pnext, result['includes'] = r

        pnext = self.m_empty_lines(pnext)

        if self.verbose:
            print "[constants]"
        r = self.m_constant_section(pnext)
        if r == None:
            return None
        pnext, result['constants'] = r

        pnext = self.m_empty_lines(pnext)

        if self.verbose:
            print "[clocks]"
        r = self.m_clock_section(pnext)
        if r == None:
            return None
        pnext, result['clocks'] = r

        pnext = self.m_empty_lines(pnext)

        if self.verbose:
            print "[pointers]"
        r = self.m_ptr_section(pnext)
        if r != None:
            pnext, result['pointers'] = r

        pnext = self.m_empty_lines(pnext)

        if self.verbose:
            print "[functions]"
        r = self.m_func_section(pnext)
        if r == None:
            return None
        pnext, result['functions'] = r

        pnext = self.m_empty_lines(pnext)

        if self.verbose:
            print "[subroutines]"
        r = self.m_subr_section(pnext)
        if r != None:
            pnext, result['subroutines'] = r

        pnext = self.m_empty_lines(pnext)
            
        if self.verbose:
            print "[mains]"
        r = self.m_subr_section(pnext, main=True)
        if r == None:
            return None
        pnext, result['mains'] = r

        pnext = self.m_empty_lines(pnext)
        
        return result

    #=======================================================================

def merge_section_tuples(stronglist, weaklist, index=0):
    """
    Manages the merge of two sections of results when the sections are lists of tuples.
    :param stronglist:
    :param weaklist:
    :return:
    """
    stronger_defs = [constant_def[index] for constant_def in stronglist]
    for constant_def in weaklist:
        if constant_def[index] not in stronger_defs:
            stronglist.append(constant_def)


def merge_section_dicts(stronglist, weaklist, fieldname):
    """
    Manages the merge of two sections of results when the sections are lists of dicts.
    :param stronglist:
    :param weaklist:
    :return:
    """
    stronger_defs = [constant_def[fieldname] for constant_def in stronglist]
    for constant_def in weaklist:
        if constant_def[fieldname] not in stronger_defs:
            stronglist.append(constant_def)


def merge_result(stronger, weaker):
    """
    Merges two 'result' from the parser, giving priority to the first.
    This modifies the content of the stronger result.
    :param stronger:
    :param weaker:
    :return:
    """
    # includes are managed in the parse_file() function, NOT merged
    merge_section_tuples(stronger['constants'], weaker['constants'])
    merge_section_tuples(stronger['clocks'], weaker['clocks'])

    # tuple of lists, one list per type of pointers
    for i in range(5):
        merge_section_tuples(stronger['pointers'][i], weaker['pointers'][i], 1)

    merge_section_dicts(stronger['functions'], weaker['functions'], 'name')
    merge_section_dicts(stronger['subroutines'], weaker['subroutines'], 'name')
    merge_section_dicts(stronger['mains'], weaker['mains'], 'name')


def parse_file(txtfile, verbose=True):
    """
    Parses input file, manages 'includes' section.
    :param txtfile:
    :return:
    """
    sfile = open(txtfile, 'r')
    s = sfile.read()
    sfile.close()

    seq = SeqParser(s, verbose)
    result = seq.m_seq(0)

    # child values overwrite parents in case of conflict, with inheritance order from [includes]
    # manages recursivity (even though it is a terribly dangerous idea)

    # includes section is a list of tuples (file, comment)
    for parentfile in reversed(result['includes']):
        parentname = parentfile[0]
        print('Including sequencer file: %s ' % parentname)
        parentresult = parse_file(parentname, verbose)
        merge_result(result, parentresult)

    return result


