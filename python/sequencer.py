#! /usr/bin/env python
#
# LSST
# Python objects for the FPGA sequencer
#
# Authors: Laurent Le Guillou, Claire Juramy

import re
import bidi

## -----------------------------------------------------------------------

def setBit(int_type, offset):
    mask = 1 << offset
    return int_type | mask


def clearBit(int_type, offset):
    mask = ~(1 << offset)
    return int_type & mask


class Program(object):
    """
    Internal representation of a 'compiled' FPGA program.
    """

    def __init__(self):
        self.instructions = {}
        self.subroutines = {}

    def __repr__(self):
        s = ""

        addrs = self.instructions.keys()
        addrs.sort()

        last_addr = None
        for addr in addrs:
            if last_addr is not None and (addr != (last_addr + 1)):
                # empty memory area
                s += "\n"
            s += "0x%03x:     " % addr 
            s += repr(self.instructions[addr])
            s += "\n"
            last_addr = addr

        return s

    def bytecode(self):
        """
        Return the 32 bits byte code for the FPGA compiled program.
        (with relative memory addresses)
        """

        instrs = self.instructions
        addrs = instrs.keys()
        addrs.sort()

        bcs = {}
        for addr in addrs:
            instr = instrs[addr]
            bc = instr.bytecode()
            bcs[addr] = bc

        return bcs


class SequencerPointer(object):

    Pointer_types = ['MAIN', 'PTR_FUNC', 'REP_FUNC', 'PTR_SUBR', 'REP_SUBR']
    Exec_pointers = ['PTR_FUNC', 'PTR_SUBR', 'MAIN']
    Repeat_pointers = ['REP_FUNC', 'REP_SUBR']

    # we are using the dictionary instead
    #Execute_Address = 0x340000
    # these four should be incremented when a pointer is added
    #Ptr_Func_Base = 0x350000
    #Rep_Func_Base = 0x360000
    #Ptr_Subr_Base = 0x370000
    #Rep_Subr_Base = 0x380000

    Mapping_Ptr = dict(zip(Pointer_types,
                           [0x340000, 0x350000, 0x360000, 0x370000, 0x380000]))

    def __init__(self, pointertype, name, value=None, target=''):
        """
        Creates the pointer, associating name and location, and initializing content.
        If not available, use target name and compile later.
        Note that target and value are not expected to match later (for now).
        :param pointertype: string for the pointer type
        :param name: pointer name
        :param value: value inside the pointer
        :param target: what we are targeting
        :return:
        """
        if pointertype in self.Pointer_types:
            self.pointer_type = pointertype
        else:
            raise ValueError('Attempting to create pointer with unknown type: %s' % pointertype)
        self.name = name

        if self.pointer_type == 'MAIN':
            self.address = self.Mapping_Ptr['MAIN']
        else:
            ptr_address = self.Mapping_Ptr[self.pointer_type]
            self.address = ptr_address

            if (ptr_address & 0xFF) < 16:
                # this increments the base address for the next instance of the class
                self.Mapping_Ptr[self.pointer_type] += 1
            else:
                raise ValueError('Error: registry for pointers %s is full' % self.pointer_type)

        if value is not None:
            self.value = value
            self.target = target
            #debug
            #print('Creating pointer %s at address %x with value %d' % (self.name, self.address, self.value))
        elif target:
            self.target = target
            #debug
            #print('Creating pointer %s at address %x with target %s' % (self.name, self.address, self.target))
        else:
            raise ValueError('Badly defined pointer: %s, %s' % (pointertype, name))

    def __repr__(self):
        s = "%s %x %s -> " % (self.pointer_type, self.address, self.name)
        if self.value is not None:
            s += "%d " % self.value
        else:
            s += "Undef "
        if self.target:
            s += '(%s)' % self.target

        return s

    def ptr_num(self):
        # address stripped of base address
        return self.address & 0xF

    def is_ptr_type(self, strtype):
        """
        Checks that the pointer type matches the one given.
        :param strtype:
        :return:
        """
        if self.pointer_type != strtype:
            raise ValueError('Error: mismatched pointer types')

    @classmethod
    def init_addresses(cls):
        """
        Initialize addresses for all pointers to the base values.
        :return:
        """

        cls.Mapping_Ptr = dict(zip(cls.Pointer_types,
                           [0x340000, 0x350000, 0x360000, 0x370000, 0x380000]))

    @classmethod
    def from_repr(cls, ptrstring):
        """
        Re-creates a pointer from the __repr__ string.
        :param ptrstring:
        :return:
        """
        selem = ptrstring.split(' ')
        pointertype = selem[0]
        name = selem[2]
        address = selem[1]
        try:
            value = int(selem[4])
        except:
            value = None
        try:
            target = selem[5][1:-1]  # removes parentheses
        except:
            target = ''

        seqptr = cls(pointertype, name, value, target)
        seqptr.address = address

        return seqptr


class Instruction(object):

    OP_CallFunction          = 0x1
    OP_CallPointerFunction   = 0x2
    OP_CallFuncPointerRepeat = 0x3
    OP_CallPointerFuncPointerRepeat = 0x4
    OP_JumpToSubroutine      = 0x5
    OP_JumpPointerSubroutine = 0x6
    OP_JumpSubPointerRepeat  = 0x7
    OP_JumpPointerSubPointerRepeat = 0x8
    OP_ReturnFromSubroutine  = 0xE
    OP_EndOfProgram          = 0xF

    OP_names = ["CALL", 'CALLP', 'CALLREP', 'CALLPREP',
                "JSR", 'JSP', 'JSREP', 'JSPREP',
                "RTS", "END"]

    OP_codes = bidi.BidiMap(OP_names,
                            [OP_CallFunction,
                             OP_CallPointerFunction,
                             OP_CallFuncPointerRepeat,
                             OP_CallPointerFuncPointerRepeat,
                             OP_JumpToSubroutine,
                             OP_JumpPointerSubroutine,
                             OP_JumpSubPointerRepeat,
                             OP_JumpPointerSubPointerRepeat,
                             OP_ReturnFromSubroutine,
                             OP_EndOfProgram])
    Call_codes = [OP_CallFunction, OP_CallPointerFunction, OP_CallFuncPointerRepeat, OP_CallPointerFuncPointerRepeat]
    Jsr_codes = [OP_JumpToSubroutine, OP_JumpPointerSubroutine, OP_JumpSubPointerRepeat, OP_JumpPointerSubPointerRepeat]

    SubAddressShift = 16

    pattern_CALL = re.compile(
        "CALL\s+func\((\d+)\)\s+repeat\(((\d+)|infinity)\)")
    pattern_JSR_addr = re.compile(
        "JSR\s+((0[xX])?[\dA-Fa-f]+)\s+repeat\((\d+)\)")
    pattern_JSR_name = re.compile(
        "JSR\s+([\dA-Za-z0-9\_]+)\s+repeat\((\d+)\)")

    def __init__(self,
                 opcode,
                 function_id=None,
                 infinite_loop=False,
                 repeat=1,
                 address=None,
                 subroutine=None):
        """
        The input opcode is the name of the operation or the code value.
        The name goes to self.name, self.opcode is the actual code.
        :param opcode: string or int
        :param function_id: int
        :param infinite_loop: bool or int
        :param repeat: int
        :param address: int
        :param subroutine: string
        :return:
        """
        self.function_id = 0
        self.address = None
        self.subroutine = None
        self.unassembled = False
        self.repeat = 0
        self.infinite_loop = False
        self.opcode = None
        self.name = None

        if opcode in self.OP_names:
            # by name
            self.name = opcode
            self.opcode = self.OP_codes[opcode]
        elif self.OP_codes.has_key(opcode):
            # by opcode value
            self.opcode = opcode
            self.name = self.OP_codes[opcode]
        else:
            raise ValueError("Invalid FPGA OPcode " + opcode.__repr__())

        if self.opcode in self.Call_codes:
            if function_id not in range(16):
                raise ValueError("Invalid Function ID")
            if infinite_loop not in [0, 1, True, False]:
                raise ValueError("Invalid Infinite Loop flag")

            self.function_id = int(function_id) & 0xf
            if infinite_loop:
                self.infinite_loop = True
                self.repeat = 0
            else:
                self.infinite_loop = False
                self.repeat = int(repeat) & 0x3fffff

        elif self.opcode in self.Jsr_codes:
            if address is not None:
                self.address = int(address) & 0x3ff
            elif subroutine is not None:
                self.subroutine = subroutine
            else:
                raise ValueError("Invalid JSR instruction: " +
                                 "no address or subroutine to jump")

            self.repeat = int(repeat) & 0xffff

    def __repr__(self):
        s = ""
        s += "%-8s" % self.name

        if self.opcode in self.Call_codes:
            s += "  %-10s" % ("func(%d)" % self.function_id)
            if self.infinite_loop:
                s += "repeat(infinity)"
            else:
                s += "repeat(%d)" % self.repeat
        elif self.opcode in self.Jsr_codes:
            if self.address is not None:
                s += "  %-8s" % ("0x%03x" % self.address)
            s += "repeat(%d)" % self.repeat
            if self.subroutine is not None:
                s += " -> " + self.subroutine

        return s

    def bytecode(self):
        """
        Return the 32 bits byte code for the FPGA instruction
        """

        bc = 0x00000000
        # Opcode
        bc |= (self.opcode & 0xf) << 28

        if self.opcode in self.Call_codes:
            bc |= (self.function_id & 0xf) << 24

            if self.infinite_loop:
                bc |= 1 << 23
            else:
                bc |= (self.repeat & 0x3fffff)

        elif self.opcode in self.Jsr_codes:
            if self.address == None:
                raise ValueError("Unassembled JSR instruction. No bytecode")

            bc |= (self.address & 0x3ff) << self.SubAddressShift
            bc |= (self.repeat & ((1 << self.SubAddressShift) - 1))

        elif self.opcode in [self.OP_ReturnFromSubroutine,
                             self.OP_EndOfProgram]:
            # OK
            pass

        else:
            raise ValueError("Invalid instruction")

        return bc

    @classmethod
    def fromstring(cls, s):
        """
        Create an instruction from a string (without label).
        Return None for an empty string.
        Raise an exception if the syntax is wrong.
        """
        # TODO: still missing the new instructions
        # looking for a comment part and remove it

        pos = s.find('#')
        if pos != -1:
            s = s[:pos]

        s = s.strip()
        if len(s) == 0:
            return None

        # CALL
        m = cls.pattern_CALL.match(s)
        if m is not None:
            function_id = int(m.group(1))
            if m.group(2) == "infinity":
                return Instruction(opcode="CALL",
                                   function_id=function_id,
                                   infinite_loop=True)
            else:
                repeat = int(m.group(2))
                return Instruction(opcode="CALL",
                                   function_id=function_id,
                                   repeat=repeat)

        # JSR addr
        m = cls.pattern_JSR_addr.match(s)
        if m is not None:
            print m.groups()
            address = int(m.group(1), base=16)
            repeat = int(m.group(3))
            return Instruction(opcode="JSR",
                               address=address,
                               repeat=repeat)

        # JSR name
        m = cls.pattern_JSR_name.match(s)
        print m, s
        if m is not None:
            subroutine = m.group(1)
            repeat = int(m.group(2))
            return Instruction(opcode="JSR",
                               subroutine=subroutine,
                               repeat=repeat)

        # RTS
        if s == "RTS":
            return Instruction(opcode=s)

        # END
        if s == "END":
            return Instruction(opcode=s)

        raise ValueError("Unknown instruction %s" % s)

    @classmethod
    def frombytecode(cls, bc):
        # Opcode
        opcode = (bc >> 28)
        if opcode not in [cls.OP_CallFunction,
                          cls.OP_CallPointerFunction,
                          cls.OP_CallFuncPointerRepeat,
                          cls.OP_CallPointerFuncPointerRepeat,
                          cls.OP_JumpToSubroutine,
                          cls.OP_JumpPointerSubroutine,
                          cls.OP_JumpSubPointerRepeat,
                          cls.OP_JumpPointerSubPointerRepeat,
                          cls.OP_ReturnFromSubroutine,
                          cls.OP_EndOfProgram]:
            raise ValueError("Invalid FPGA bytecode (invalid opcode)")

        if opcode in cls.Call_codes:
            function_id = (bc >> 24) & 0xf
            infinite_loop = (bc & (1 << 23)) != 0
            # print infinite_loop
            repeat = (bc & 0x3fffff)
            # print repeat

            if infinite_loop:
                # print "infinity"
                return Instruction(opcode=opcode,
                                   function_id=function_id,
                                   infinite_loop=infinite_loop,
                                   repeat=0)
            else:
                # print "repeat", repeat
                return Instruction(opcode=opcode,
                                   function_id=function_id,
                                   repeat=repeat)

        elif opcode == cls.Jsr_codes:
            address = (bc >> cls.SubAddressShift) & 0x3ff
            # print address
            repeat = bc & ((1 << cls.SubAddressShift) - 1)
            # print repeat

            return Instruction(opcode=opcode,
                               address=address,
                               repeat=repeat)

        return Instruction(opcode=opcode)


class Subroutine(object):
    def __init__(self):
        self.name = None
        self.instructions = []  # subroutine instruction list


class Program_UnAssembled(object):
    def __init__(self):
        self.subroutines = {}  # key = name, value = subroutine object
        self.subroutines_names = []  # to keep the order
        self.instructions = []  # main program instruction list
        self.seq_pointers = {}  # pointers (if applicable)

    # I/O XML -> separate python file
    # I/O text -> separate python file

    def compile(self):
        """
        Compile the program and return the compiled version.
        """
        # subroutines alignment on 0x??0
        alig = 0x008

        result = Program()
        subroutines_addr = {}

        current_addr = 0x000

        # first, the main program
        for instr in self.instructions:
            result.instructions[current_addr] = instr
            current_addr += 1

        # then, each subroutine
        # for subr_name, subr in self.subroutines.iteritems():
        for subr_name in self.subroutines_names:
            subr = self.subroutines[subr_name]
            # alignment
            if current_addr > 0:
                current_addr = (current_addr / alig + 1) * alig
            subroutines_addr[subr_name] = current_addr
            result.subroutines[subr_name] = current_addr
            for instr in subr.instructions:
                result.instructions[current_addr] = instr
                current_addr += 1

        # now setting addresses into JSR/JSREP instructions referring subroutine names
        addrs = result.instructions.keys()
        addrs.sort()
        for addr in addrs:
            instr = result.instructions[addr]
            # print addr, instr
            if instr.name in ['JSR', 'JSREP']:
                if not (subroutines_addr.has_key(instr.subroutine)):
                    raise ValueError("Undefined subroutine %s" %
                                     instr.subroutine)
                # instr.subroutine = None
                instr.address = subroutines_addr[instr.subroutine]
                # print addr, instr

        # also setting pointers referencing subroutines if there are any
        for ptrname in self.seq_pointers:
            seq_pointer = self.seq_pointers[ptrname]
            if seq_pointer.pointer_type in ['MAIN', 'PTR_SUBR']:
                if not (subroutines_addr.has_key(seq_pointer.target)):
                    raise ValueError("Pointer to undefined subroutine %s" %
                                     seq_pointer.target)
                seq_pointer.value = subroutines_addr[seq_pointer.target]

        return result

    @classmethod
    def fromstring(cls, s):
        """
        Create a new UnAssembledProgram from a string of instructions.
        """
        lines = s.split("\n")
        nlines = len(lines)
        current_subroutine = None

        prg = Program_UnAssembled()

        print lines

        for iline in xrange(nlines):
            print iline + 1
            line = lines[iline]
            print line
            elts = line.split()

            if len(elts) < 1:
                # empty line
                continue

            # label
            if elts[0][-1] == ':':
                # first elt is a label -> start of a subroutine
                subroutine_name = elts[0][:-1]
                prg.subroutines[subroutine_name] = Subroutine()
                prg.subroutines_names.append(subroutine_name)
                current_subroutine = prg.subroutines[subroutine_name]
                elts = elts[1:]

            if len(elts) < 1:
                # empty label
                continue

            s = " ".join(elts)

            instr = Instruction.fromstring(s)
            print "INSTR = ", instr
            if instr is None:
                continue

            if current_subroutine is not None:
                current_subroutine.instructions.append(instr)
            else:
                prg.instructions.append(instr)

            if instr.opcode == Instruction.OP_ReturnFromSubroutine:
                current_subroutine = None

        return prg


        # @classmethod
        # def fromxmlstring(cls, s):
        # """
        #     Create a new UnAssembledProgram from a XML string.
        #     """
        #     pass


Prg_NA = Program_UnAssembled

# # -----------------------------------------------------------------------


class Sequencer(object):
    # 32 outputs are available

    default_channels_desc = {
        0: {'channel': 0,
            'name': 'RU',
            'fullname': 'ASPIC ramp-up integration',
            'FPGA': 'ASPIC_r_up'},
        1: {'channel': 1,
            'name': 'RD',
            'fullname': 'ASPIC ramp-down integration',
            'FPGA': 'ASPIC_r_down'},
        2: {'channel': 2,
            'name': 'RST',
            'fullname': 'ASPIC integrator reset',
            'FPGA': 'ASPIC_reset'},
        3: {'channel': 3,
            'name': 'CL',
            'fullname': 'ASPIC clamp',
            'FPGA': 'ASPIC_clamp'},
        4: {'channel': 4,
            'name': 'R1',
            'fullname': 'Serial clock 1',
            'FPGA': 'CCD_ser_clk(0)'},
        5: {'channel': 5,
            'name': 'R2',
            'fullname': 'Serial clock 2',
            'FPGA': 'CCD_ser_clk(1)'},
        6: {'channel': 6,
            'name': 'R3',
            'fullname': 'Serial clock 3',
            'FPGA': 'CCD_ser_clk(2)'},
        7: {'channel': 7,
            'name': 'RG',
            'fullname': 'Serial reset clock',
            'FPGA': 'CCD_reset_gate'},
        8: {'channel': 8,
            'name': 'P1',
            'fullname': 'Parallel clock 1',
            'FPGA': 'CCD_par_clk(0)'},
        9: {'channel': 9,
            'name': 'P2',
            'fullname': 'Parallel clock 2',
            'FPGA': 'CCD_par_clk(1)'},
        10: {'channel': 10,
             'name': 'P3',
             'fullname': 'Parallel clock 3',
             'FPGA': 'CCD_par_clk(2)'},
        11: {'channel': 11,
             'name': 'P4',
             'fullname': 'Parallel clock 4',
             'FPGA': 'CCD_par_clk(3)'},
        12: {'channel': 12,
             'name': 'SPL',
             'fullname': 'ADC sampling signal',
             'FPGA': 'ADC_trigger'},
        13: {'channel': 13,
             'name': 'SOI',
             'fullname': 'Start of Image',
             'FPGA': 'SOI'},
        14: {'channel': 14,
             'name': 'EOI',
             'fullname': 'End of Image',
             'FPGA': 'EOI'},
        #
        16: {'channel': 16,
             'name': 'SHU',
             'fullname': 'Shutter TTL',
             'FPGA': 'shutter'}
    }

    default_channels = bidi.BidiMap([v['channel']
                                     for v in default_channels_desc.values()],
                                    [v['name']
                                     for v in default_channels_desc.values()])

    def __init__(self,
                 channels=default_channels,
                 channels_desc=default_channels_desc,
                 functions={},
                 functions_desc={},
                 program=Program(),
                 parameters={},
                 pointers={}):
        #
        self.channels = channels
        self.channels_desc = channels_desc
        self.functions = functions  # max 16 functions (#0 is special)
        self.functions_desc = functions_desc
        self.program = program  # empty program
        self.parameters = parameters  # memory of the parameter values set in XML/txt
        self.pointers = pointers  # memory of pointers set in txt

    def get_function(self, funcref):
        # looks up mapping
        if isinstance(funcref, str):
            func_id = self.functions_desc[funcref]['idfunc']
        elif funcref in range(16):
            func_id = funcref
        else:
            return None

        if not (self.functions.has_key(func_id)):
            return None

        return self.functions[func_id]

    def pointer_value(self, typeptr, numptr):
        """
        Returns the pointer content for a given pointer type and number.
        :param typeptr:
        :param numptr:
        :return:
        """
        for pname in self.pointers:
            p = self.pointers[pname]
            if p.pointer_type == typeptr and p.ptr_num() == numptr:
                return p.value

        return None

    def pointer_name(self, typeptr, numptr):
        """
        Returns the name of the pointer for a given pointer type and number.
        :param numptr:
        :return:
        """
        for pname in self.pointers:
            p = self.pointers[pname]
            if p.pointer_type == typeptr and p.ptr_num() == numptr:
                return pname

        return ''

    def repr_pointer(self, typeptr, numptr):
        """
        Representation of a pointer as name and target.
        :param typeptr:
        :param numptr:
        :return:
        """
        # need to look up name
        for pname in self.pointers:
            p = self.pointers[pname]
            if p.pointer_type == typeptr and p.ptr_num() == numptr:
                if typeptr in SequencerPointer.Repeat_pointers:
                    return "%d: %s -> %d" % (numptr, pname, p.value)
                else:
                    return "%d: %s -> %s" % (numptr, pname, p.target)

    def repr_instruction(self, address):
        """
        Improved representation of an instruction, with names for functions, pointers, and subroutines.
        :param address:
        :return:
        """
        instr = self.program.instructions[address]

        s = "0x%03x: " % address
        s += "%-8s" % instr.name

        if instr.opcode in instr.Call_codes:
            # function called
            if instr.name in ["CALL", 'CALLREP']:
                s += "  func(%d = %s)" % (instr.function_id, self.functions[instr.function_id].name)
            else:
                s += "  func(%s)" % self.repr_pointer('PTR_FUNC', instr.function_id)

            # repetition called
            if instr.infinite_loop:
                s += "  repeat(infinity)"
            elif instr.name in ["CALL", 'CALLP']:
                s += "  repeat(%d)" % instr.repeat
            else:
                s += "  repeat(%s)" % self.repr_pointer('REP_FUNC', instr.repeat)

        elif instr.opcode in instr.Jsr_codes:
            if instr.name in ["JSR", "JSREP"]:
                s += "  0x%03x" % instr.address
                if instr.subroutine is not None:
                    s += " -> " + instr.subroutine
            else:
                s += self.repr_pointer('PTR_SUBR', instr.address)

            if instr.name in ["JSR", 'JSP']:
                s += "  repeat(%d)" % instr.repeat
            else:
                s += "  repeat(%s)" % self.repr_pointer('REP_SUBR', instr.repeat)

        return s

    def recurse_exec(self, start_address, recurse_level=0, verbose=True):
        """
        Auxiliary for recursivity in sequence().
        :param start_adress:
        :return:
        """
        current_address = start_address
        listexec = []
        strlevel = '__' * recurse_level

        while current_address in self.program.instructions:
            # fill table with all instructions
            instr = self.program.instructions[current_address]
            s = '%s%s' % (strlevel, self.repr_instruction(current_address))
            listexec.append(s)
            if verbose:
                print(s)

            if instr.opcode in [instr.OP_ReturnFromSubroutine, instr.OP_EndOfProgram]:
                # we are done with this level
                break
            # if it calls another subroutine : looks its address and recurse
            elif instr.opcode in instr.Jsr_codes:
                if instr.opcode in [instr.OP_JumpToSubroutine, instr.OP_JumpSubPointerRepeat]:
                    target_address = instr.address
                else:
                    target_address = self.pointer_value('PTR_SUBR', instr.address)
                listexec.extend(self.recurse_exec(target_address, recurse_level=recurse_level+1, verbose=verbose))

            # else : function execution : we go to the next instruction
            current_address += 1

        return listexec

    def sequence(self, subr, verbose=True):
        """
        Unrolls a given subroutine, with a line per instruction.
        :param subr:
        :return:
        """
        if subr not in self.program.subroutines:
            print('Unknown subroutine name: %s' % subr)
            return ''

        start_address = self.program.subroutines[subr]

        # will need this, converts to us
        p = self.parameters['clockperiod'] * 1e6

        # sequence only
        #listexec = self.recurse_exec(start_address, verbose=verbose)
        # with timing
        listexec, total_time = self.recurse_full(start_address, p, verbose=verbose)

        return listexec

    def recurse_time(self, start_address, clockperiod, recurse_level=0, verbose=True):
        """
        Auxiliary for recursivity in timing().
        :param start_adress:
        :return:
        """
        current_address = start_address
        total_time = 0
        strlevel = '__' * recurse_level

        while current_address in self.program.instructions:
            instr = self.program.instructions[current_address]
            if instr.opcode in instr.Call_codes:
                # parse repetitions, look up function
                if instr.opcode in [instr.OP_CallFunction, instr.OP_CallPointerFunction]:
                    repetitions = instr.repeat
                else:
                    repetitions = self.pointer_value('REP_FUNC', instr.repeat)
                if instr.opcode in [instr.OP_CallFunction, instr.OP_CallFuncPointerRepeat]:
                    funcnum = instr.function_id
                else:
                    funcnum = self.pointer_value('PTR_FUNC', instr.function_id)
                instr_time = self.functions[funcnum].total_time() * repetitions * clockperiod
                total_time += instr_time

            elif instr.opcode in instr.Jsr_codes:
                # parse repetitions, look up new address, iterate
                if instr.opcode in [instr.OP_JumpToSubroutine, instr.OP_JumpPointerSubroutine]:
                    repetitions = instr.repeat
                else:
                    repetitions = self.pointer_value('REP_SUBR', instr.repeat)
                if instr.opcode in [instr.OP_JumpToSubroutine, instr.OP_JumpSubPointerRepeat]:
                    target_address = instr.address
                else:
                    target_address = self.pointer_value('PTR_SUBR', instr.address)
                instr_time = self.recurse_time(target_address, clockperiod, recurse_level=recurse_level+1,
                                               verbose=verbose) * repetitions
                total_time += instr_time

            else:
                if verbose:
                    print('%s%s  run total: %.2f us' % (strlevel, instr.__repr__(), total_time))
                break

            # print here to get total after breakout for calls to subroutines
            if verbose:
                print('%s%s  run time: %.2f us  run total: %.2f us' %
                      (strlevel, instr.__repr__(), instr_time, total_time))
            current_address += 1

        return total_time

    def timing(self, subr, verbose=True):
        """
        Computes timing for a given subroutine, with breakout by instruction.
        Result in microseconds.
        :param subr:
        :return:
        """
        # will need this, converts to us
        p = self.parameters['clockperiod'] * 1e6

        if subr not in self.program.subroutines:
            print('Unknown subroutine name: %s' % subr)
            return None

        start_address = self.program.subroutines[subr]

        return self.recurse_time(start_address, p, verbose=verbose)

    def recurse_full(self, start_address, clockperiod, recurse_level=0, verbose=True):
        """
        Auxiliary for recursivity on sequence breakout and timing.
        :param start_adress:
        :return:
        """
        current_address = start_address
        listexec = []
        total_time = 0
        strlevel = '__' * recurse_level

        while current_address in self.program.instructions:
            instr = self.program.instructions[current_address]
            s = '%s%s' % (strlevel, self.repr_instruction(current_address))

            if instr.opcode in [instr.OP_ReturnFromSubroutine, instr.OP_EndOfProgram]:
                # we are done with this level
                s += (' = subtotal: %.2f us' %  total_time)
                listexec.append(s)
                if verbose:
                    print(s)
                break

            if instr.opcode in instr.Call_codes:
                # parse repetitions, look up function
                if instr.opcode in [instr.OP_CallFunction, instr.OP_CallPointerFunction]:
                    repetitions = instr.repeat
                else:
                    repetitions = self.pointer_value('REP_FUNC', instr.repeat)
                if instr.opcode in [instr.OP_CallFunction, instr.OP_CallFuncPointerRepeat]:
                    funcnum = instr.function_id
                else:
                    funcnum = self.pointer_value('PTR_FUNC', instr.function_id)
                instr_time = self.functions[funcnum].total_time() * repetitions * clockperiod
                s += ' = run time: %.2f us  ' % instr_time
                # append to table collecting all instructions
                listexec.append(s)
                if verbose:
                    print(s)

            elif instr.opcode in instr.Jsr_codes:
                # parse repetitions, look up new address, recurse
                if instr.opcode in [instr.OP_JumpToSubroutine, instr.OP_JumpPointerSubroutine]:
                    repetitions = instr.repeat
                else:
                    repetitions = self.pointer_value('REP_SUBR', instr.repeat)
                if instr.opcode in [instr.OP_JumpToSubroutine, instr.OP_JumpSubPointerRepeat]:
                    target_address = instr.address
                else:
                    target_address = self.pointer_value('PTR_SUBR', instr.address)
                subexec, subtime = self.recurse_full(target_address, clockperiod, recurse_level=recurse_level+1,
                                               verbose=verbose)
                instr_time =  subtime * repetitions
                s += ' = run time: %.2f us  ' % instr_time
                # heads list with subroutine call
                listexec.append(s)
                if verbose:
                    print(s)
                # appends called subroutine to execution list
                listexec.extend(subexec)

            else:
                raise ValueError('Unknown opcode %s' % instr.opcode)

            total_time += instr_time

            current_address += 1

        return listexec, total_time

    def find_function_withclock(self, subr, clockname):
        """
        Finds the function that does the actual readout in a given subroutine/main.
        :param subr:
        :return:
        """

        if subr not in self.program.subroutines:
            print('Unknown subroutine name: %s' % subr)
            return ''

        current_address = self.program.subroutines[subr]
        saved_address = []

        while current_address in self.program.instructions:
            instr = self.program.instructions[current_address]
            if instr.opcode in instr.Call_codes:
                # function
                if instr.opcode in [instr.OP_CallFunction, instr.OP_CallFuncPointerRepeat]:
                    funcnum = instr.function_id
                else:
                    funcnum = self.pointer_value('PTR_FUNC', instr.function_id)
                funcname = self.functions[funcnum].name
                if clockname in self.functions_desc[funcname]['clocks']:
                    return funcname
                # moves on to next instruction
                current_address += 1

            elif instr.opcode in instr.Jsr_codes:
                # stacks memory of where the next instruction would be
                saved_address.append(current_address + 1)
                # looks up call to subroutine and goes there
                if instr.opcode in [instr.OP_JumpToSubroutine, instr.OP_JumpSubPointerRepeat]:
                    current_address = instr.address
                else:
                    current_address = self.pointer_value('PTR_SUBR', instr.address)
            else:
                # returns from end of subroutine
                current_address = saved_address.pop()

        return ''


## -----------------------------------------------------------------------

class Function(object):
    def __init__(self,
                 name="", fullname="",
                 timelengths={}, outputs={}, channels=Sequencer.default_channels):
        # timelengths = id: duration (10ns unit), etc...
        # self.timelengths = {0: 12, 1: 14}
        # self.outputs = {0: '0b01001101...', 1: '0b1111000...', ... }
        self.name = name
        self.fullname = fullname
        self.timelengths = dict(timelengths)  # 16 max, (last one zero duration)
        self.outputs = dict(outputs)  # bit setup
        self.channels = channels  # mapping bit/symbolic name

        # TODO: add flexibility on the clock line bit map

    def __repr__(self):
        s = "Function: " + self.name + "\n"
        s += "    " + self.fullname + "\n"

        # s += ("                                \t " + 
        #       "               S ESSPPPPRRRRCRRR\n")
        # s += ("slice\t duration (x10ns)\t\t " + 
        #       "               H OOP4321G321LSDU\n")
        # s += ("                        \t\t " + 
        #       "               U IIL|||||||||T||\n")

        l0 = "                                \t "
        l1 = "slice\t duration (x10ns)\t\t "
        l2 = "                        \t\t "

        for i in xrange(32):
            c = 32 - 1 - i
            if self.channels.has_key(c):
                name = self.channels[c]
                named = dict(zip(xrange(len(name)), list(name)))
                l0 += named.get(0, '|')
                l1 += named.get(1, '|')
                l2 += named.get(2, '|')
            else:
                l0 += ' '
                l1 += ' '
                l2 += ' '

        s += l0 + '\n' + l1 + '\n' + l2 + '\n'

        s += (73 * "-") + "\n"
        for sl in xrange(16):
            bit_str = "%032d" % int(bin(self.outputs.get(sl, 0x0))[2:])
            s += "%02d\t %8d\t\t\t %s\n" % (sl,
                                            self.timelengths.get(sl, 0),
                                            bit_str)
        return s

    def is_on(self, channel, timeslice):
        """
        Return the state (0/1) of channel #channel during
        the time slice #timeslice. Return None if undefined.
        """
        if isinstance(channel, str):
            c = self.channels[channel]
        else:
            c = channel

        if self.timelengths.has_key(timeslice):
            state = int(self.outputs[timeslice] & (1 << c) != 0)
            return state

        return None

    def set_output_channel(self, value, channel, timeslice=None):
        """
        Sets either a given timeslice or all (if None given) of a given channel to a value.
        :param value:
        :param channel: channel by name
        :param timeslice:
        :return:
        """
        # looks up mapping
        if isinstance(channel, str):
            c = self.channels[channel]
        else:
            c = channel

        if timeslice is None:
            if value:
                for t in self.outputs:
                    self.outputs[t] = setBit(self.outputs[t], c)
            else:
                for t in self.outputs:
                    self.outputs[t] = clearBit(self.outputs[t], c)
        else:
            if value:
                self.outputs[timeslice] = setBit(self.outputs[timeslice], c)
            else:
                self.outputs[timeslice] = clearBit(self.outputs[timeslice], c)

    def split_timeslice(self, ts, firstduration):
        """
        Splits a timeslice into two identical consecutive timeslices of the same total time.
        With the first taking the given duration, the second the rest.
        :param ts:
        :param firstduration:
        :return:
        """
        if firstduration <= 0 or firstduration > self.timelengths[ts]:
            raise ValueError('Error splitting function timeslice: inappropriate duration %d' % firstduration)

        # shifts timeslices above
        for t in range(16, ts, -1):
            if t in self.timelengths:
                self.timelengths[t+1] = self.timelengths[t]
                self.outputs[t+1] = self.outputs[t]

        # duplicates to split
        self.outputs[ts+1] = self.outputs[ts]

        # split times
        self.timelengths[ts+1] = self.timelengths[ts] - firstduration
        self.timelengths[ts] = firstduration

        # special timeslices
        if ts==0:
            # need to shift subtraction of 1 from second to first TS
            self.timelengths[ts+1] += 1
            self.timelengths[ts] -= 1
            if self.timelengths[ts] == 0:
                raise ValueError('Error trying to program 0 duration to first timeslice')

        if ts+2 not in self.timelengths:
            if self.timelengths[ts+1] <= 0:
                raise ValueError('Error trying to program 0 duration to last timeslice')

    def cumulated_time(self):
        """
        Returns the total time spent in the function after each timeslice.
        :rtype: list
        """
        running_total = 0
        cumulated = []

        for t in range(16):
            if t in self.timelengths:
                running_total += self.timelengths[t]

                # special timeslices
                if t == 0:
                    running_total += 1
                if t+1 not in self.timelengths:
                    running_total += 2

                cumulated.append(running_total)

        return cumulated

    def set_output_at_time(self, value, channel, clktime, wrap=False):
        """
        Sets a given output to a given value at a given time. Splits the timeslice if needed.
        Currently tolerates 10 ns timeslices, to be checked.
        :param value:
        :param channel:
        :param timeslice:
        :return:
        """
        # add time before first timeslice to have all posts
        cumulated = [0] + self.cumulated_time()

        if clktime >= cumulated[-1]:
            # not possible: gets kicked out or wrap around (for trigger)
            if wrap:
                clktime = divmod(clktime, cumulated[-1])[1]
            else:
                raise ValueError('Clock time %d to set %s is after end of function' % (clktime, channel))

        for ts, t in enumerate(cumulated):
            if clktime == t:
                self.set_output_channel(value, channel, timeslice=ts)
                break
            elif clktime < t :
                # need to split the right timeslice at the right time
                # ts cannot be 0 because cumulated[0] = 0
                self.split_timeslice(ts-1, clktime-cumulated[ts-1])
                # puts value in the newly-splitted timeslice
                self.set_output_channel(value, channel, timeslice=ts)
                break

    def total_time(self):
        """
        Returns total duration of functions (expressed as clock cycles).
        Takes into account additionnal cycles at beginning and end.
        :return:
        """
        return sum(self.timelengths.itervalues())+3

    def scope(self, channel):
        """
        Returns a list with on/off values for the given channel, with one item per FPGA cycle.
        :return:
        """
        ntime = self.total_time()
        timescope = [0] * ntime
        i = 0

        for tslice in sorted(self.timelengths.keys()):
            duration = self.timelengths[tslice]
            # special cases at beginning and end of function
            if tslice == 0:
                duration += 1
            if tslice+1 not in self.timelengths:
                duration += 2

            if self.is_on(channel, tslice):
                for d in range(duration):
                    timescope[i+d] = 1
            i += duration

        return timescope

