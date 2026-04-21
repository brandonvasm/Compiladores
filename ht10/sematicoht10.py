
from sintacticoht10 import *

class TablaSimbolos:
    def __init__(self):
        self.variables = {}   # {nombre: tipo}
        self.funciones  = {}   
        self.vars_en_si = set()  # variables declaradas solo dentro de si

    def declaracion_variable(self, nombre, tipo):
        self.variables[nombre] = tipo

    def obtener_tipo_variable(self, nombre):
        if nombre not in self.variables:
            raise Exception(f"Error: Variable '{nombre}' no identificada")
        return self.variables[nombre]

    def declarar_funcion(self, nombre, tipo_retorno, parametros):
        if nombre in self.funciones:
            raise Exception(f"Error: Funcion '{nombre}' ya definida")
        self.funciones[nombre] = (tipo_retorno, parametros)

    def obtener_info_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: Funcion '{nombre}' no definida")
        return self.funciones[nombre]

    def marcar_condicional(self, nombre):
        self.vars_en_si.add(nombre)

    def advertir_condicional(self, nombre):
        if nombre in self.vars_en_si:
            print(f"Advertencia: '{nombre}' puede no estar inicializada")


# ── Analizador semantico ───────────────────────────────────
class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()

    def analizar(self, nodo):

        if isinstance(nodo, NodoPrograma):
    
            for fn in nodo.funciones:
                params = [(p.nombre[1], 'int') for p in fn.parametros]
                self.tabla_simbolos.declarar_funcion(fn.nombre[1], 'int', params)
           
            for fn in nodo.funciones:
                self.analizar(fn)
            
            self.analizar(nodo.main)

        elif isinstance(nodo, NodoFuncion):
          
            for param in nodo.parametros:
                self.tabla_simbolos.declaracion_variable(param.nombre[1], 'int')
            for inst in nodo.cuerpo:
                self.analizar(inst)

        elif isinstance(nodo, NodoAsignacion):
            tipo_expr = self.analizar(nodo.expresion)
            self.tabla_simbolos.declaracion_variable(nodo.nombre[1], tipo_expr)

        elif isinstance(nodo, NodoCondicional):
            self.analizar(nodo.condicion)
            # Capturar variables existentes antes del bloque si
            vars_antes = set(self.tabla_simbolos.variables.keys())
            for inst in nodo.cuerpo:
                self.analizar(inst)
            # Variables nuevas dentro del si
            vars_despues = set(self.tabla_simbolos.variables.keys())
            for nueva in vars_despues - vars_antes:
                self.tabla_simbolos.marcar_condicional(nueva)

        elif isinstance(nodo, NodoEscribir):
            for arg in nodo.argumentos:
                if isinstance(arg, NodoIdentificador):
                    self.tabla_simbolos.advertir_condicional(arg.nombre[1])
                self.analizar(arg)

        elif isinstance(nodo, NodoOperacion):
            tipo_izq = self.analizar(nodo.izquierda)
            tipo_der = self.analizar(nodo.derecha)
            if tipo_izq and tipo_der and tipo_izq != tipo_der:
                raise Exception(
                    f"Error semantico: tipos incompatibles ({tipo_izq} {nodo.operador[1]} {tipo_der})")
            return tipo_izq

        elif isinstance(nodo, NodoLlamadaFuncion):
            tipo_ret, params = self.tabla_simbolos.obtener_info_funcion(nodo.nombre_funcion)
            if len(params) != len(nodo.argumentos):
                raise Exception(
                    f"Error: '{nodo.nombre_funcion}' espera {len(params)} args, "
                    f"recibio {len(nodo.argumentos)}")
            for arg in nodo.argumentos:
                self.analizar(arg)
            return tipo_ret

        elif isinstance(nodo, NodoRetorno):
            return self.analizar(nodo.expresion)

        elif isinstance(nodo, NodoIdentificador):
            return self.tabla_simbolos.obtener_tipo_variable(nodo.nombre[1])

        elif isinstance(nodo, NodoNumero):
            return 'float' if '.' in nodo.valor[1] else 'int'
            

    
        
        
        