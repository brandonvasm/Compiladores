from sintactico_ast_ext import *
 
 
class TablaSimbolos:
    def __init__(self):
        self.ambitos = [{}]
        self.funciones = {}
        self.historial_ambitos = []
 
    def entrar_ambito(self):
        self.ambitos.append({})
 
    def salir_ambito(self):
        if len(self.ambitos) > 1:
            self.historial_ambitos.append(self.ambitos.pop())
        else:
            raise Exception('No se puede salir del ambito global')
 
    def declaracion_variable(self, nombre, tipo):
        ambito_actual = self.ambitos[-1]
        if nombre in ambito_actual:
            raise Exception(f"Error: Variable '{nombre}' ya declarada en este ambito")
        ambito_actual[nombre] = tipo
 
    def obtener_tipo_variable(self, nombre):
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]
        raise Exception(f"Error: Variable '{nombre}' no identificada")
 
    def declarar_funcion(self, nombre, tipo_retorno, parametros):
        if nombre in self.funciones:
            raise Exception(f"Error: Funcion '{nombre}' ya definida")
        self.funciones[nombre] = (tipo_retorno, parametros)
 
    def obtener_info_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: Funcion '{nombre}' no definida")
        return self.funciones[nombre]
 
    def imprimir_resumen_final(self, errores):
 
        print("\nAmbito global actual (self.ambitos[0]):")
        for nombre, tipo in self.ambitos[0].items():
            print(f"   {nombre!r:15} -> {tipo}")
 
        print(f"\nHistorial de ambitos cerrados ({len(self.historial_ambitos)} registrados):")
        for i, ambito in enumerate(self.historial_ambitos):
            print(f"   Ambito historico [{i}]: {ambito}")
 
        print(f"\nFunciones registradas:")
        for nombre, (ret, params) in self.funciones.items():
            print(f"   {nombre}() -> retorno: {ret!r}, parametros: {params}")
 
        print(f"\nErrores semanticos detectados ({len(errores)}):")
        if errores:
            for i, err in enumerate(errores, 1):
                print(f"   Error {i}: {err}")
        else:
            print("   Ninguno.")
 
 
 
# --------------- Sistema de Tipos ----------------
class SistemaTipos:
    @staticmethod
    def es_compatible(t1, t2):
        return t1 == t2 or (t1 == 'int' and t2 == 'float') or (t1 == 'float' and t2 == 'int')
 
    @staticmethod
    def tipo_resultante(t1, t2, operador):
        if t1 == 'float' or t2 == 'float':
            return 'float'
        return 'int'
 
 
# --------------- Analizador Semantico ----------------
class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
        self.errores = []
 
    def analizar(self, nodo):
 
        if isinstance(nodo, NodoPrograma):
            for funcion in nodo.funciones:
                self.analizar(funcion)
            self.analizar(nodo.main)
 
        elif isinstance(nodo, NodoFuncion):
            parametros_info = [(p.nombre[1], p.tipo[1]) for p in nodo.parametros]
            self.tabla_simbolos.declarar_funcion(nodo.nombre[1], nodo.tipo_retorno[1], parametros_info)
            self.tabla_simbolos.entrar_ambito()
            for p_nombre, p_tipo in parametros_info:
                self.tabla_simbolos.declaracion_variable(p_nombre, p_tipo)
            for instruccion in nodo.cuerpo:
                if isinstance(instruccion, NodoRetorno):
                    tipo_retorno = self.analizar(instruccion.expresion)
                    if tipo_retorno != nodo.tipo_retorno[1]:
                        raise Exception(f"Error: de tipo devuelto")
                else:
                    self.analizar(instruccion)
            self.tabla_simbolos.salir_ambito()
 
        elif isinstance(nodo, NodoAsignacion):
            tipo_expr = self.analizar(nodo.expresion)
            if tipo_expr != nodo.tipo[1]:
                raise Exception(f"Error: no coinciden los tipos {nodo.tipo[1]} != {tipo_expr}")
            self.tabla_simbolos.declaracion_variable(nodo.nombre[1], nodo.tipo[1])
 
        elif isinstance(nodo, NodoOperacion):
            tipo_izq = self.analizar(nodo.izquierda)
            tipo_der = self.analizar(nodo.derecha)
            if not SistemaTipos.es_compatible(tipo_izq, tipo_der):
                raise Exception(f"Error: tipos incompatibles {tipo_izq} {nodo.operador} {tipo_der}")
            return SistemaTipos.tipo_resultante(tipo_izq, tipo_der, nodo.operador[1])
 
        elif isinstance(nodo, NodoIdentificador):
            return self.tabla_simbolos.obtener_tipo_variable(nodo.nombre[1])
 
        elif isinstance(nodo, NodoNumero):
            return 'int' if '.' not in nodo.valor[1] else 'float'
 
        elif isinstance(nodo, NodoLlamadaFuncion):
            tipo, parametros = self.tabla_simbolos.obtener_info_funcion(nodo.nombre_funcion)
            if len(parametros) != len(nodo.argumentos):
                raise Exception(f"Error: La funcion {nodo.nombre_funcion} espera {len(parametros)} argumentos, pero recibio {len(nodo.argumentos)}")
            for i, argumento in enumerate(nodo.argumentos):
                arg_tipo = self.analizar(argumento)
                param_tipo = parametros[i][1]
                if not SistemaTipos.es_compatible(arg_tipo, param_tipo):
                    raise Exception(f"Error: No coinciden los tipos")
            return tipo
 
        elif isinstance(nodo, NodoRetorno):
            return self.analizar(nodo.expresion)
 
 
# --------------- Simulacion del Laberinto de Ambitos ----------------
def simular_laberinto():
    ts = TablaSimbolos()
    errores = []
 
    # Ambito global: int x = 10
    ts.declaracion_variable('x', 'int')
    print("\n[Global] Declarado: x -> int")
    print(f"  self.ambitos = {ts.ambitos}")
 
    ts.declarar_funcion('test', 'void', [('a', 'int')])
    ts.entrar_ambito()
    ts.declaracion_variable('a', 'int')
    print("\n[Funcion test()] Entro ambito, declarado: a -> int")
 
    ts.declaracion_variable('y', 'int')
    print("\nMOMENTO A ")
    print(f"  self.ambitos = {ts.ambitos}")
 
    ts.entrar_ambito()
    ts.declaracion_variable('x', 'float')
    print("\n[Bloque {}] Entro ambito, declarado: x -> float  (shadowing!)")
 
    tipo_y = ts.obtener_tipo_variable('y')
    tipo_x = ts.obtener_tipo_variable('x')
    print(f"\n  En 'y = y + x': tipo('y')={tipo_y}, tipo('x')={tipo_x}")
    print(f"  obtener_tipo_variable busca en reversed -> encuentra x:float primero")
 
    if tipo_y != tipo_x:
        err = f"Tipos incompatibles en asignacion: 'y' es '{tipo_y}' pero (y+x) produce '{tipo_x}'"
        errores.append(err)
        print(f"  Error 1: {err}")
 
    print("\nMOMENTO B")
    print(f"  self.ambitos = {ts.ambitos}")
 
    ts.salir_ambito()
    print("\n[Bloque {}] Salio -> guardado en historial_ambitos")
 
    err2 = "Reasignacion de 'x' sin tipo declarado: NodoAsignacion requiere tipo explicito"
    errores.append(err2)
    print(f"\n  En 'x = y + 1': Error 2: {err2}")
 
    try:
        ts.obtener_tipo_variable('z')
    except Exception as e:
        errores.append(str(e))
        print(f"\n  En 'escribir(z)': Error 3: {e}")
 
    print("\nMOMENTO C")
    print(f"  self.ambitos = {ts.ambitos}")
 
    ts.salir_ambito()
    print("\n[Funcion test()] Salio -> guardado en historial_ambitos")
 
    ts.imprimir_resumen_final(errores)
 
    return ts, errores