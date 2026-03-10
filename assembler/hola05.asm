; Hola mundo! version 5
; creador por: brandon
; fecha: 3 de marzo de 2026
; compilar: nasm -f elf hola05.asm
; vincular con: ld -m elf_i386 hola05.o -o holamundo05

%include	'stdio32.asm'

SECTION .data
        msg1    db      'Hola mundo sin ENTER!',0		; cadena msg = 'Hola mundo!'
	msg2	db      'Esta cadena despues del hola',0
	msg3	db	'Esta cadena en nueva linea', 0	
SECTION .text
global _start

_start:
	; -------- printStr(msg) ---------
	mov	eax, msg1
	call	printStr 

	mov	eax, msg2
	call	printStrLn
	
	mov 	eax, msg3
	call	printStrLn

	call	quit