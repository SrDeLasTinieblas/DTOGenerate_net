import pyodbc

# Solicitar información de configuración
server = input("Nombre del servidor SQL: ")
database = input("Nombre de la base de datos: ")
username = input("Nombre de usuario: ")
password = input("Contraseña: ")
namespace = input("Namespace: ")

try:
    # Intentar establecer la conexión
    conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    cursor = conn.cursor()

    # Obtener el nombre de todas las tablas en la base de datos
    cursor.execute("SELECT name FROM sys.tables")
    tables = cursor.fetchall()

    # Generar clases C# basadas en las tablas
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
        columns = cursor.fetchall()

        #class_template = f"using System.ComponentModel.DataAnnotations;\n\nnamespace WebApiEmpresaXYZ.Models\n{{\n\tpublic class {table_name}\n\t{{\n"
        class_template = f"namespace {namespace}\n{{\n\tpublic class {table_name}\n\t{{\n"

        for column in columns:
            column_name, data_type = column
            if "char" in data_type:
                csharp_type = "string"
            elif "int" in data_type:
                csharp_type = "int"
            elif "bool" in data_type:
                csharp_type = "bool"
            elif "datetime" in data_type or "date" in data_type:
                csharp_type = "DateTime"
            elif "decimal" in data_type or "DECIMAL" in data_type:
                csharp_type = "decimal"
            else:
                csharp_type = "UNKNOWN_TYPE"

            class_template += f"\t\tpublic {csharp_type} {column_name} {{ get; set; }}\n"

        class_template += "\t}\n}"
        with open(f"{table_name}.cs", "w") as file:
            file.write(class_template)

    conn.close()

    print("Conectado a la base de datos. Clases generadas correctamente.")

except pyodbc.Error as e:
    print("No se pudo conectar a la base de datos:", e)
