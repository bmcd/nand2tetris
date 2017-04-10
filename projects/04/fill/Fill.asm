// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
(MAIN)
@KBD
D=M
@WHITE
D;JEQ
(BLACK)
@color
M=0
@color
M=M-1
@DRAW
D;JMP

(WHITE)
@color
M=0
@DRAW
D;JMP

(DRAW)
@SCREEN
D=A
@current
M=D
(LOOP)
@color
D=M
@current
A=M
M=D
@current
M=M+1
D=M
@24576
D=A-D
@MAIN
D;JLE
@LOOP
D;JMP





