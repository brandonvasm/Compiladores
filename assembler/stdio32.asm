; Bloque de funciones de entrada-salida estándar de 32 bits 
; creado por: Brandon
; fecha: 26 de febrero de 2026


; -------------------- Calculo de tamaño de cadena -----------

StrLen:
	push	ebx		; guardar en pila el contenido de ebx 
	mov	ebx, eax	; ebx = direccion de msg
	


sigChar:
        cmp	byte [eax], 0	; si [eax] == NULL
        jz	finConteo 
        inc	eax 
        jmp	sigChar 
finConteo:
        sub	eax, ebx 
	pop	ebx 
	ret

; ----------------- printStr(Max = cadena) --------------------------
printStr: 
	push	edx			; edx a pila
	push	ecx			; ecx a pila
	push	ebx			; ebx a pila			
	push	eax 			; eax a pila
	
	call	StrLen			; llamada a calculo de longitud de cadena
					; la longitud se devuelve en eax 

        mov	edx, eax                ; edx = 12 (numero de caracteres)
        pop 	ecx                     ; ecx = msg (direccin de cadena)
        mov 	ebx, 1                  ; escrive al STDOUT_file 
        mov 	eax, 4                  ; invocar SYS_WRITE 
        int 	80h 

	pop 	ebx			; extraer pila en ebx
 	pop	ecx 		        ; extraer pila en ecx
	pop   	edx 			; extraer pila en edx 
	ret 


;------------------- printStrLen(eax = cadena)-----------------------
printStrLn:
	call	printStr		; impresion de cadena
	push	eax			; resguardar eax
	mov	eax, 0Ah		; eax = 0Ah (Enter)
	push	eax			; colar el valor de eax en pila
	mov	eax, esp 		; eax = Puntero de pilas $$
	call	printStr
	pop	eax
	pop	eax
	ret
		
	

; --------------------- Salida al sistema --------------------------
quit:
	mov	ebx, 0	; return 0
	mov	eax, 1	; invoca SYS_EXIT
	int	80h
