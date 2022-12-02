#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
#include <inttypes.h>

/*
 Processor's clock cycle (global clock)
 */
unsigned long long cpu_cycles = 0;

/*
 Processor's States:
   (1) Register (x32)
   (2) Program Counter
   (3) Data Memory
   (4) Instruction Memory
 */
#define REGS_SIZE   32
#define IMEM_SIZE   32*1024 // 4 KiB of instruction memory (I$)
#define DMEM_SIZE   32*1024 // 4 KiB of data memory (D$)

long int        reg[REGS_SIZE];  //(1) -> 32 (general-purpose) registers
unsigned long   PC = 0;   //(2) -> Let's assume that program segment starts from 0x00000000
unsigned long   inst_mem[IMEM_SIZE];
unsigned long   data_mem[DMEM_SIZE];

char            DMEM_flag[DMEM_SIZE];   // a set of flags for checking the data memory is touched or not
/*
  Tip: Data types
    (i) long = 4 bytes = 32 bits
    (ii) long long int = 8 bytes = 64 bits
*/

/*
  Functions for modelling 5-stages with 1 control unit
    (1) IF: Fetching instructions from instruction memory
    (2) ID: Decoding instructions (also access registers)
    (3) EX: Executing (ALU)
    (4) MEM: Accessing to data memory
    (5) WB: Write-back (store result data to a target register)
    (6) Control Unit

    * return type of IF, ID, EX, MEM, WB, Control_Unit function should not be changed.
*/
unsigned long IF(unsigned long addr);
unsigned long ID(unsigned addr_rs1, unsigned addr_rs2);
unsigned long EX(unsigned long inputA, unsigned long inputB, int ALUSel);
unsigned long MEM(unsigned long addr, unsigned long dataW, int MemRW);
unsigned long WB(unsigned long dataD, unsigned addr_rd1, int RegWEn);
unsigned long Control_Unit(unsigned long inst, int BrEq, int BrLT);

void init_states(FILE* _binary_exe);
void print_statistics(); // print processor's clock cycles
void dump_registers();   // print all contents of registers
void dump_memory();      // print all used data in (data) memory

int main(int argc, char** argv)
{
    int halt = 0;

    FILE* _exe = fopen(argv[1], "r");
    init_states(_exe);

    while (!halt)
    {
        //TODO: add or fix statements in this while loop
        //PC = PC + ???
        IF(PC);
        ID();
        EX();
        MEM();
        WB();
        /*
         Exit condition: when the value of 31st register is 0xDEADBEEF, then stop the simulation.
                        (End of the program)
         */
        if (reg[31] == 0xDEADBEEF)
            halt = 1;
        cpu_cycles++;
    }

    print_statistics(); // print processor's clock cycles
    dump_registers();   // print all contents of registers
    dump_memory();      // print all used data in (data) memory

    return 0;
}

void init_states(FILE* _binary_exe)
{
    if (_binary_exe == NULL)
    {
        fprintf(stdout, "File path is missing...\n")
        exit(-1);
    }

    /* 
     Initializing instruction memory
     - Copying all instructions from a given binary executable file
     - One element in inst_mem[] contains one line of RV32I's instruction
     */
    unsigned long *p_inst = inst_mem;
    while (!feof(_binary_exe))
    {
        fscanf(_binary_exe, "%lx", &(p_inst++));
    }

    /*
     Initializing register value as 0
     */
    memset(reg, 0, sizeof(long int) * REGS_SIZE);

    /*
     Initializing program counter (PC)
    */
    PC = 0; // -> Let's assume that program segment starts from 0x00000000

    /*
     Reset global clock cycles
    */
    cpu_cycles = 0;

    memset(DMEM_flag, 0, sizeof(char) * DMEM_SIZE);
}

/* TODO: your work should be done with completing these five functions: */
void IF()
{

}

void ID()
{

}

void EX()
{

}

void MEM()
{

}

void WB()
{

}

void print_statistics()
{
    fprintf(stdout, "Processor's clock cycles: %lld\n", cpu_cycles);
}

void dump_registers()
{
    fprintf(stdout, ">>>>>>>>[REGISTER DUMP]<<<<<<<\n");
    fprintf(stdout, "PC: = %ld\n", PC);
    for (int i=0; i<REGS_SIZE; i++)
        fprintf(stdout, "x%2d = %d\n", reg[i]);
    fprintf(stdout, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n");
}

void dump_memory()
{
    fprintf(stdout, ">>>>>>>>[MEMORY DUMP]<<<<<<<<<\n");
    for (int i=0; i<DMEM_SIZE; i++)
    {
        if (DMEM_flag[i] != 0)
            fprintf(stdout, "%lx : \n", data_mem[i]);
    }
    fprintf(stdout, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n");
}
