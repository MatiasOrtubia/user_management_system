from flask import Flask # Para usar flask
from flask import render_template # Para redireccionar una u otra URL
from flask import request # Para tomar datos de formularios etc.
from flask import redirect # Para redirigir a la misma pagina (o a otra? no se)
from flaskext.mysql import MySQL # Para que Flask pueda conectarse con sql
from datetime import datetime # Para tomar la fecha y hora de la computadora, la usamos para cambiar el nombre de archivo de la imagen
import os

app = Flask(__name__) # Siempre se arranca asi

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema22072'
mysql.init_app(app)

CARPETA = os.path.join('uploads') # Se ingresa la ruta del directorio que quiero referenciar
app.config['CARPETA'] = CARPETA # Cuando en el sistema hago referencia a la palabra CARPETA, hago referencia al directorio uploads


@app.route('/') # Lo que sucede al entrar al index
def index():  # ese 'index' puede tener otro nombre que yo quiera.
    sql =  "SELECT * FROM `empleados`;" # Quiero que el index me muestre todo lo que esta cargado.
    conn = mysql.connect() # Se abre la coneccion
    cursor = conn.cursor() # Se crea un cursor
    cursor.execute(sql) # Hago que el cursor ejecute la consulta
    empleados = cursor.fetchall() # Trae todos los datos y los mete en una tupla
    print(empleados)
    conn.commit() # Se envian los cambios a la base de datos.
    return render_template('empleados/index.html', empleados=empleados) # En el segundo parametro le pongo el nombre de la variable que quiero

@app.route("/destroy/<int:id>")
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM empleados WHERE ID=%s", id)
    conn.commit()
    return redirect('/')

@app.route("/edit/<int:id>")
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", id) # Solo se busca el empleado con el id que se ingreso
    empleados = cursor.fetchall()
    print(empleados)
    conn.commit()
    return render_template('empleados/edit.html', empleados=empleados) # Envia al usuario a /edit

@app.route("/update", methods=['POST'])
def update():
    id = request.form['txtId'] # Para poder usar el id aca, HAY que ponerlo en el html. Despues se puede ocultar.
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    sql = 'UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s;'
    datos = (_nombre, _correo, id)
    conn = mysql.connect()
    cursor = conn.cursor()
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        fila = cursor.fetchall() # Todo esto es para conseguir el nombre de la foto anterior (que se quiere eliminar ya que se reemplaza con otra)
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        # remove agarra dos parametros. Primero a donde se quiere entrar, y despues que se quiere borrar
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s", (nuevoNombreFoto, id))

    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')

@app.route("/create") # Al entrar a /create, se muestra el contenido de create.html
def create():
    return render_template('empleados/create.html')

@app.route("/store", methods=['POST']) # Al entrar a /store, se toman los datos del formulario
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if _foto.filename != '': # Se verifica que la foto se haya cargado. Si no, nombre es vacio.
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

    sql =  "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    
    datos = (_nombre, _correo, nuevoNombreFoto)
    
    # Grabar en la BD (Base de Datos) VVVV
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos) # Se ejecuta la consulta en mysql, y el segundo parametro es la lista de datos con los que se reemplazan %s del string
    conn.commit()
    return render_template('empleados/index.html') # Al terminar, vuelve a mandar al usuario al index

if __name__ == '__main__':
    app.run(debug=True) # Ejecuta la aplicacion y comienza a correr el controlador