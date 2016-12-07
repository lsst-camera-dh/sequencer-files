#! /usr/bin/env python
#
# LSST
# Python minimal interface for the REB FPGA
# TXT assembler-style IO
#

from sequencer import *
import grammar

class TxtParser(object):

    time_units = {'ns': 1e-9, 'us': 1e-6, 'ms': 1e-3, 's': 1}

    def __init__(self, verbose=True):

        self.channels_desc = {}
        self.channels = {}
        self.parameters_desc = {}
        self.parameters = {}
        self.functions = {}
        self.functions_desc = {}
        self.subroutines = {}
        self.subroutines_names = []
        self.mains = {}
        self.mains_names = []
        self.unnamed_subroutine_num = 0
        self.pointers = {}
        self.pointers_desc = {}
        self.verbose = verbose

    def process_number(self, s):
        ss = s.strip()
        if s == 'infinity':
            return 'Inf'
        try:
            value = int(ss)
        except ValueError:
            value = float(ss)

        return value

    def process_value(self, s):
        # now converts to FPGA clock cycles
        if self.parameters.has_key(s):
            # now assuming this is a time parameter and therefore a tuple
            value, unit = self.parameters[s]
            # print "K lvalue = ", lvalue
        else:
            # expecting an already parsed tuple
            value, unit = s

        try:
            ckperiod = self.parameters['clockperiod'][0] * self.time_units[self.parameters['clockperiod'][1]]
        except:
            ckperiod = 10e-9

        if unit in self.time_units:
            duration = int(value * self.time_units[unit] / ckperiod)
        else:
            raise ValueError('Unable to parse unit %s' % unit)

        return duration

    def parse_parameters(self, parameters_node):
        # list of tuples
        for param in parameters_node:
            fullname = param[2]
            name = param[0]
            value = param[1]

            param_dict = {'value': value}  # will be a tuple if time parameter

            if fullname != None:
                param_dict['fullname'] = fullname

            self.parameters_desc[name] = dict(param_dict)

        self.parameters = \
            dict([(k, self.parameters_desc[k]['value'])
                  for k in self.parameters_desc.keys()])

    def parse_channels(self, channels_node):

        for c in channels_node:
            fullname = c[2]
            name = c[0]
            value = c[1]

            c_dict = {'channel': value,
                      'name': name}

            if fullname != None:
                c_dict['fullname'] = fullname[0]

            self.channels_desc[name] = dict(c_dict)

        self.channels = bidi.BidiMap([v['channel']
                                      for v in self.channels_desc.values()],
                                     [v['name']
                                      for v in self.channels_desc.values()])

    def parse_pointers(self, pointers_node):
        #re-initialize address list
        SequencerPointer.init_addresses()
 
        # tuple of lists of tuples
        for pointer_list in pointers_node:
            for param in pointer_list:
                pointertype = param[0]
                name = param[1]
                content = param[2]

                param_dict = {'value': content, 'type': pointertype}

                try:
                    fullname = param[3]
                    param_dict['fullname'] = fullname
                except:
                    param_dict['fullname'] = ''

                self.pointers_desc[name] = dict(param_dict)

                if pointertype in SequencerPointer.Exec_pointers:
                    # will compile later
                    self.pointers[name] = SequencerPointer(pointertype, name, target=content)
                elif pointertype in SequencerPointer.Repeat_pointers:
                    self.pointers[name] = SequencerPointer(pointertype, name, value=content)

    def parse_functions(self, functions_node):
        # list of dictionaries
        idfunc = 1
        for func in functions_node:
            fullname = func['comment']
            name = func['name']

            func_dict = {}

            if name == 'Default':  # reserved name
                func_dict['idfunc'] = 0
            else:
                func_dict['idfunc'] = idfunc
                idfunc += 1

            if fullname != None:
                func_dict['fullname'] = fullname

            self.functions_desc[name] = dict(func_dict)

            if self.verbose:
                print name, fullname

            function = Function(name=name,
                                fullname=fullname,
                                channels=self.channels)

            # analyzing constants
            constants = {}
            if func['constants'] is not None:
                for const in func['constants']:
                    # list of tuples
                    channel = const[0]
                    value = const[1]
                    constants[channel] = value
                # print constants

            # analyzing slices
            channel_position = {}
            cpos = 0
            for clock in func['clocks']:
                # print clock
                channel_position[clock] = cpos
                cpos += 1

            if self.verbose:
                print channel_position
            self.functions_desc[name]['clocks'] = func['clocks']  # list of active channels

            # self.timelengths = {0: 12, 1: 14}
            # self.outputs = {0: '0b01001101...', 1: '0b1111000...', ... }
            timelengths = {}
            outputs = {}

            islice = 0
            for timeslice in func['slices']:
                duration = self.process_value(timeslice[0])

                if islice == 0:
                    timelengths[islice] = duration - 1  # FPGA adds one to duration of first slice
                elif islice == len(func['slices']) - 1:
                    timelengths[islice] = duration - 2  # FPGA adds 2 to duration of last slice
                else:
                    timelengths[islice] = duration

                output = 0x0000000000000000

                values = timeslice[1]

                for ck, cdesc in self.channels_desc.iteritems():
                    cname = cdesc['name']
                    crank = cdesc['channel']

                    if constants.has_key(cname):
                        # that's a constant one
                        output |= (constants[cname] << crank)
                    elif channel_position.has_key(cname):
                        cpos = channel_position[cname]
                        cval = values[cpos]
                        output |= (cval << crank)
                if self.verbose:
                    print bin(output)

                outputs[islice] = output

                islice += 1
                if islice > 15:
                    print('Warning: too many slices in function %s' % name)
                    break

            function.timelengths = dict(timelengths)
            function.outputs = dict(outputs)

            self.functions_desc[name]['function'] = function
            self.functions[name] = function

    def parse_repeat(self, reptuple):
        """
        Parse repeat part of the call dictionaries
        :param reptuple:
        :return: value, is it a pointer, is it infinity
        """

        if reptuple == 1:
            # check that this is actually false for a tuple
            return 1, False, False
        elif reptuple[0] == 'INTEGER':
            return reptuple[1], False, False
        elif reptuple[0] == 'CONSTANT_NAME':
            return self.parameters[reptuple[1]], False, False
        elif reptuple[0] in ['REP_SUBR', 'REP_FUNC']:
            # checks that the type of pointer we are looking for matches the type of the pointer we find
            self.pointers[reptuple[1]].is_ptr_type(reptuple[0])
            return self.pointers[reptuple[1]].ptr_num(), True, False
        elif reptuple[0] == 'INFINITY':
            return 1, False, True

    def parse_call(self, call_node):
        """
        Parse a single line of program instruction, returns instruction
        """
        # list of dictionaries
        # print "        call"
        if call_node['opname'] == 'RTS':
            instr = Instruction(opcode=Instruction.OP_ReturnFromSubroutine)
        elif call_node['opname'] == 'END':
            instr = Instruction(opcode=Instruction.OP_EndOfProgram)
        elif call_node['opname'] == 'CALL':
            # looks up repetitions and if it is a pointer
            repeat, isrepeatpointer, infinite_loop = self.parse_repeat(call_node['repeat'])
            # if direct call
            if call_node['func'][0] == 'FUNC_NAME':
                called_id = self.functions_desc[call_node['func'][1]]['idfunc']
                if isrepeatpointer:
                    instr = Instruction(opcode=Instruction.OP_CallFuncPointerRepeat,
                                function_id=called_id,
                                infinite_loop=infinite_loop,
                                repeat=repeat)
                else:
                    instr = Instruction(opcode=Instruction.OP_CallFunction,
                                function_id=called_id,
                                infinite_loop=infinite_loop,
                                repeat=repeat)
            # if pointer to function
            elif call_node['func'][0] == 'PTR_FUNC':
                # checks
                self.pointers[call_node['func'][1]].is_ptr_type(call_node['func'][0])
                called_id = self.pointers[call_node['func'][1]].ptr_num()
                if isrepeatpointer:
                    instr = Instruction(opcode=Instruction.OP_CallPointerFuncPointerRepeat,
                                function_id=called_id,
                                infinite_loop=infinite_loop,
                                repeat=repeat)
                else:
                    instr = Instruction(opcode=Instruction.OP_CallPointerFunction,
                                function_id=called_id,
                                infinite_loop=infinite_loop,
                                repeat=repeat)
            else:
                raise ValueError('Unknown function call: %s' % call_node['func'][0])

        elif call_node['opname'] == 'JSR':
            # looks up repetitions and if it is a pointer
            repeat, isrepeatpointer, infinite_loop = self.parse_repeat(call_node['repeat'])
            # if direct call
            if call_node['subr'][0] == 'SUBR_NAME':
                # will be compiled later
                called = call_node['subr'][1]
                if isrepeatpointer:
                    instr = Instruction(opcode=Instruction.OP_JumpSubPointerRepeat,
                                subroutine=called,
                                infinite_loop=False,
                                repeat=repeat)
                else:
                    instr = Instruction(opcode=Instruction.OP_JumpToSubroutine,
                                subroutine=called,
                                infinite_loop=False,
                                repeat=repeat)
            elif call_node['subr'][0] == 'PTR_SUBR':
                self.pointers[call_node['subr'][1]].is_ptr_type(call_node['subr'][0])
                called = self.pointers[call_node['subr'][1]].ptr_num()
                # we have already the addresses of the pointers
                if isrepeatpointer:
                    instr = Instruction(opcode=Instruction.OP_JumpPointerSubPointerRepeat,
                                address=called,
                                infinite_loop=False,
                                repeat=repeat)
                else:
                    instr = Instruction(opcode=Instruction.OP_JumpPointerSubroutine,
                                address=called,
                                infinite_loop=False,
                                repeat=repeat)
            else:
                raise ValueError('Unknown function call: %s' % call_node['subr'][0])
        else:
            raise ValueError('Unkown instruction: %s' % call_node['opname'])

        return instr

    def parse_subroutine(self, sub_node):
        # print "subroutine"
        subname = sub_node['name']
        fullname = sub_node['comment']
        if self.verbose:
            print "   name = ", subname
            # print "   fullname = ", fullname

        sub = Subroutine()
        sub.name = subname
        sub.fullname = fullname

        for call_node in sub_node['instrs']:
            c_instr = self.parse_call(call_node)
            sub.instructions.append(c_instr)

        return sub

    def parse_subroutines(self, subroutines_node):
        # need to update the dictionary of subroutines
        for sub_node in subroutines_node:
            sub = self.parse_subroutine(sub_node)
            self.subroutines[sub.name] = sub
            self.subroutines_names.append(sub.name)

    def parse_mains(self, mains_node):

        for main_node in mains_node:
            main = self.parse_subroutine(main_node)
            self.mains[main.name] = main
            self.mains_names.append(main.name)

    def parse_result(self, result):

        self.unnamed_subroutine_num = 0

        # Get the parameters
        self.parse_parameters(result['constants'])

        # parse the channel descriptions
        self.parse_channels(result['clocks'])

        # parse the pointers
        self.parse_pointers(result['pointers'])

        # parse the sequencer functions
        self.parse_functions(result['functions'])
        # compiling pointers to functions
        for ptrname in self.pointers:
            seq_pointer = self.pointers[ptrname]
            if seq_pointer.pointer_type == 'PTR_FUNC':
                if not self.functions_desc.has_key(seq_pointer.target):
                    raise ValueError("Pointer to undefined function %s" %
                                     seq_pointer.target)
                seq_pointer.value = self.functions_desc[seq_pointer.target]['idfunc']

        # Parse all subroutines
        self.parse_subroutines(result['subroutines'])
        if self.verbose:
            print "SUBS", self.subroutines_names

        # Parse all 'mains' 
        self.parse_mains(result['mains'])
        if self.verbose:
            print "MAINS", self.mains_names
        # we will use 0x340000 (now in pointers) to point to the right one
        # initializing Main pointer if does not exist in file
        if 'Main' not in self.pointers:
            self.pointers['Main'] = SequencerPointer('MAIN', 'Main', target=self.mains_names[0])

        # group for compilation (the right routine terminations are included)
        allsubs = dict(self.mains)
        allsubs.update(self.subroutines)
        allsubsnames = self.mains_names + self.subroutines_names

        self.prg = Program_UnAssembled()

        self.prg.subroutines = allsubs  # key = name, value = subroutine object
        self.prg.subroutines_names = allsubsnames  # to keep the order
        self.prg.seq_pointers = self.pointers  # to be compiled for the missing subroutine references

        return ( self.prg,
                 self.functions_desc,
                 self.parameters_desc,
                 self.channels_desc )

    def parse_file(self, txtfile):
        # parser manages includes of other files and fuses dictionaries
        result = grammar.parse_file(txtfile, self.verbose)

        return self.parse_result(result)


# @classmethod
# def fromxmlfile(cls, xmlfile):
def fromtxtfile(txtfile, verbose=True):
    """
    Create and return a Sequencer instance from a text file.
    Raise an exception if the syntax is wrong.
    """

    functions = {}
    parameters = {}

    parser = TxtParser(verbose=verbose)
    ( prg,
      functions_desc,
      parameters_desc,
      channels_desc ) = parser.parse_file(txtfile)

    program = prg.compile()

    channels = bidi.BidiMap([v['channel']
                             for v in channels_desc.values()],
                            [v['name']
                             for v in channels_desc.values()])

    for k, v in functions_desc.iteritems():
        # re-index the function dictionary by function number
        functions[v['idfunc']] = v['function']

    for k in parameters_desc:
        if isinstance(parameters_desc[k]['value'], tuple):
            # converts to value in seconds
            parameters[k] = parameters_desc[k]['value'][0] * parser.time_units[parameters_desc[k]['value'][1]]
        else:
            # should be just an int
            parameters[k] = parameters_desc[k]['value']

    seq = Sequencer(channels=channels,
                    channels_desc=channels_desc,
                    functions=functions,
                    functions_desc=functions_desc,
                    program=program,
                    parameters=parameters,
                    pointers=prg.seq_pointers)

    return seq


Sequencer.fromtxtfile = staticmethod(fromtxtfile)


# f = 'lsst/camera/reb3/sequencer-reb3.txt'
# seq = Sequencer.fromtxtfile(f)

