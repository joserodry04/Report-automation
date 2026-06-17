import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet

#configuracion ruta absoluta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def obtener_ruta (nombre_archivo):
    #une la carpeta del script con cualquier nombre de archivo
    return os.path.join(BASE_DIR, nombre_archivo)

def obtener_archivos(ruta_carpeta):
    try:
        archivos = []
        for archivo in os.listdir(ruta_carpeta):#lista archivos de una carpeta
            if archivo.endswith('.csv'):#filtra solo .csv
                archivos.append(os.path.join(ruta_carpeta, archivo))
        return archivos
    except FileNotFoundError:
        log(f"ERROR: Archivo no encontrado en {ruta_carpeta}")
        return [] #con esto siempre devolvera lista

def cargar_multiples_csv(lista_archivos):
    dataframes = []
    for archivo in lista_archivos:
        try:
            df = pd.read_csv(archivo)
            dataframes.append(df)
        except Exception as e:
            log(f"ERROR al leer {archivo}: {str(e)}")
    if not dataframes:
        raise ValueError("No se pudo cargar ningún CSV válido")
    return pd.concat(dataframes, ignore_index=True)#pd.concat une multiples tablas

def revisar_datos(df):
    print(df.info())
    print(df.describe())
    print(df.isnull().sum())
    return df 


def limpiar_datos(df):
    df = df.drop_duplicates()
    columnas_necesarias = ['precio', 'cantidad', 'fecha', 'pais', 'cliente', 'producto']
    faltantes = [col for col in columnas_necesarias if col not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes: {faltantes}")
    df['fecha'] = pd.to_datetime(df['fecha'], errors="coerce")
    df = df.dropna(subset=['fecha'])
    df['ingresos'] = df['precio'] * df['cantidad']
    return df

def ingresos_totales(df):
    return df['ingresos'].sum()

def ingresos_producto (df):
    return df.groupby('producto')['ingresos'].sum().sort_values(ascending=False).reset_index()

def grafica_producto(df_plot):
    plt.figure(figsize=(10, 6))
    #creacion de grafico con seaborn
    ax = sns.barplot(data=df_plot, x='producto', y='ingresos', hue='producto', palette="viridis", legend=False)
    for container in ax.containers:#agrega etiquetas (valores)
        ax.bar_label(container, fmt='$%.0f', padding=3)
    plt.title("Ingresos por Producto", fontsize=14)
    plt.ylabel("Ingresos")
    plt.savefig(obtener_ruta("grafica_producto.png"))
    plt.close()

def ingresos_pais(df):
    return df.groupby('pais')['ingresos'].sum().sort_values(ascending=False).reset_index()
def grafica_pais(df_plot):
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_plot, x="pais", y="ingresos", hue="pais", palette="viridis", legend=False)
    for container in ax.containers:
        ax.bar_label(container, fmt='$%.0f', padding=3)
    plt.title("Ingresos por País", fontsize=14)
    plt.ylabel("Ingresos")
    #Guradamos con ruta absoluta
    plt.savefig(obtener_ruta("grafica_pais.png"))
    plt.close()

def top_clientes(df):
    return df.groupby('cliente')['ingresos'].sum().sort_values(ascending=False).head().reset_index()

def grafica_cliente(df_plot):
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_plot, x='cliente', y='ingresos', hue='cliente', palette="magma", legend=False)
    for container in ax.containers:
        ax.bar_label(container, fmt='$%.0f', padding=5)

    plt.title("Top 5 Clientes con Mayore Ingresos", fontsize=14)
    plt.ylabel("Ingresos")
    plt.savefig(obtener_ruta("grafica_cliente.png"))
    plt.close()

def ventas_dia(df):
    orden = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    return df.groupby(df['fecha'].dt.day_name())['ingresos'].sum().reindex(orden).fillna(0)

def grafica_dia(serie):
    df_plot = serie.reset_index()
    df_plot.columns = ['dia', 'ingresos']
    plt.figure(figsize=(10,6))
    sns.set_theme(style="ticks")
    ax = sns.lineplot(data=df_plot, x='dia', y='ingresos', marker="o", linewidth=2.5, color="teal")
    #relleno en la parte de abajo
    plt.fill_between(df_plot['dia'], df_plot['ingresos'], alpha=0.1, color="teal")
    for i, valor in enumerate(df_plot['ingresos']):
        ax.text(i, valor + (valor*0.03), f'${valor:,.0f}', ha='center', fontsize=9)

    plt.title("Tendencia de Ingresos por Día de la Semana", fontsize=14)
    plt.ylabel("Ingresos Totales")
    plt.xlabel("Día")
    plt.savefig(obtener_ruta("grafica_temporal.png"))
    plt.close()

def generar_reporte(df_productos, df_pais, df_clientes, serie_temporal):
    with open(obtener_ruta("reporte.txt"), "w", encoding="utf-8") as f:
        #calculos
        ingreso_tot = df_pais["ingresos"].sum()
        mejor_pais = df_pais.loc[df_pais['ingresos'].idxmax(), 'pais']
        val_pais = df_pais.iloc[0]['ingresos']
        mejor_cliente = df_clientes.iloc[0]['cliente']
        val_cliente = df_clientes.iloc[0]['ingresos']
        porcentaje_total = (val_cliente / ingreso_tot) * 100
        mejor_prod = df_productos.iloc[0]['producto']
        val_prod = df_productos.iloc[0]['ingresos']
        porcentaje_prod = (val_prod / ingreso_tot) * 100
        mejor_dia = serie_temporal.idxmax()
        val_dia = serie_temporal.max()

        f.write("       REPORTE EJECUTIVO GENERAL\n")
        f.write("===============================================\n\n")
        # SECCION 1: Ingresos total
        f.write("Ingresos Total Genera\n")
        f.write(f"${ingreso_tot:,.2f}\n")
        f.write("\n\n")
        # SECCIÓN 2: PRODUCTOS ESTRELLA
        f.write("3. TOP 3 PRODUCTOS MÁS VENDIDOS\n")
        f.write(df_productos.to_string(index=False) + "\n")
        f.write(f"El producto más retable: {mejor_prod} (${val_prod:,.2f})\n mostrando una fuerte dependencia en este producto\n\n")
        # SECCIÓN 3: DESEMPEÑO POR PAÍS
        f.write("1. ANÁLISIS GEOGRÁFICO\n")
        f.write(df_pais.to_string(index=False) + "\n")
        f.write(f"Se observó que existe una dependencia en: {mejor_pais} (${val_pais:,.2f}) siendo este nuestro\n lider del mercado\n\n")
        # SECCIÓN 4: TOP CLIENTES
        f.write("2. TOP 5 CLIENTES (VALOR)\n")
        f.write(df_clientes.to_string(index=False) + "\n\n")
        f.write(f"Nuestro mejor cliente: {mejor_cliente} (${val_cliente:,.2f}),")
        f.write(f"representando el {porcentaje_total:.1f}% de los ingresos totales\n\n")
        # SECCIÓN 5: TENDENCIA TEMPORAL
        f.write("4. RENDIMIENTO POR DÍA DE LA SEMANA\n")
        f.write(serie_temporal.to_string() + "\n\n")
        f.write(f"El mejor día en ventas fue: {mejor_dia} (${val_dia:,.2f})\n\n")

        f.write("INSIGHTS:\n")
        f.write("")
        f.write("===============================================\n")
        f.write(f"TOTAL GLOBAL DE INGRESOS: ${ingreso_tot:,.2f}\n")
        f.write("1. Existe una alta concentración de ingresos: proviene de un solo producto y de un único cliente, lo que representa un riesgo significativo para la estabilidad del negocio.\n")
        f.write("2. Un solo cliente es el 38.64% de los ingresos en clientes\n")
        f.write(f"3. Un solo producto es el {porcentaje_prod:.1f}% de los ingresos\n")
        f.write("4. semanalmente el mercado está balaceado, a excepcion de un dia crítico\n")
        f.write("5. fines de semana las ventas son nulas\n")
        f.write("===============================================\n")
        f.write("CONCLUSIÓN:\n\n")
        f.write("Gracias al análisis realizado, se obtivieron\n datos importantes para el negocio, por lo que se recomienda lo siguiente:\n")
        f.write("1. Diversificación en el mercado, mejorando su marketing\n")
        f.write("2. Tener en cuenta estrategias de upselling o bundling\n")
        f.write("3. Realizar ventas cruzadas para aumentar ventas en productos bajos\n")
        f.write("4. Realizar ofertas relampago los fines de semana")

def generar_pdf():
    doc = SimpleDocTemplate(obtener_ruta("reporte.pdf"))
    estilos = getSampleStyleSheet()
    estilo_texto = estilos["Normal"]

    contenido = []
    try:
        with open(obtener_ruta("reporte.txt"), "r", encoding="utf-8") as f:
            lineas = f.readlines()
        for linea in lineas:
            texto = linea.strip()#quita saltos de linea (\n)
            if texto == "": #si la linea esta vacia, se pone un espacio
                contenido.append(Paragraph("<br/>", estilo_texto))#salto de linea PDF
            else:
                estilo = estilos["Title"] if "REPORTE" in texto else estilo_texto
                contenido.append(Paragraph(texto, estilo))
        contenido.append(Paragraph("<br/><br/>", estilo_texto))

        #agregamos todas las gráficas
        for g in ["grafica_producto.png", "grafica_pais.png", "grafica_cliente.png", "grafica_temporal.png"]:
            ruta = obtener_ruta(g)
            if os.path.exists(ruta):
                contenido.append(Paragraph("<br/>", estilos["Normal"]))
                try:
                    contenido.append(Image(ruta, width=400, height=200))
                except Exception as e:
                    log(f"ERROR cargando imagen {ruta} {str(e)}")
            else:
                log(f"No se encontro {g}")
        
        doc.build(contenido)#construye el pdf
    except Exception as e:
        log(f"ERROR al generar PDF {str(e)}")

def log(mensaje):
    try:
        with open(obtener_ruta("log.txt"), "a") as f:
            import datetime
            ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ahora}] {mensaje}\n")
    except Exception:
        print("ERROR escribiendo log...")

def main():
    log("----Inicio del Proceso----")

    try:
        ruta_datos = obtener_ruta("datos")
        #creacion de carpeta si no existe
        if not os.path.exists(ruta_datos):
            os.makedirs(ruta_datos)
            log("Carpeta datos creada automaticamente")
        # 1. Buscar en /datos
        archivos = obtener_archivos(ruta_datos)
        # 2. Si no hay, buscar en raiz
        if not archivos:
            log("No se encontraron archivos en /datos, buscando en carpeta principal...")
            archivos = obtener_archivos(BASE_DIR)
        # 3. Si sigue vacio -> error real
        if not archivos:
            log("ERROR: No se encontraron archivos CSV en ninguna ubicacion")
            return
        df = cargar_multiples_csv(archivos)
        log("Datos cargados correctamente")

        df = revisar_datos(df)
        log("Revision de datos rapida, realizada")

        df = limpiar_datos(df)
        log("Datos limpios y cálculos realizados")

        res_productos = ingresos_producto(df)
        res_pais = ingresos_pais(df)
        res_clientes = top_clientes(df)
        res_temporal = ventas_dia(df)

        grafica_producto(res_productos)
        grafica_pais(res_pais)
        grafica_cliente(res_clientes)
        grafica_dia(res_temporal)

        generar_reporte(res_productos, res_pais, res_clientes, res_temporal)
        log("Reporte TXT generado correctamente")

        generar_pdf()
        log("Reporte PDF finalizado")
    
    except Exception as e:
        log(f"ERROR CRITICO: {str(e)}")
    
    log("----Script finalizado----")
if __name__ == "__main__":
    main()
