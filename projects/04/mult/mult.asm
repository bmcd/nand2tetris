// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.
	@R0
	D=M
	@x
	M=D
	@R1
	D=M
	@y
	M=D
	@sum
	M=0
	@x
	D=M
	@END
	D;JEQ
(LOOP)
	@y
	D=M
	@END
	D;JEQ
	@x
	D=M
	@sum
	M=M+D
	@y
	M=M-1
	@LOOP
	D;JMP
(END)
	@sum
	D=M
	@R2
	M=D

