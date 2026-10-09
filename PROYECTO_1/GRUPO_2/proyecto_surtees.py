"""
 TIENDA VIRTUAL 
 "SurTees"

"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as sp

# 
# bloque de MODELO MATEMÁTICO BASE
# 

def calcular_costo(q, cf, cv):
    return cf + (cv * q)

def calcular_ingreso(q, precio_base):
    factor_descuento = 8
    precio_final = precio_base - (factor_descuento * q)
    return precio_final * q

def calcular_utilidad(q, cf, cv, precio_base):
    return calcular_ingreso(q, precio_base) - calcular_costo(q, cf, cv)

def calcular_impuesto(utilidad_bruta):
    u = np.atleast_1d(utilidad_bruta)
    return np.where(u <= 300000, 0, (u - 300000) * 0.15)

def calcular_utilidad_neta(q, cf, cv, precio_base):
    ub = calcular_utilidad(q, cf, cv, precio_base)
    return ub - calcular_impuesto(ub)

def buscar_equilibrios(q_array, utilidades):
    puntos = []
    for i in range(len(utilidades)-1):
        if utilidades[i] < 0 and utilidades[i+1] >= 0:
            puntos.append(q_array[i+1])
    return puntos

def analisis_analitico_sympy(cf, cv, precio_base):
    q_simb = sp.Symbol('q')
    
    C_sym = cf + cv * q_simb
    R_sym = (precio_base - 8 * q_simb) * q_simb
    U_sym = R_sym - C_sym
    
    U_prima = sp.diff(U_sym, q_simb)
    U_doble_prima = sp.diff(U_prima, q_simb)
    C_prima = sp.diff(C_sym, q_simb)
    R_prima = sp.diff(R_sym, q_simb)
    
    puntos_criticos = sp.solve(U_prima, q_simb)
    q_optimo = float(puntos_criticos[0]) if puntos_criticos else 0
    
    concavidad = "Cóncava hacia abajo (Máximo)" if float(U_doble_prima) < 0 else "Cóncava hacia arriba"
    
    # Se usa Courier o consola para que los caracteres se alineen perfecto.
    return {
        "ecuacion_ingreso": sp.pretty(R_sym, use_unicode=True),
        "ecuacion_costo": sp.pretty(C_sym, use_unicode=True),
        "ecuacion_utilidad": sp.pretty(U_sym, use_unicode=True),
        "U_prima": sp.pretty(U_prima, use_unicode=True),
        "U_doble_prima": sp.pretty(U_doble_prima, use_unicode=True),
        "C_prima": sp.pretty(C_prima, use_unicode=True),
        "R_prima": sp.pretty(R_prima, use_unicode=True),
        "q_critico": q_optimo,
        "concavidad": concavidad
    }


# bloque de INTERFAZ GRÁFICA Y NAVEGACIÓN


class SurTeesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tablero de Rentabilidad - SurTees")
        self.root.geometry("900x750") # Un poco más grande para el informe
        
        self.var_cf = tk.DoubleVar(value=250000)
        self.var_cv = tk.DoubleVar(value=4500)
        self.var_pb = tk.DoubleVar(value=12000)
        self.var_cap = tk.DoubleVar(value=600)
        
        self.datos_actuales = {}
        
        self.contenedor = tk.Frame(self.root)
        self.contenedor.pack(fill="both", expand=True)
        
        self.pantalla_menu()

    def limpiar_pantalla(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    def pantalla_menu(self):
        self.limpiar_pantalla()
        
        tk.Label(self.contenedor, text="SurTees: Planificador de Inventario", font=("Arial", 16, "bold")).pack(pady=20)
        
        frame_form = tk.LabelFrame(self.contenedor, text="Parámetros de la Tienda", padx=20, pady=20)
        frame_form.pack(pady=10)
        
        tk.Label(frame_form, text="Costo Fijo (CRC):").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(frame_form, textvariable=self.var_cf).grid(row=0, column=1)
        
        tk.Label(frame_form, text="Costo Variable (CRC):").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(frame_form, textvariable=self.var_cv).grid(row=1, column=1)
        
        tk.Label(frame_form, text="Precio de Venta Base (CRC):").grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(frame_form, textvariable=self.var_pb).grid(row=2, column=1)
        
        tk.Label(frame_form, text="Capacidad Bodega:").grid(row=3, column=0, sticky="w", pady=5)
        tk.Entry(frame_form, textvariable=self.var_cap).grid(row=3, column=1)
        
        tk.Label(self.contenedor, text="Seleccione un Escenario:", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Button(self.contenedor, text="1. Escenario Base (Operación Normal)", bg="lightblue", width=40,
                  command=lambda: self.procesar_datos("Escenario Base", self.var_pb.get(), self.var_cv.get())).pack(pady=5)
        
        tk.Button(self.contenedor, text="2. Escenario Competencia (Precio baja a 9000)", bg="lightgreen", width=40,
                  command=lambda: self.procesar_datos("Escenario Competencia", 9000, self.var_cv.get())).pack(pady=5)
        
        tk.Button(self.contenedor, text="3. Escenario Proveedor Caro (Costo sube a 6000)", bg="lightcoral", width=40,
                  command=lambda: self.procesar_datos("Escenario Proveedor", self.var_pb.get(), 6000)).pack(pady=5)

    def procesar_datos(self, titulo, pb, cv):
        cf = self.var_cf.get()
        cap = self.var_cap.get()
        
        analisis_sympy = analisis_analitico_sympy(cf, cv, pb)
        
        q_array = np.linspace(0, cap, 200)
        ubruta = calcular_utilidad(q_array, cf, cv, pb)
        uneta = calcular_utilidad_neta(q_array, cf, cv, pb)
        costos = calcular_costo(q_array, cf, cv)
        ingresos = calcular_ingreso(q_array, pb)
        equilibrios = buscar_equilibrios(q_array, ubruta)
        
        idx_max = np.argmax(uneta)
        q_optimo_num = q_array[idx_max]
        util_max_num = uneta[idx_max]
        
        q_tabla = np.linspace(0, cap, 15)
        df_tabla = pd.DataFrame({
            'Unidades (q)': q_tabla,
            'Precio Unit.': pb - (8 * q_tabla),
            'Costo Total': calcular_costo(q_tabla, cf, cv),
            'Ingreso Total': calcular_ingreso(q_tabla, pb),
            'U. Bruta': calcular_utilidad(q_tabla, cf, cv, pb),
            'U. Neta': calcular_utilidad_neta(q_tabla, cf, cv, pb)
        }).astype(int)
        
        self.datos_actuales = {
            "titulo": titulo, "pb": pb, "cv": cv, "cf": cf, "cap": cap,
            "q_array": q_array, "costos": costos, "ingresos": ingresos,
            "ubruta": ubruta, "uneta": uneta, "equilibrios": equilibrios,
            "q_optimo": q_optimo_num, "util_max": util_max_num,
            "df_tabla": df_tabla, "sympy": analisis_sympy
        }
        
        self.pantalla_tabla()

    # TABLA TIPO EXCEL
    def pantalla_tabla(self):
        self.limpiar_pantalla()
        d = self.datos_actuales
        
        frame_nav = tk.Frame(self.contenedor)
        frame_nav.pack(fill="x", pady=10)
        tk.Button(frame_nav, text="Atrás", command=self.pantalla_menu).pack(side="left", padx=10)
        tk.Button(frame_nav, text="Siguiente", command=self.pantalla_grafica_equilibrio).pack(side="right", padx=10)
        
        tk.Label(self.contenedor, text=f"Proyección de Inventario: {d['titulo']}", font=("Arial", 14, "bold")).pack(pady=5)
        
        recomendacion_simple = f"Recomendación: Comprar {d['q_optimo']:.0f} camisetas."
        tk.Label(self.contenedor, text=recomendacion_simple, fg="darkblue", font=("Arial", 12)).pack(pady=5)
        
        frame_tabla = tk.Frame(self.contenedor)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)
        
        cols = list(d['df_tabla'].columns)
        tree = ttk.Treeview(frame_tabla, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110, anchor="center")
            
        for _, fila in d['df_tabla'].iterrows():
            tree.insert("", tk.END, values=list(fila))
            
        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

    # FUNCIÓN AUXILIAR PARA GRÁFICAS
    def dibujar_entorno_grafico(self, comando_atras, comando_siguiente, titulo_grafico):
        self.limpiar_pantalla()
        frame_nav = tk.Frame(self.contenedor)
        frame_nav.pack(fill="x", pady=10)
        tk.Button(frame_nav, text="Atrás", command=comando_atras).pack(side="left", padx=10)
        tk.Button(frame_nav, text="Siguiente", command=comando_siguiente).pack(side="right", padx=10)
        
        tk.Label(self.contenedor, text=titulo_grafico, font=("Arial", 14, "bold")).pack()
        
        frame_graf = tk.Frame(self.contenedor)
        frame_graf.pack(fill="both", expand=True, padx=20, pady=10)
        return frame_graf

# GRÁFICA EQUILIBRIO
    def pantalla_grafica_equilibrio(self):
        """
        Genera la Gráfica 1: Punto de Equilibrio.
    
        """
        d = self.datos_actuales
        frame = self.dibujar_entorno_grafico(self.pantalla_tabla, self.pantalla_grafica_utilidades, "Gráfica 1: Punto de Equilibrio")
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(d['q_array'], d['costos'], label="Costo Total", color="red")
        ax.plot(d['q_array'], d['ingresos'], label="Ingreso Total", color="blue")
        
        ax.set_xlabel("Cantidad de Camisetas (q)")
        ax.set_ylabel("Monto en Colones (CRC)") 
        ax.yaxis.set_major_formatter('{x:,.0f}') 
        
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # GRÁFICA UTILIDADES
    def pantalla_grafica_utilidades(self):
        """
       Maximización de Utilidades.
     
        """
        d = self.datos_actuales
        frame = self.dibujar_entorno_grafico(self.pantalla_grafica_equilibrio, self.pantalla_grafica_marginal, "Gráfica 2: Maximización de Utilidades")
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(d['q_array'], d['ubruta'], label="Utilidad Bruta", color="orange")
        ax.plot(d['q_array'], d['uneta'], label="Utilidad Neta", color="green", linewidth=2.5)
        ax.axvline(x=d['q_optimo'], color='purple', linestyle=':', label="Punto Óptimo")
        
        ax.set_xlabel("Cantidad de Camisetas (q)")
        ax.set_ylabel("Monto en Colones (CRC)") 
        ax.yaxis.set_major_formatter('{x:,.0f}') 
        
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # GRÁFICA MARGINAL
    def pantalla_grafica_marginal(self):
        """
       Análisis Marginal.
        Muestra la intersección R'(q) = C'(q).

        """
        d = self.datos_actuales
        frame = self.dibujar_entorno_grafico(self.pantalla_grafica_utilidades, self.pantalla_informe_final, "Gráfica 3: Análisis Marginal")
        
        fig, ax = plt.subplots(figsize=(6, 4))
        q_sym = sp.Symbol('q')
        
        # Debemos parsear de nuevo para graficar, ya que convertimos a str para el informe
        C_prima_func = sp.lambdify(q_sym, sp.sympify(d['cf'] + d['cv'] * q_sym).diff(q_sym), 'numpy')
        R_prima_func = sp.lambdify(q_sym, sp.sympify((d['pb'] - 8 * q_sym) * q_sym).diff(q_sym), 'numpy')
        
        cm_val = C_prima_func(0)
        cm_array = np.full_like(d['q_array'], cm_val) if isinstance(cm_val, (int, float)) else C_prima_func(d['q_array'])
        rm_array = R_prima_func(d['q_array'])
        
        ax.plot(d['q_array'], cm_array, label="Costo Marginal", color="darkred")
        ax.plot(d['q_array'], rm_array, label="Ingreso Marginal", color="darkblue")
        ax.axvline(x=d['q_optimo'], color='purple', linestyle=':', label="Cruce Óptimo")
        
        ax.set_xlabel("Cantidad de Camisetas (q)")
        ax.set_ylabel("Colones por unidad extra") 
        ax.yaxis.set_major_formatter('{x:,.0f}') 
        ax.set_title("Punto donde el Ingreso Extra iguala al Costo Extra")
        
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    #  INFORME FINAL 
    def pantalla_informe_final(self):
        self.limpiar_pantalla()
        d = self.datos_actuales
        sy = d['sympy']
        
        frame_nav = tk.Frame(self.contenedor)
        frame_nav.pack(fill="x", pady=10)
        tk.Button(frame_nav, text="Atrás", command=self.pantalla_grafica_marginal).pack(side="left", padx=10)
        tk.Button(frame_nav, text="Finalizar (Ir al Menú)", command=self.pantalla_menu, bg="lightgray").pack(side="right", padx=10)
        
        tk.Label(self.contenedor, text="Informe Analítico de Rentabilidad", font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=5)
        
        # Text widget con configuración estética (márgenes, interlineado, fondo)
        texto = tk.Text(self.contenedor, wrap="word", bg="#f8f9fa", relief="flat",
                        padx=30, pady=20, spacing1=8, spacing2=4, spacing3=8)
        texto.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configuramos los "estilos" del texto
        texto.tag_configure("titulo", font=("Arial", 12, "bold"), foreground="#2980b9")
        texto.tag_configure("normal", font=("Helvetica", 11), foreground="#333333")
        texto.tag_configure("destacado", font=("Helvetica", 11, "bold"), foreground="#27ae60")
        texto.tag_configure("formula", font=("Consolas", 12, "bold"), foreground="#c0392b", justify="center")
        texto.tag_configure("nota", font=("Helvetica", 10, "italic"), foreground="#7f8c8d")

        eq_punto = f"{d['equilibrios'][0]:.0f}" if d['equilibrios'] else "No se alcanza"

        # 1. Recomendación
        texto.insert(tk.END, "Recomendación Estratégica\n", "titulo")
        texto.insert(tk.END, "Para maximizar las ganancias reales del próximo periodo, la tienda debe comprar exactamente ", "normal")
        texto.insert(tk.END, f"{d['q_optimo']:.0f} camisetas.\n", "destacado")
        texto.insert(tk.END, f"Se espera generar una Utilidad Neta máxima de ₡{d['util_max']:,.2f}. ", "normal")
        texto.insert(tk.END, f"El punto de equilibrio se logra al vender {eq_punto} unidades.\n\n", "nota")

        # 2. Costos e Ingresos
        texto.insert(tk.END, " Análisis de Costos e Ingresos\n", "titulo")
        texto.insert(tk.END, "El costo total C(q) crece según el costo fijo y variable. La ecuación modelada es:\n", "normal")
        texto.insert(tk.END, f"{sy['ecuacion_costo']}\n", "formula")
        texto.insert(tk.END, "El ingreso total R(q) contempla una disminución estratégica del precio por volumen de compra:\n", "normal")
        texto.insert(tk.END, f"{sy['ecuacion_ingreso']}\n\n", "formula")

        # 3. Utilidad
        texto.insert(tk.END, "Función de Utilidad Bruta\n", "titulo")
        texto.insert(tk.END, "Se obtiene restando los costos a los ingresos ( U(q) = R(q) - C(q) ):\n", "normal")
        texto.insert(tk.END, f"{sy['ecuacion_utilidad']}\n\n", "formula")

        # 4. Análisis Marginal (Cálculo Diferencial)
        texto.insert(tk.END, "Análisis Marginal y Optimización\n", "titulo")
        texto.insert(tk.END, "Para encontrar el punto óptimo, calculamos la derivada (Utilidad Marginal):\n", "normal")
        texto.insert(tk.END, f"U'(q) = {sy['U_prima']}\n", "formula")
        texto.insert(tk.END, "Al igualar esta derivada a cero, encontramos el Punto Crítico exacto:\n", "normal")
        texto.insert(tk.END, f"q = {sy['q_critico']:.2f} unidades\n", "formula")
        
        texto.insert(tk.END, "Para confirmar que es un máximo absoluto, calculamos la segunda derivada:\n", "normal")
        texto.insert(tk.END, f"U''(q) = {sy['U_doble_prima']}\n", "formula")
        texto.insert(tk.END, f"Al ser un valor negativo, se comprueba que la curva es {sy['concavidad']}, garantizando que esta cantidad representa el tope máximo de rentabilidad antes de que los costos marginales superen a los ingresos marginales.", "normal")


        texto.config(state=tk.DISABLED)


if __name__ == "__main__":
    ventana_principal = tk.Tk()
    app = SurTeesApp(ventana_principal)
    ventana_principal.mainloop()