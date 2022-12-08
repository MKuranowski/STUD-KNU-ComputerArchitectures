package main

// Student: Mikolaj Kuranowski
// Student ID: 2020427681
// Date: 2022-12-08
// Course: Computer Architectures

import (
	"bufio"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
)

const Registers = 32
const IMemSize = 32 * 1024
const DMemSize = 32 * 1024

var ByteOrder binary.ByteOrder = binary.LittleEndian

const (
	WBSelectorNone = iota
	WBSelectorALU
	WBSelectorMemory
	WBSelectorPCPlus4
)

// ALUSelectors are combined with this equation: `(funct7 << 4) | funct3`
const (
	ALUSelectorADD = 0x000
	ALUSelectorSUB = 0x200
	ALUSelectorXOR = 0x004
	ALUSelectorOR  = 0x006
	ALUSelectorAND = 0x007
	ALUSelectorSLL = 0x001
	ALUSelectorSRL = 0x005
	ALUSelectorMUL = 0x010
	ALUSelectorDIV = 0x014
	ALUSelectorREM = 0x016
)

// BranchSelectors simply represent the value of `funct3` in BRANCH instructions
const (
	BranchSelectorEQ  = 0x0
	BranchSelectorNE  = 0x1
	BranchSelectorLT  = 0x4
	BranchSelectorGE  = 0x5
	BranchSelectorLTU = 0x6
	BranchSelectorGEU = 0x7
)

const (
	OperationInvalid = 0x00
	OperationALUReg  = 0x33
	OperationALUImm  = 0x13
	OperationLoad    = 0x03
	OperationStore   = 0x23
	OperationBranch  = 0x63
	OperationJAL     = 0x6F
	OperationJALR    = 0x67
	OperationLUI     = 0x37
	OperationAUIPC   = 0x17
)

func signExtend(x uint32, bits uint32) uint32 {
	if x&(1<<(bits-1)) != 0 {
		// MSB set - sign extend bits
		x |= 0xFFFF_FFFF &^ ((1 << bits) - 1)
	}
	return x
}

func readImmI(instruction uint32) uint32 {
	return signExtend((instruction>>20)&0xFFF, 12)
}

func readImmU(instruction uint32) uint32 {
	return instruction & 0xFFFF_F000
}

func readImmS(instruction uint32) uint32 {
	bits0to4 := (instruction >> 7) & 0x1F
	bits5to11 := (instruction >> 25) & 0x7F
	return signExtend((bits5to11<<5)|bits0to4, 12)
}

func readImmB(instruction uint32) uint32 {
	bits1to4 := (instruction >> 8) & 0xF
	bits5to10 := (instruction >> 25) & 0x3F
	bit11 := (instruction >> 7) & 0x1
	bit12 := (instruction >> 31) & 0x1
	return signExtend((bits1to4<<1)|(bits5to10<<5)|(bit11<<11)|(bit12<<12), 13)
}

func readImmJ(instruction uint32) uint32 {
	bits1to10 := (instruction >> 21) & 0x3FF
	bit11 := (instruction >> 20) & 0x1
	bits12to19 := (instruction >> 12) & 0xFF
	bit20 := (instruction >> 31) & 0x1
	return signExtend((bits1to10<<1)|(bit11<<11)|(bits12to19<<12)|(bit20<<20), 21)
}

type Processor struct {
	Clock     uint32
	PC        uint32
	Registers [Registers]uint32
	Flags     ProcessorFlags

	IMem          [IMemSize]uint8
	DMem          [IMemSize]uint8
	TouchedMemory [IMemSize]bool
}

type ProcessorFlags struct {
	WBSelector              uint8
	PCSel, ASel, BSel, BrUn bool
}

type decodedInstruction struct {
	rs1Value, rs2Value, rd, imm uint32

	funct uint16
	op    uint8
}

func (p *Processor) InstructionFetch(address uint32) uint32 {
	if address%4 != 0 {
		panic(fmt.Errorf("misaligned instruction fetch from 0x%08x", address))
	}
	return ByteOrder.Uint32(p.IMem[address : address+4])
}

func (p *Processor) InstructionDecode(instruction uint32) (d decodedInstruction) {
	d.op = uint8(instruction & 0x7F)
	switch d.op {
	case OperationInvalid:
		panic(fmt.Errorf("invalid instruction at PC=0x%08x", p.PC))

	case OperationALUReg: // R-type
		d.funct = uint16(((instruction >> 21) & 0x7F0) | ((instruction >> 12) & 0x7))
		d.rs1Value = p.Registers[(instruction>>15)&0x1F]
		d.rs2Value = p.Registers[(instruction>>20)&0x1F]
		d.rd = (instruction >> 7) & 0x1F

		p.Flags.WBSelector = WBSelectorALU

	case OperationALUImm, OperationLoad, OperationJALR: // I-type
		d.funct = uint16((instruction >> 12) & 0x7)
		d.rs1Value = p.Registers[(instruction>>15)&0x1F]
		d.rd = (instruction >> 7) & 0x1F
		d.imm = readImmI(instruction)

		p.Flags.PCSel = d.op == OperationJALR
		p.Flags.BSel = true
		if d.op == OperationLoad {
			p.Flags.WBSelector = WBSelectorMemory
		} else if d.op == OperationJALR {
			p.Flags.WBSelector = WBSelectorPCPlus4
		} else {
			p.Flags.WBSelector = WBSelectorALU
		}

	case OperationStore: // S-type
		d.funct = uint16((instruction >> 12) & 0x7)
		d.rs1Value = p.Registers[(instruction>>15)&0x1F]
		d.rs2Value = p.Registers[(instruction>>20)&0x1F]
		d.imm = readImmS(instruction)

		p.Flags.BSel = true

	case OperationBranch: // B-type
		d.funct = uint16((instruction >> 12) & 0x7)
		d.rs1Value = p.Registers[(instruction>>15)&0x1F]
		d.rs2Value = p.Registers[(instruction>>20)&0x1F]
		d.imm = readImmB(instruction)

		p.Flags.ASel = true
		p.Flags.BSel = true
		p.Flags.BrUn = d.funct&0x2 != 0

	case OperationJAL: // J-type
		d.rd = (instruction >> 7) & 0x1F
		d.imm = readImmJ(instruction)

		p.Flags.PCSel = true
		p.Flags.ASel = true
		p.Flags.BSel = true
		p.Flags.WBSelector = WBSelectorPCPlus4

	case OperationLUI, OperationAUIPC: // U-type
		d.rd = (instruction >> 7) & 0x1F
		d.imm = readImmU(instruction)

		p.Flags.ASel = d.op == OperationAUIPC
		p.Flags.BSel = true
		p.Flags.WBSelector = WBSelectorALU

	default:
		panic(fmt.Errorf("unexpected op 0x%02x at 0x%08x", d.op, p.PC))
	}
	return
}

func (p *Processor) executeBranchSelector(d decodedInstruction) {
	switch d.funct {
	case BranchSelectorEQ:
		p.Flags.PCSel = d.rs1Value == d.rs2Value
	case BranchSelectorNE:
		p.Flags.PCSel = d.rs1Value != d.rs2Value
	case BranchSelectorLT:
		p.Flags.PCSel = int32(d.rs1Value) < int32(d.rs2Value)
	case BranchSelectorGE:
		p.Flags.PCSel = int32(d.rs1Value) >= int32(d.rs2Value)
	case BranchSelectorLTU:
		p.Flags.PCSel = d.rs1Value < d.rs2Value
	case BranchSelectorGEU:
		p.Flags.PCSel = d.rs1Value >= d.rs2Value
	default:
		panic(fmt.Errorf("invalid branch selector: 0x%x", d.funct))
	}
}

func (p *Processor) executeALU(d decodedInstruction) uint32 {
	// Select the first operand
	a := d.rs1Value
	if p.Flags.ASel {
		a = p.PC
	}

	// Select the second operand
	b := d.rs2Value
	if p.Flags.BSel {
		b = d.imm
	}

	// Select the operation
	s := uint16(ALUSelectorADD)
	if d.op == OperationALUReg || d.op == OperationALUImm {
		s = d.funct
	}

	// Perform the operation
	switch s {
	case ALUSelectorADD:
		return a + b
	case ALUSelectorSUB:
		return a - b
	case ALUSelectorXOR:
		return a ^ b
	case ALUSelectorOR:
		return a | b
	case ALUSelectorAND:
		return a & b
	case ALUSelectorSLL:
		return a << b
	case ALUSelectorSRL:
		return a >> b
	case ALUSelectorMUL:
		return uint32(int32(a) * int32(b))
	case ALUSelectorDIV:
		return uint32(int32(a) / int32(b))
	case ALUSelectorREM:
		return uint32(int32(a) % int32(b))
	default:
		panic(fmt.Errorf("invalid ALU selector: 0x%03x", s))
	}
}

func (p *Processor) Execute(d decodedInstruction) uint32 {
	if d.op == OperationBranch {
		p.executeBranchSelector(d)
	}

	return p.executeALU(d)
}

func (p *Processor) Memory(address, data uint32, doWrite bool) uint32 {
	// NOTE: Assuming only word load/stores are permitted
	if address%4 != 0 {
		panic(fmt.Errorf("misaligned memory access to 0x%08x at PC=0x%08x", address, p.PC))
	}

	if doWrite {
		ByteOrder.PutUint32(p.DMem[address:address+4], data)
		p.TouchedMemory[address] = true
		p.TouchedMemory[address+1] = true
		p.TouchedMemory[address+2] = true
		p.TouchedMemory[address+3] = true
	} else {
		data = ByteOrder.Uint32(p.DMem[address : address+4])
	}

	return data
}

func (p *Processor) WriteBack(memory, alu, register uint32) {
	// Don't write to x0
	if register == 0 {
		return
	}

	switch p.Flags.WBSelector {
	case WBSelectorNone:

	case WBSelectorALU:
		p.Registers[register] = alu

	case WBSelectorMemory:
		p.Registers[register] = memory

	case WBSelectorPCPlus4:
		p.Registers[register] = p.PC + 4

	default:
		panic(fmt.Errorf("invalid WBSelector: %x", p.Flags.WBSelector))
	}
}

func (p *Processor) ControlUnit(alu uint32) {
	if p.Flags.PCSel {
		p.PC = alu
	} else {
		p.PC += 4
	}
}

func (p *Processor) MainLoop() {
	for p.Registers[31] != 0xDEADBEEF {
		p.Flags = ProcessorFlags{} // Clear flags

		instruction := p.InstructionFetch(p.PC)
		decoded := p.InstructionDecode(instruction)

		alu := p.Execute(decoded)

		mem := uint32(0)
		if decoded.op == OperationStore || decoded.op == OperationLoad {
			mem = p.Memory(alu, decoded.rs2Value, decoded.op == OperationStore)
		}

		p.WriteBack(mem, alu, decoded.rd)
		p.ControlUnit(alu)

		p.Clock++
	}
}

func (p *Processor) PrintStatistics() {
	fmt.Println("Processor's clock cycles:", p.Clock)
}

func (p *Processor) DumpRegisters() {
	fmt.Println(">>>>>>>>[REGISTER DUMP]<<<<<<<")
	fmt.Println("PC: =", p.PC)
	for i, value := range p.Registers {
		fmt.Printf("x%02d = %d\n", i, int32(value))
	}
	fmt.Println(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
}

func (p *Processor) DumpMemory() {
	fmt.Println(">>>>>>>>[MEMORY DUMP]<<<<<<<<<")
	for addr, value := range p.DMem {
		if p.TouchedMemory[addr] {
			fmt.Printf("%x : %v\n", addr, value)
		}
	}
	fmt.Println(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
}

func (p *Processor) LoadProgramFromBitStrings(r io.Reader) {
	addr := uint32(0)
	lineNo := 1

	br := bufio.NewReader(r)
	for {
		// Read next line
		line, err := br.ReadString('\n')
		if errors.Is(err, io.EOF) {
			break
		} else if err != nil {
			panic(fmt.Errorf("failed to read input: %w", err))
		} else if line == "\n" {
			// Ignore empty lines
			lineNo++
			continue
		}

		// Parse the instruction
		instruction, err := strconv.ParseUint(strings.Trim(line, "\n"), 2, 32)
		if err != nil {
			panic(fmt.Errorf("failed to parse program (at line %d): %w", lineNo, err))
		}

		// Save the instruction
		ByteOrder.PutUint32(p.IMem[addr:addr+4], uint32(instruction))

		// Advance counter
		addr += 4
		lineNo++
	}
}

func (p *Processor) Run(bitStringProgram io.Reader) {
	*p = Processor{} // Reset state
	p.LoadProgramFromBitStrings(bitStringProgram)
	p.MainLoop()
	p.PrintStatistics()
	p.DumpRegisters()
	p.DumpMemory()
}

func main() {
	// Open input file
	in := os.Stdin
	if len(os.Args) >= 2 {
		var err error
		in, err = os.Open(os.Args[1])
		if err != nil {
			panic(fmt.Errorf("failed to open %q: %w", os.Args[1], err))
		}
		defer in.Close()
	}

	// Run the program
	p := new(Processor)
	p.Run(in)
}
