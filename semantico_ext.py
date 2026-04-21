from sintactico_ast_ext import *
# ----------------------------------------- Tabla de simbolos ------------------------------------
class TablaSimbolos:
    def __init__(self):
        self.variables = {}  # Almacenar varibles {nombre:tipo}
        self.funciones = {}  # Almacena funciones {nombre: (tipo_ret, [parametros])}

    def declaracion_variable(self, nombre, tipo):
        if nombre in self.variables:
            raise Exception(f"Error: Variable '{nombre}' ya declarada")
        self.variables[nombre] = tipo

    def obtener_tipo_variable(self, nombre):
        if nombre not in self.variables:
            raise Exception(f"Error: Variable '{nombre}' no identificada")
        return self.variables[nombre]
    
    def declarar_funcion(self, nombre, tipo_retorno, parametros):
        if nombre in self.funciones:
            raise Exception(f"Error: Funcion '{nombre} ' ya definida")
        self.funciones[nombre] = (tipo_retorno, parametros)

    def obtener_info_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: Funcion '{nombre}' no definida")
        return self.funciones[nombre]

# -------------------------------------- Analizador semantico -----------------------------------
class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos= TablaSimbolos()

    def analizar(self, nodo):

        if isinstance(nodo, NodoPrograma):
            for funcion in nodo.funciones:
                self.analizar(funcion)
            self.analizar(nodo.main)

        elif isinstance(nodo, NodoFuncion):
            parametros = []
            for parametro in nodo.parametros:
                parametros.append((parametro.nombre[1], parametro.tipo[1]))
                self.tabla_simbolos.declaracion_variable(parametro.nombre[1], parametro.tipo[1])

            self.tabla_simbolos.declarar_funcion(nodo.nombre[1], nodo.tipo_retorno[1], parametros)
            for instruccion in nodo.cuerpo:
                if isinstance(instruccion, NodoRetorno):
                    tipo_retorno = self.analizar(instruccion.expresion)
                    if tipo_retorno != nodo.tipo_retorno[1]:
                        raise Exception(f"Error: de tipo devuelto")
                self.analizar(instruccion)

        elif isinstance(nodo, NodoAsignacion):
            tipo_expr = self.analizar(nodo.expresion)
            if tipo_expr != nodo.tipo[1]:
                raise Exception(f"Error: no coincidn los tipos {nodo.tipo[1]} != {tipo_expr}")
            self.tabla_simbolos.declaracion_variable(nodo.nombre[1], nodo.tipo[1])

        elif isinstance(nodo, NodoOperacion):
            tipo_izq = self.analizar(nodo.izquierda)
            tipo_der = self.analizar(nodo.derecha)
            if tipo_izq != tipo_der:
                raise Exception(f"Error: tipos incompatibles en la expresion {tipo_izq} {nodo.operador} {tipo_der}")
            return tipo_izq

        elif isinstance(nodo, NodoIdentificador):
            return self.tabla_simbolos.obtener_tipo_variable(nodo.nombre[1]) 

        elif isinstance(nodo, NodoNumero):
            return 'int' if '.' not in nodo.valor[1] else 'float'
        
        elif isinstance(nodo, NodoLlamadaFuncion):
            tipo, parametros = self.tabla_simbolos.obtener_info_funcion(nodo.nombre_funcion)
            if len(parametros) != len(nodo.argumentos):
                raise Exception(f"Error: La funcion {nodo.nombre_funcion} espera {len(parametros)} argumentos, pero recibio {len(nodo.argumentos)}")
            i = 0
            for argumento in nodo.argumentos:
                print(parametros[i][1])
                if self.analizar(argumento) != parametros[i][1]:
                    raise Exception(f"Error: No coinciden los tipos")
                i += 1
            return tipo
        
        elif isinstance(nodo, NodoRetorno):
            tipo_retorno = self.analizar(nodo.expresion)
            return tipo_retorno
        
        
            
            

    
        
        
        
        