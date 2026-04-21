class NodoAST:
    # Clase para todos los nodos de AST
    pass

    def traducirPy(self):
        # Traduccion de C++ a Python
        raise NotImplementedError('Metodo traducirPy() no implementado en este Nodo.')

    def traducirRuby(self):
        # Traduccion de C++ a Ruby
        raise NotImplementedError('Metodo traducirRuby() no implementado en este Nodo.')

    def generarCodigo():
        # Traducir de C++ ASSEMBLER
        raise NotImplementedError('Metodo generarCodigo() no implementado en este Nodo.')     

class NodoPrograma(NodoAST):
    # Nodo que representa un programa completo
    def __init__(self, funciones, main):
        self.variables = []
        self.funciones = funciones
        self.main = main

    def traducirPy(self):
        codigo = []
        for funcion in self.funciones:
            codigo.append(funcion.traducirPy())
        codigo.append(self.main.traducirPy())
        return "\n\n".join(codigo)
    
    def traducirRuby(self):
        codigo = []
        for funcion in self.funciones:
            codigo.append(funcion.traducirRuby())
        codigo.append(self.main.traducirRuby())
        return "\n\n".join(codigo)

    def generarCodigo(self):
        self.variables = [] 
        codigo = ["section .text", "global _start"]
        data = ["section .bss"]
        
        for funcion in self.funciones:
            codigo.append(funcion.generarCodigo())
        
        codigo.append("_start:")
        codigo.append(self.main.generarCodigo())
        
        codigo.append("    mov eax, 1  ; syscall exit")
        codigo.append("    xor ebx, ebx  ; codigo de salida 0")
        codigo.append("    int 0x80")

        for funcion in list(self.funciones) + [self.main]:
            for instruccion in funcion.cuerpo:
                if isinstance(instruccion, NodoAsignacion):
                    self.variables.append((instruccion.tipo[1], instruccion.nombre[1]))
            for parametro in funcion.parametros:
                self.variables.append((parametro.tipo[1], parametro.nombre[1]))

        for variable in self.variables:
            if variable[0] == 'int':
                data.append(f'    {variable[1]}:    resd 1')
        
        codigo = '\n'.join(codigo)
        return '\n'.join(data) + "\n" + codigo

class NodoLlamadaFuncion(NodoAST):
    # Nodo que representa una llamada de funcion
    def __init__(self, nombref, argumentos):
        self.nombre_funcion = nombref
        self.argumentos = argumentos

    def traducirPy(self):
        args = ", ".join(a.traducirPy() for a in self.argumentos)
        return f"{self.nombre_funcion}({args})"
    
    def traducirRuby(self):
        args = ", ".join(a.traducirRuby() for a in self.argumentos)
        return f"{self.nombre_funcion}({args})"

    def generarCodigo(self):
        codigo = []
        for arg in reversed(self.argumentos):
            codigo.append(arg.generarCodigo())
            codigo.append("    push eax  ; Pasar argumento a la pila")

        codigo.append(f"    call {self.nombre_funcion}  ; Llamar a la funcion {self.nombre_funcion}")
        codigo.append(f"    add esp, {len(self.argumentos) * 4}  ; Limpiar pila de argumentos")
        return "\n".join(codigo)

class NodoFuncion(NodoAST):
    # Nodo que representa la funcion
    def __init__(self, tipo_retorno, nombre, parametros, cuerpo):
        self.tipo_retorno = tipo_retorno
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

    def generarCodigo(self):
        codigo = f'{self.nombre[1]}:\n'
        if len(self.parametros) > 0:
            # Aqui guardamos en la pila el registro ax que usaremo
            for parametro in self.parametros:
                codigo += '\n    pop    eax'
                codigo += f'\n    mov [{parametro.nombre[1]}], eax'
        codigo += '\n'.join(c.generarCodigo() for c in self.cuerpo)
        codigo += '\n    ret'
        codigo += '\n'
        return codigo

    def traducirPy(self):
        params = ", ".join(p.traducirPy() for p in self.parametros)
        cuerpo = "\n    ".join(c.traducirPy() for c in self.cuerpo)
        return f"def {self.nombre[1]}({params}):\n    {cuerpo}"

    def traducirRuby(self):
        params = ", ".join(p.traducirRuby() for p in self.parametros)
        cuerpo = "\n  ".join(c.traducirRuby() for c in self.cuerpo)
        return f"def {self.nombre[1]}({params})\n  {cuerpo}\nend"

class NodoParametro(NodoAST):
    # Nodo que representa a un parametro de funcion
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

    def traducirPy(self):
        return self.nombre[1]

    def traducirRuby(self):
        return self.nombre[1]

class NodoAsignacion(NodoAST):
    # Nodo que representa un asignacion de variables
    def __init__(self, tipo, nombre, expresion):
        self.tipo = tipo
        self.nombre = nombre
        self.expresion = expresion

    def generarCodigo(self):
        codigo = self.expresion.generarCodigo()
        codigo += f'\n    mov [{self.nombre[1]}], eax'
        return codigo

    def traducirPy(self):
        return f'{self.nombre[1]} = {self.expresion.traducirPy()}'

    def traducirRuby(self):
        return f'{self.nombre[1]} = {self.expresion.traducirRuby()}'

class NodoOperacion(NodoAST):
    # Nodo que representa una operacion aritmetica
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

    def traducirPy(self):
        return f'{self.izquierda.traducirPy()} {self.operador[1]} {self.derecha.traducirPy()}'

    def traducirRuby(self):
        return f'{self.izquierda.traducirRuby()} {self.operador[1]} {self.derecha.traducirRuby()}'

    def generarCodigo(self):
        codigo = []
        codigo.append(self.izquierda.generarCodigo())
        codigo.append('    push    eax')
        codigo.append(self.derecha.generarCodigo())
        codigo.append('    mov    ebx, eax')
        codigo.append('    pop    eax')
        if self.operador[1] == '+':
            codigo.append('    add    eax, ebx')
        elif self.operador[1] == '-':
            codigo.append('    sub    eax, ebx  ;   eax - ebx')
        elif self.operador[1] == '*':
            codigo.append('    imul    ebx  ;   eax * ebx')
        elif self.operador[1] == '/':
            codigo.append('    cdq')
            codigo.append('    idiv ebx  ;  eax / ebx')
        return '\n'.join(codigo)

    def optimizar(self):
        # Si ambos lados son numeros, podemos calcular el resultado en tiempo de compilacion
        if isinstance(self.izquierda, NodoOperacion):
            self.izquierda.optimizar()
        else:
            izquierda = self.izquierda

        if isinstance(self.derecha, NodoOperacion):
            self.derecha.optimizar()
        else:
            derecha = self.derecha

        # Si ambos nodos son numeros realizamos a operacion de manera directa
        if isinstance(izquierda, NodoNumero) and isinstance(derecha, NodoNumero):
            izq = int(izquierda.valor[1])
            der = int(derecha.valor[1])
            if self.operador[1] == '+':
                valor = izq + der
            elif self.operador[1] == '-':
                valor = izq - der
            elif self.operador[1] == '*':
                valor = izq * der
            elif self.operador[1] == '/':
                valor = izq / der
            return NodoNumero(('NUMBER', str(valor)))
            
        # Simplificacion algebraica (valores neutros)
        if self.operador[1] == '*' and isinstance(derecha, NodoNumero) and derecha.valor[1] == '1':
            return izquierda        
        if self.operador[1] == '*' and isinstance(izquierda, NodoNumero) and izquierda.valor[1] == '1':
            return derecha
        if self.operador[1] == '+' and isinstance(derecha, NodoNumero) and derecha.valor[1] == '0':
            return izquierda        
        if self.operador[1] == '+' and isinstance(izquierda, NodoNumero) and izquierda.valor[1] == '0':
            return derecha

        # Si no se puede optimizar mas, se devuelve la expresion
        return NodoOperacion(izquierda, self.operador, derecha)

class NodoRetorno(NodoAST):
    # Nodo que representa a la sentencia return
    def __init__(self, expresion):
        self.expresion = expresion

    def traducirPy(self):
        return f'return {self.expresion.traducirPy()}'

    def traducirRuby(self):
        return f'return {self.expresion.traducirRuby()}'

    def generarCodigo(self):
        return self.expresion.generarCodigo()

class NodoIdentificador(NodoAST):
    # Nodo que representa a un identificador
    def __init__(self, nombre):
        self.nombre = nombre

    def traducirPy(self):
        return self.nombre[1]

    def traducirRuby(self):
        return self.nombre[1]

    def generarCodigo(self):
        return f'\n    mov eax, [{self.nombre[1]}]'

class NodoNumero(NodoAST):
    # Nodo que representa a un numero
    def __init__(self,valor):
        self.valor = valor

    def traducirPy(self):
        return str(self.valor[1])

    def traducirRuby(self):
        return str(self.valor[1])

    def generarCodigo(self):
        return f'\n    mov eax, {self.valor[1]}'

class NodoCadena(NodoAST):
    # Nodo que representa a una cadena
    def __init__(self, valor):
        self.valor = valor 

    def traducirPy(self):
        return self.valor[1] 

    def traducirRuby(self):
        return self.valor[1]

class NodoPrint(NodoAST):
    # Nodo que representa la sentencia print
    def __init__(self, argumentos):
        self.argumentos = argumentos

    def traducirPy(self):
        args = ", ".join(a.traducirPy() for a in self.argumentos)
        return f"print({args})"

    def traducirRuby(self):
        args = ", ".join(a.traducirRuby() for a in self.argumentos)
        return f"print {args}"

    def generarCodigo(self):
        codigo = []
        for arg in self.argumentos:

            codigo.append(arg.generarCodigo())

            codigo.append("    push edx")
            codigo.append("    push ecx")
            codigo.append("    push ebx")
            codigo.append("    push eax")

            # calcular longitud
            codigo.append("    mov ebx, eax")

            codigo.append("len_loop:")
            codigo.append("    cmp byte [eax], 0")
            codigo.append("    jz len_fin")
            codigo.append("    inc eax")
            codigo.append("    jmp len_loop")

            codigo.append("len_fin:")
            codigo.append("    sub eax, ebx")

            codigo.append("    mov edx, eax")
            codigo.append("    pop ecx")
            codigo.append("    mov ebx, 1")
            codigo.append("    mov eax, 4")
            codigo.append("    int 80h")

            codigo.append("    pop ebx")
            codigo.append("    pop ecx")
            codigo.append("    pop edx")

        return "\n".join(codigo)

class NodoPrintln(NodoAST):
    # Nodo que representa la sentencia println
    def __init__(self, argumentos):
        self.argumentos = argumentos

    def traducirPy(self):
        args = ", ".join(a.traducirPy() for a in self.argumentos)
        return f"print({args})"

    def traducirRuby(self):
        args = ", ".join(a.traducirRuby() for a in self.argumentos)
        return f"puts {args}"

    def generarCodigo(self):
        codigo = []
        for arg in self.argumentos:

            codigo.append(arg.generarCodigo())

            codigo.append("    push edx")
            codigo.append("    push ecx")
            codigo.append("    push ebx")
            codigo.append("    push eax")

            codigo.append("    mov ebx, eax")

            codigo.append("len_loop2:")
            codigo.append("    cmp byte [eax], 0")
            codigo.append("    jz len_fin2")
            codigo.append("    inc eax")
            codigo.append("    jmp len_loop2")

            codigo.append("len_fin2:")
            codigo.append("    sub eax, ebx")

            codigo.append("    mov edx, eax")
            codigo.append("    pop ecx")
            codigo.append("    mov ebx, 1")
            codigo.append("    mov eax, 4")
            codigo.append("    int 80h")

            codigo.append("    pop ebx")
            codigo.append("    pop ecx")
            codigo.append("    pop edx")

            # imprimir salto de linea
            codigo.append("    push eax")
            codigo.append("    mov eax, 0Ah")
            codigo.append("    push eax")
            codigo.append("    mov eax, esp")

            codigo.append("    mov edx, 1")
            codigo.append("    mov ecx, eax")
            codigo.append("    mov ebx, 1")
            codigo.append("    mov eax, 4")
            codigo.append("    int 80h")

            codigo.append("    pop eax")
            codigo.append("    pop eax")

        return "\n".join(codigo)

class NodoPrintf(NodoAST):
    def __init__(self, argumentos):
        self.argumentos = argumentos 

    def traducirPy(self):
        # Caso vacío
        if not self.argumentos:
            return "print()"

        formato = self.argumentos[0]
        vars_ = self.argumentos[1:]

        # Si el primer argumento NO es string, caemos a print normal
        if not isinstance(formato, NodoCadena):
            args = ", ".join(a.traducirPy() for a in self.argumentos)
            return f"print({args})"

        # formato.valor[1] incluye comillas -> '"Hola %d"'
        texto_con_comillas = formato.valor[1]
        contenido = texto_con_comillas[1:-1]  # sin comillas

        # Reemplazo básico: %d %f %s -> {variable}
        for v in vars_:
            if "%d" in contenido:
                contenido = contenido.replace("%d", "{" + v.traducirPy() + "}", 1)
            elif "%f" in contenido:
                contenido = contenido.replace("%f", "{" + v.traducirPy() + "}", 1)
            elif "%s" in contenido:
                contenido = contenido.replace("%s", "{" + v.traducirPy() + "}", 1)

        return f'print(f"{contenido}")'

    def traducirRuby(self):
        args = ", ".join(a.traducirRuby() for a in self.argumentos)
        return f"printf({args})"

class NodoIf(NodoAST):
    def __init__(self, condicion, cuerpo, sino=None):
        self.condicion = condicion
        self.cuerpo = cuerpo
        self.sino = sino

    def traducirPy(self):
        cuerpo = "\n    ".join(c.traducirPy() for c in self.cuerpo)
        codigo = f"if {self.condicion.traducirPy()}:\n    {cuerpo}"
        if self.sino:
            sino = "\n    ".join(c.traducirPy() for c in self.sino)
            codigo += f"\nelse:\n    {sino}"
        return codigo
    
    def traducirRuby(self):
        cuerpo = "\n  ".join(c.traducirRuby() for c in self.cuerpo)
        codigo = f"if {self.condicion.traducirRuby()}\n  {cuerpo}"
        if self.sino:
            sino = "\n  ".join(c.traducirRuby() for c in self.sino)
            codigo += f"\nelse\n  {sino}\nend"
        else:
            codigo += "\nend"
        return codigo

class NodoWhile(NodoAST):
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo

    def traducirPy(self):
        cuerpo = "\n    ".join(c.traducirPy() for c in self.cuerpo)
        return f"while {self.condicion.traducirPy()}:\n    {cuerpo}"
    
    def traducirRuby(self):
        cuerpo = "\n  ".join(c.traducirRuby() for c in self.cuerpo)
        return f"while {self.condicion.traducirRuby()}\n  {cuerpo}\nend"
    
class NodoFor(NodoAST):
    def __init__(self, init, condicion, incremento, cuerpo):
        self.init = init
        self.condicion = condicion
        self.incremento = incremento
        self.cuerpo = cuerpo

    def traducirPy(self):
        cuerpo = "\n    ".join(c.traducirPy() for c in self.cuerpo)
        return f"# for convertido\n{self.init.traducirPy()}\nwhile {self.condicion.traducirPy()}:\n    {cuerpo}\n    {self.incremento.traducirPy()}"
    
    def traducirRuby(self):
        cuerpo = "\n  ".join(c.traducirRuby() for c in self.cuerpo)
        return f"# for convertido\n{self.init.traducirRuby()}\nwhile {self.condicion.traducirRuby()}\n  {cuerpo}\n  {self.incremento.traducirRuby()}\nend"

# Analizador sintactico
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual
        else:
            raise SyntaxError(f'Error sintactico: se esperaba {tipo_esperado}, pero se encontro: {token_actual}')

    def parsear(self):
        return self.programa()
    
    def programa(self):
        funciones = []
        main = None
    
        while self.obtener_token_actual() is not None:
            nodo = self.funcion()
            if nodo.nombre[1] == 'main':
                main = nodo
            else:
                funciones.append(nodo)
    
        if main is None:
            raise SyntaxError('Error: no se encontro una funcion main')
    
        return NodoPrograma(funciones, main)
        
    def funcion(self):
        # Gramatica para una funcion: int IDENTIFIER (int IDENTIFIER) {cuerpo}
        tipo_retorno = self.coincidir('KEYWORD') # Tipo de retorno (ej. int)
        nombre_funcion = self.coincidir('IDENTIFIER') # Nombre de la funcion
        self.coincidir('DELIMITER') # Se espera un (
        if nombre_funcion[1] == 'main':
            parametros = []
        else:            
            parametros = self.parametros() # Regla para los parametros
        self.coincidir('DELIMITER') # Se espera un )
        self.coincidir('DELIMITER') # Se espera un {
        cuerpo = self.cuerpo() # Regla parael cuerpo de la funcino
        self.coincidir('DELIMITER') # Se espera un }
        return NodoFuncion(tipo_retorno, nombre_funcion, parametros, cuerpo)

    def parametros(self):
        lista_parametros = []
        # Reglas para parametros: int IDENTIFIER (, int IDENTIFIER)*
        tipo = self.coincidir('KEYWORD') # Tipo de parametro
        nombre = self.coincidir('IDENTIFIER') # Nombre del parametro
        lista_parametros.append(NodoParametro(tipo, nombre))
        while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',': 
            self.coincidir('DELIMITER') # Se espera una ,
            tipo = self.coincidir('KEYWORD') # Tipo de parametro
            nombre = self.coincidir('IDENTIFIER') # Nombre del parametro
            lista_parametros.append(NodoParametro(tipo, nombre))
        return lista_parametros

    def cuerpo(self):
        # Gramatica para el cuerpo: return IDENTIFIER OPERATOR IDENTIFIER:
        instrucciones = []
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != '}': 
            if self.obtener_token_actual()[1] == 'return':
                instrucciones.append(self.retorno())
            elif self.obtener_token_actual()[1] == 'print':
                instrucciones.append(self.sentencia_print())
            elif self.obtener_token_actual()[1] == 'printf':
                instrucciones.append(self.sentencia_printf())
            elif self.obtener_token_actual()[1] == 'println':
                instrucciones.append(self.sentencia_println())
            elif self.obtener_token_actual()[1] == 'if':
                instrucciones.append(self.sentencia_if())

            elif self.obtener_token_actual()[1] == 'while':
                instrucciones.append(self.sentencia_while())

            elif self.obtener_token_actual()[1] == 'for':
                instrucciones.append(self.sentencia_for())
            else:
                instrucciones.append(self.asignacion())
        return instrucciones

    def asignacion(self):
        # Gramatica para la estructura de una asignacion
        tipo = self.coincidir('KEYWORD') # Se espera un tipo
        nombre = self.coincidir('IDENTIFIER')
        self.coincidir('OPERATOR') # Se espera un =
        expresion = self.expresion() 
        self.coincidir('DELIMITER') # Se espera un ;
        return NodoAsignacion(tipo, nombre, expresion)

    def retorno(self):
        self.coincidir('KEYWORD') # Se espera un return
        expresion = self.expresion()
        self.coincidir('DELIMITER') # Se espera un ;
        return NodoRetorno(expresion)

    def expresion(self):
        izquierda = self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[0] == 'OPERATOR': 
            operador = self.coincidir('OPERATOR')
            derecha = self.termino()
            izquierda = NodoOperacion(izquierda, operador, derecha)
        return izquierda

    def termino(self):
        token = self.obtener_token_actual()
        if token[0] == 'NUMBER':
            return NodoNumero(self.coincidir('NUMBER'))
        elif token[0] == 'IDENTIFIER':
            identificador = self.coincidir('IDENTIFIER')
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == '(': 
                self.coincidir('DELIMITER')
                argumentos = self.llamadaFuncion()
                self.coincidir('DELIMITER')
                return NodoLlamadaFuncion(identificador[1], argumentos)
            else:
                return NodoIdentificador(identificador)
        elif token[0] == 'STRING':
            return NodoCadena(self.coincidir('STRING'))
        else:
            raise SyntaxError(f'Expresion no valida: {token}')

    def llamadaFuncion(self):
        argumentos = []
        # Reglas para argumentos: IDENTIFIER | NUMBER (, IDENTIFIER | NUMBER)*
        sigue = True
        token = self.obtener_token_actual()
        while sigue:
            sigue = False
            if token[0] == 'NUMBER':
                argumento = NodoNumero(self.coincidir('NUMBER'))
            elif token[0] == 'IDENTIFIER':
                argumento = NodoIdentificador(self.coincidir('IDENTIFIER'))
            elif token[0] == 'STRING':
                argumento = NodoCadena(self.coincidir('STRING'))
            else:
                raise SyntaxError(f'Error de sintaxis, se esperaba un IDENTsIFICADOR|NUMERO pero se encontro_ {token}')
            argumentos.append(argumento)
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
                self.coincidir('DELIMITER') # Se espera una coma
                token = self.obtener_token_actual()
                sigue = True
        return argumentos

    def sentencia_print(self):
        self.coincidir('KEYWORD')     
        self.coincidir('DELIMITER')   
        argumentos = []
        if self.obtener_token_actual() and self.obtener_token_actual()[1] != ')':
            argumentos = self.llamadaFuncion()
        self.coincidir('DELIMITER')  
        self.coincidir('DELIMITER')   
        return NodoPrint(argumentos)    
    
    def sentencia_printf(self):
        self.coincidir('KEYWORD')    
        self.coincidir('DELIMITER')   
        argumentos = []
        if self.obtener_token_actual() and self.obtener_token_actual()[1] != ')':
            argumentos = self.llamadaFuncion()
        self.coincidir('DELIMITER')   
        self.coincidir('DELIMITER')   
        return NodoPrintf(argumentos)
    
    def sentencia_println(self):
        self.coincidir('KEYWORD')
        self.coincidir('DELIMITER')
        argumentos = []
        if self.obtener_token_actual() and self.obtener_token_actual()[1] != ')':
            argumentos = self.llamadaFuncion()
        self.coincidir('DELIMITER')
        self.coincidir('DELIMITER')
        return NodoPrintln(argumentos)
    
    def sentencia_if(self):
        self.coincidir('KEYWORD')    
        self.coincidir('DELIMITER')  
        condicion = self.expresion()
        self.coincidir('DELIMITER') 
        self.coincidir('DELIMITER') 
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER')  
        sino = None
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == 'else':
            self.coincidir('KEYWORD')
            self.coincidir('DELIMITER')  # {
            sino = self.cuerpo()
            self.coincidir('DELIMITER')  # }
        return NodoIf(condicion, cuerpo, sino)

    def sentencia_while(self):
        self.coincidir('KEYWORD')    
        self.coincidir('DELIMITER') 
        condicion = self.expresion()
        self.coincidir('DELIMITER')  
        self.coincidir('DELIMITER')  
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER') 
        return NodoWhile(condicion, cuerpo)

    def sentencia_for(self):
        self.coincidir('KEYWORD')
        self.coincidir('DELIMITER')
        init = self.asignacion()
        condicion = self.expresion()
        incremento = self.expresion()
        self.coincidir('DELIMITER')
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER')
        return NodoFor(init, condicion, incremento, cuerpo)