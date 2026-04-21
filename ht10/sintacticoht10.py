
class NodoAST:
    def generarCodigo(self):
        raise NotImplementedError('generarCodigo() no implementado')
    def optimizar(self):
        return self


class NodoPrograma(NodoAST):
  
    def __init__(self, funciones, main):
        self.variables = []
        self.funciones  = funciones
        self.main       = main        

    def generarCodigo(self):
        self.variables = []
        codigo = ["section .text", "global _start"]
        data   = ["section .bss"]

        for fn in self.funciones:
            codigo.append(fn.generarCodigo())

        codigo.append("_start:")
        codigo.append(self.main.generarCodigo())
        codigo.append("    mov eax, 1")
        codigo.append("    xor ebx, ebx")
        codigo.append("    int 0x80")

        for fn in list(self.funciones) + [self.main]:
            for inst in fn.cuerpo:
                if isinstance(inst, NodoAsignacion):
                    self.variables.append(inst.nombre[1])
            for param in fn.parametros:
                self.variables.append(param.nombre[1])
        for var in self.variables:
            data.append(f'    {var}: resd 1')

        return '\n'.join(data) + '\n' + '\n'.join(codigo)


class NodoFuncion(NodoAST):
    def __init__(self, tipo_retorno, nombre, parametros, cuerpo):
        self.tipo_retorno = tipo_retorno
        self.nombre      = nombre       
        self.parametros  = parametros 
        self.cuerpo      = cuerpo      

    def generarCodigo(self):
        codigo = f'{self.nombre[1]}:\n'
        for p in self.parametros:
            codigo += f'\n    pop eax'
            codigo += f'\n    mov [{p.nombre[1]}], eax'
        codigo += '\n'.join(c.generarCodigo() for c in self.cuerpo)
        codigo += '\n    ret\n'
        return codigo


class NodoParametro(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo   = tipo
        self.nombre = nombre


class NodoAsignacion(NodoAST):

    def __init__(self, tipo, nombre, expresion):
        self.tipo      = tipo      
        self.nombre    = nombre      
        self.expresion = expresion

    def generarCodigo(self):
        codigo  = self.expresion.generarCodigo()
        codigo += f'\n    mov [{self.nombre[1]}], eax'
        return codigo


class NodoRetorno(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion

    def generarCodigo(self):
        return self.expresion.generarCodigo()


class NodoCondicional(NodoAST):
    """si (condicion) entonces ... finsi"""
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo    = cuerpo

    def generarCodigo(self):
    
        codigo  = self.condicion.generarCodigo()
        codigo += '\n    cmp eax, 0'
        codigo += '\n    je  .fin_si'
        for inst in self.cuerpo:
            codigo += '\n' + inst.generarCodigo()
        codigo += '\n.fin_si:'
        return codigo


class NodoEscribir(NodoAST):
    """escribir(expresion)"""
    def __init__(self, argumentos):
        self.argumentos = argumentos

    def generarCodigo(self):
        codigo = []
        for arg in self.argumentos:
            codigo.append(arg.generarCodigo())
            codigo.append("    push eax")
            codigo.append("    mov  eax, 4")
            codigo.append("    mov  ebx, 1")
            codigo.append("    int  0x80")
            codigo.append("    pop  eax")
        return '\n'.join(codigo)


# ── Nodos de expresiones ───────────────────────────────────
class NodoLlamadaFuncion(NodoAST):
    def __init__(self, nombref, argumentos):
        self.nombre_funcion = nombref
        self.argumentos     = argumentos

    def generarCodigo(self):
        codigo = []
        for arg in reversed(self.argumentos):
            codigo.append(arg.generarCodigo())
            codigo.append("    push eax")
        codigo.append(f"    call {self.nombre_funcion}")
        codigo.append(f"    add  esp, {len(self.argumentos) * 4}")
        return '\n'.join(codigo)


class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador  = operador   
        self.derecha   = derecha

    def generarCodigo(self):
        codigo = [self.izquierda.generarCodigo(), '    push eax',
                  self.derecha.generarCodigo(),   '    mov  ebx, eax',
                  '    pop  eax']
        op = self.operador[1]
        if   op == '+': codigo.append('    add eax, ebx')
        elif op == '-': codigo.append('    sub eax, ebx')
        elif op == '*': codigo.append('    imul ebx')
        elif op == '/': codigo.extend(['    cdq', '    idiv ebx'])
        elif op == '>':
            codigo.extend(['    cmp  eax, ebx',
                           '    setg al',
                           '    movzx eax, al'])
        return '\n'.join(codigo)

    def optimizar(self):
        izq = self.izquierda.optimizar() if isinstance(self.izquierda, NodoOperacion) else self.izquierda
        der = self.derecha.optimizar()   if isinstance(self.derecha,   NodoOperacion) else self.derecha
        if isinstance(izq, NodoNumero) and isinstance(der, NodoNumero):
            a, b = int(izq.valor[1]), int(der.valor[1])
            op = self.operador[1]
            resultado = (a+b if op=='+' else a-b if op=='-'
                         else a*b if op=='*' else a//b)
            return NodoNumero(('NUMBER', str(resultado)))
        # Eliminacion de neutros
        if self.operador[1] == '*':
            if isinstance(der, NodoNumero) and der.valor[1] == '1': return izq
            if isinstance(izq, NodoNumero) and izq.valor[1] == '1': return der
        if self.operador[1] == '+':
            if isinstance(der, NodoNumero) and der.valor[1] == '0': return izq
            if isinstance(izq, NodoNumero) and izq.valor[1] == '0': return der
        return NodoOperacion(izq, self.operador, der)


class NodoIdentificador(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre  

    def generarCodigo(self):
        return f'\n    mov eax, [{self.nombre[1]}]'


class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor   

    def generarCodigo(self):
        return f'\n    mov eax, {self.valor[1]}'


class NodoCadena(NodoAST):
    def __init__(self, valor):
        self.valor = valor


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        t = self.obtener_token_actual()
        if t and t[0] == tipo_esperado:
            self.pos += 1
            return t
        raise SyntaxError(f'Error sintactico: se esperaba {tipo_esperado}, pero se encontro: {t}')

    def parsear(self):

        funciones = []
        while (self.obtener_token_actual() and
               self.obtener_token_actual()[1] == 'funcion'):
            funciones.append(self.funcion_def())
        main = self.bloque_principal()
        return NodoPrograma(funciones, main)

    def funcion_def(self):
        tipo_ret = self.coincidir('KEYWORD')   
        nombre   = self.coincidir('IDENTIFIER')       
        self.coincidir('DELIMITER')              
        params   = self.parametros()
        self.coincidir('DELIMITER')                 
        cuerpo   = self.cuerpo(['finfuncion'])
        self.coincidir('KEYWORD')                  
        return NodoFuncion(tipo_ret, nombre, params, cuerpo)


    def bloque_principal(self):
        inicio = self.coincidir('KEYWORD')      
        cuerpo = self.cuerpo(['fin'])
        self.coincidir('KEYWORD')                 
        nombre_fake = ('KEYWORD', 'main')
        return NodoFuncion(inicio, nombre_fake, [], cuerpo)

    def parametros(self):
        params = []
        if (self.obtener_token_actual() and
                self.obtener_token_actual()[1] != ')'):
            tipo   = ('KEYWORD', 'int')
            nombre = self.coincidir('IDENTIFIER')
            params.append(NodoParametro(tipo, nombre))
            while (self.obtener_token_actual() and
                   self.obtener_token_actual()[1] == ','):
                self.coincidir('DELIMITER')
                nombre = self.coincidir('IDENTIFIER')
                params.append(NodoParametro(tipo, nombre))
        return params

    def cuerpo(self, palabras_fin):
        instrucciones = []
        while (self.obtener_token_actual() and
               self.obtener_token_actual()[1] not in palabras_fin):
            tok = self.obtener_token_actual()[1]
            if   tok == 'si':       instrucciones.append(self.condicional())
            elif tok == 'escribir': instrucciones.append(self.sentencia_escribir())
            elif tok == 'retorna':  instrucciones.append(self.retorno())
            else:                    instrucciones.append(self.asignacion())
        return instrucciones

    def asignacion(self):
        nombre = self.coincidir('IDENTIFIER')
        self.coincidir('OPERATOR')   # =
        expr   = self.expresion()
        return NodoAsignacion(None, nombre, expr)

    def retorno(self):
        self.coincidir('KEYWORD')    # retorna
        return NodoRetorno(self.expresion())

    def condicional(self):
        self.coincidir('KEYWORD')    # si
        self.coincidir('DELIMITER')  # (
        cond = self.expresion()
        self.coincidir('DELIMITER')  # )
        self.coincidir('KEYWORD')    # entonces
        cuerpo = self.cuerpo(['finsi'])
        self.coincidir('KEYWORD')    # finsi
        return NodoCondicional(cond, cuerpo)

    def sentencia_escribir(self):
        self.coincidir('KEYWORD')    # escribir
        self.coincidir('DELIMITER')  # (
        args = []
        if self.obtener_token_actual() and self.obtener_token_actual()[1] != ')':
            args = self.argumentos()
        self.coincidir('DELIMITER')  # )
        return NodoEscribir(args)

    def expresion(self):
        izq = self.termino()
        while (self.obtener_token_actual() and
               self.obtener_token_actual()[0] == 'OPERATOR'):
            op  = self.coincidir('OPERATOR')
            der = self.termino()
            izq = NodoOperacion(izq, op, der)
        return izq

    def termino(self):
        tok = self.obtener_token_actual()
        if tok[0] == 'NUMBER':
            return NodoNumero(self.coincidir('NUMBER'))
        elif tok[0] == 'IDENTIFIER':
            ident = self.coincidir('IDENTIFIER')
            if (self.obtener_token_actual() and
                    self.obtener_token_actual()[1] == '('):
                self.coincidir('DELIMITER')
                args = self.argumentos() if self.obtener_token_actual()[1] != ')' else []
                self.coincidir('DELIMITER')
                return NodoLlamadaFuncion(ident[1], args)
            return NodoIdentificador(ident)
        elif tok[0] == 'STRING':
            return NodoCadena(self.coincidir('STRING'))
        raise SyntaxError(f'Expresion invalida: {tok}')

    def argumentos(self):
        args = [self.expresion()]
        while (self.obtener_token_actual() and
               self.obtener_token_actual()[1] == ','):
            self.coincidir('DELIMITER')
            args.append(self.expresion())
        return args