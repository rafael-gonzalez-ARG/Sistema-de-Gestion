import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('heladeria.db')
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                direccion TEXT,
                telefono TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT,
                precio REAL NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_total REAL NOT NULL,
                fecha TEXT NOT NULL,
                FOREIGN KEY (producto_id) REFERENCES Productos (id)
            )
        ''')
        self.connection.commit()

class ClientManager:
    def __init__(self, db):
        self.db = db

    def add_client(self, nombre, direccion, telefono):
        self.db.cursor.execute('INSERT INTO Clientes (nombre, direccion, telefono) VALUES (?, ?, ?)', 
                               (nombre, direccion, telefono))
        self.db.connection.commit()

    def get_clients(self):
        self.db.cursor.execute('SELECT * FROM Clientes')
        return self.db.cursor.fetchall()

    def update_client(self, client_id, nombre, direccion, telefono):
        self.db.cursor.execute('UPDATE Clientes SET nombre=?, direccion=?, telefono=? WHERE id=?',
                               (nombre, direccion, telefono, client_id))
        self.db.connection.commit()

    def delete_client(self, client_id):
        self.db.cursor.execute('DELETE FROM Clientes WHERE id=?', (client_id,))
        self.db.connection.commit()

class ProductManager:
    def __init__(self, db):
        self.db = db

    def add_product(self, nombre, categoria, precio):
        self.db.cursor.execute('INSERT INTO Productos (nombre, categoria, precio) VALUES (?, ?, ?)', 
                               (nombre, categoria, precio))
        self.db.connection.commit()

    def get_products(self):
        self.db.cursor.execute('SELECT * FROM Productos')
        return self.db.cursor.fetchall()

    def update_product(self, product_id, nombre, categoria, precio):
        self.db.cursor.execute('UPDATE Productos SET nombre=?, categoria=?, precio=? WHERE id=?',
                               (nombre, categoria, precio, product_id))
        self.db.connection.commit()

    def delete_product(self, product_id):
        self.db.cursor.execute('DELETE FROM Productos WHERE id=?', (product_id,))
        self.db.connection.commit()

class SalesManager:
    def __init__(self, db):
        self.db = db

    def sell_product(self, product_id, cantidad):
        self.db.cursor.execute('SELECT precio FROM Productos WHERE id=?', (product_id,))
        precio = self.db.cursor.fetchone()
        if precio:
            precio_total = precio[0] * cantidad
            self.db.cursor.execute('INSERT INTO Ventas (producto_id, cantidad, precio_total, fecha) VALUES (?, ?, ?, DATE("now"))',
                                   (product_id, cantidad, precio_total))
            self.db.connection.commit()
        else:
            raise ValueError("Producto no encontrado")

    def get_sales(self):
        self.db.cursor.execute('SELECT * FROM Ventas')
        return self.db.cursor.fetchall()

class HeladeriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión - Heladería")
        self.db = Database()
        self.client_manager = ClientManager(self.db)
        self.product_manager = ProductManager(self.db)
        self.sales_manager = SalesManager(self.db)

        self.create_menu()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        gestion_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Gestión", menu=gestion_menu)
        gestion_menu.add_command(label="Clientes", command=self.open_client_management)
        gestion_menu.add_command(label="Productos", command=self.open_product_management)
        gestion_menu.add_command(label="Punto de Venta", command=self.open_sales_point)
        gestion_menu.add_command(label="Cerrar Caja", command=self.open_sales_report)

    def open_client_management(self):
        ClientManagementWindow(self)

    def open_product_management(self):
        ProductManagementWindow(self)

    def open_sales_point(self):
        SalesPointWindow(self)

    def open_sales_report(self):
        SalesReportWindow(self)

class ClientManagementWindow:
    def __init__(self, app):
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title("Gestión de Clientes - Heladería")
        self.window.geometry("600x500")

        self.selected_client_id = None

        self.create_widgets()

    def create_widgets(self):
        label_nombre_cliente = tk.Label(self.window, text="Nombre del Cliente:")
        label_nombre_cliente.pack(pady=5)
        self.entry_nombre_cliente = tk.Entry(self.window, width=40)
        self.entry_nombre_cliente.pack(pady=5)

        label_direccion_cliente = tk.Label(self.window, text="Dirección:")
        label_direccion_cliente.pack(pady=5)
        self.entry_direccion_cliente = tk.Entry(self.window, width=40)
        self.entry_direccion_cliente.pack(pady=5)

        label_telefono_cliente = tk.Label(self.window, text="Teléfono:")
        label_telefono_cliente.pack(pady=5)
        self.entry_telefono_cliente = tk.Entry(self.window, width=40)
        self.entry_telefono_cliente.pack(pady=5)

        btn_agregar_cliente = tk.Button(self.window, text="Agregar Cliente", command=self.add_client)
        btn_agregar_cliente.pack(pady=10)

        self.tree_clientes = ttk.Treeview(self.window, columns=('ID', 'Nombre', 'Dirección', 'Teléfono'), show='headings')
        self.tree_clientes.heading('ID', text='ID')
        self.tree_clientes.heading('Nombre', text='Nombre')
        self.tree_clientes.heading('Dirección', text='Dirección')
        self.tree_clientes.heading('Teléfono', text='Teléfono')
        self.tree_clientes.column('ID', anchor='center')
        self.tree_clientes.pack(pady=10, fill='x')

        self.tree_clientes.bind('<<TreeviewSelect>>', self.select_client)

        btn_actualizar_cliente = tk.Button(self.window, text="Actualizar Cliente", command=self.update_client)
        btn_actualizar_cliente.pack(pady=5)

        btn_eliminar_cliente = tk.Button(self.window, text="Eliminar Cliente", command=self.delete_client)
        btn_eliminar_cliente.pack(pady=5)

        self.load_clients()

    def load_clients(self):
        for row in self.tree_clientes.get_children():
            self.tree_clientes.delete(row)

        clients = self.app.client_manager.get_clients()
        for client in clients:
            self.tree_clientes.insert('', tk.END, values=client)

    def add_client(self):
        nombre = self.entry_nombre_cliente.get()
        direccion = self.entry_direccion_cliente.get()
        telefono = self.entry_telefono_cliente.get()

        if nombre:  # Verificar campo requerido
            self.app.client_manager.add_client(nombre, direccion, telefono)
            messagebox.showinfo("Cliente agregado", f"Cliente '{nombre}' agregado con éxito.")
            self.entry_nombre_cliente.delete(0, tk.END)
            self.entry_direccion_cliente.delete(0, tk.END)
            self.entry_telefono_cliente.delete(0, tk.END)
            self.load_clients()
        else:
            messagebox.showwarning("Error", "El campo 'Nombre' es obligatorio.")

    def select_client(self, event):
        selected_item = self.tree_clientes.selection()
        if selected_item:
            item = self.tree_clientes.item(selected_item)
            self.selected_client_id = item['values'][0]  # ID del cliente seleccionado
            self.entry_nombre_cliente.delete(0, tk.END)
            self.entry_nombre_cliente.insert(0, item['values'][1])
            self.entry_direccion_cliente.delete(0, tk.END)
            self.entry_direccion_cliente.insert(0, item['values'][2])
            self.entry_telefono_cliente.delete(0, tk.END)
            self.entry_telefono_cliente.insert(0, item['values'][3])

    def update_client(self):
        if self.selected_client_id:
            nombre = self.entry_nombre_cliente.get()
            direccion = self.entry_direccion_cliente.get()
            telefono = self.entry_telefono_cliente.get()

            if nombre:  # Verificar campo requerido
                self.app.client_manager.update_client(self.selected_client_id, nombre, direccion, telefono)
                messagebox.showinfo("Cliente actualizado", f"Cliente '{nombre}' actualizado con éxito.")
                self.load_clients()
            else:
                messagebox.showwarning("Error", "El campo 'Nombre' es obligatorio.")
        else:
            messagebox.showwarning("Error", "Seleccione un cliente para actualizar.")

    def delete_client(self):
        if self.selected_client_id:
            self.app.client_manager.delete_client(self.selected_client_id)
            messagebox.showinfo("Cliente eliminado", "Cliente eliminado con éxito.")
            self.load_clients()
            self.selected_client_id = None
            self.entry_nombre_cliente.delete(0, tk.END)
            self.entry_direccion_cliente.delete(0, tk.END)
            self.entry_telefono_cliente.delete(0, tk.END)
        else:
            messagebox.showwarning("Error", "Seleccione un cliente para eliminar.")

class ProductManagementWindow:
    def __init__(self, app):
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title("Gestión de Productos - Heladería")
        self.window.geometry("600x500")

        self.selected_product_id = None

        self.create_widgets()

    def create_widgets(self):
        label_nombre_producto = tk.Label(self.window, text="Nombre del Producto:")
        label_nombre_producto.pack(pady=5)
        self.entry_nombre_producto = tk.Entry(self.window, width=40)
        self.entry_nombre_producto.pack(pady=5)

        label_categoria_producto = tk.Label(self.window, text="Categoría:")
        label_categoria_producto.pack(pady=5)
        self.entry_categoria_producto = tk.Entry(self.window, width=40)
        self.entry_categoria_producto.pack(pady=5)

        label_precio_producto = tk.Label(self.window, text="Precio:")
        label_precio_producto.pack(pady=5)
        self.entry_precio_producto = tk.Entry(self.window, width=40)
        self.entry_precio_producto.pack(pady=5)

        btn_agregar_producto = tk.Button(self.window, text="Agregar Producto", command=self.add_product)
        btn_agregar_producto.pack(pady=10)

        self.tree_productos = ttk.Treeview(self.window, columns=('ID', 'Nombre', 'Categoría', 'Precio'), show='headings')
        self.tree_productos.heading('ID', text='ID')
        self.tree_productos.heading('Nombre', text='Nombre')
        self.tree_productos.heading('Categoría', text='Categoría')
        self.tree_productos.heading('Precio', text='Precio')
        self.tree_productos.column('ID', anchor='center')
        self.tree_productos.pack(pady=10, fill='x')

        self.tree_productos.bind('<<TreeviewSelect>>', self.select_product)

        btn_actualizar_producto = tk.Button(self.window, text="Actualizar Producto", command=self.update_product)
        btn_actualizar_producto.pack(pady=5)

        btn_eliminar_producto = tk.Button(self.window, text="Eliminar Producto", command=self.delete_product)
        btn_eliminar_producto.pack(pady=5)

        self.load_products()

    def load_products(self):
        for row in self.tree_productos.get_children():
            self.tree_productos.delete(row)

        products = self.app.product_manager.get_products()
        for product in products:
            self.tree_productos.insert('', tk.END, values=product)

    def add_product(self):
        nombre = self.entry_nombre_producto.get()
        categoria = self.entry_categoria_producto.get()
        precio = self.entry_precio_producto.get()

        if nombre and precio:  # Verificar campos requeridos
            try:
                precio = float(precio)  # Convertir a float
                self.app.product_manager.add_product(nombre, categoria, precio)
                messagebox.showinfo("Producto agregado", f"Producto '{nombre}' agregado con éxito.")
                self.entry_nombre_producto.delete(0, tk.END)
                self.entry_categoria_producto.delete(0, tk.END)
                self.entry_precio_producto.delete(0, tk.END)
                self.load_products()
            except ValueError:
                messagebox.showwarning("Error", "El precio debe ser un número.")
        else:
            messagebox.showwarning("Error", "Los campos 'Nombre' y 'Precio' son obligatorios.")

    def select_product(self, event):
        selected_item = self.tree_productos.selection()
        if selected_item:
            item = self.tree_productos.item(selected_item)
            self.selected_product_id = item['values'][0]  # ID del producto seleccionado
            self.entry_nombre_producto.delete(0, tk.END)
            self.entry_nombre_producto.insert(0, item['values'][1])
            self.entry_categoria_producto.delete(0, tk.END)
            self.entry_categoria_producto.insert(0, item['values'][2])
            self.entry_precio_producto.delete(0, tk.END)
            self.entry_precio_producto.insert(0, item['values'][3])

    def update_product(self):
        if self.selected_product_id:
            nombre = self.entry_nombre_producto.get()
            categoria = self.entry_categoria_producto.get()
            precio = self.entry_precio_producto.get()

            if nombre and precio:  # Verificar campos requeridos
                try:
                    precio = float(precio)  # Convertir a float
                    self.app.product_manager.update_product(self.selected_product_id, nombre, categoria, precio)
                    messagebox.showinfo("Producto actualizado", f"Producto '{nombre}' actualizado con éxito.")
                    self.load_products()
                except ValueError:
                    messagebox.showwarning("Error", "El precio debe ser un número.")
            else:
                messagebox.showwarning("Error", "Los campos 'Nombre' y 'Precio' son obligatorios.")
        else:
            messagebox.showwarning("Error", "Seleccione un producto para actualizar.")

    def delete_product(self):
        if self.selected_product_id:
            self.app.product_manager.delete_product(self.selected_product_id)
            messagebox.showinfo("Producto eliminado", "Producto eliminado con éxito.")
            self.load_products()
            self.selected_product_id = None
            self.entry_nombre_producto.delete(0, tk.END)
            self.entry_categoria_producto.delete(0, tk.END)
            self.entry_precio_producto.delete(0, tk.END)
        else:
            messagebox.showwarning("Error", "Seleccione un producto para eliminar.")

class SalesPointWindow:
    def __init__(self, app):
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title("Punto de Venta - Heladería")
        self.window.geometry("500x600")
        
        # Variables de control
        self.selected_product_price = 0.0
        self.total_amount = 0.0
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sección de producto
        product_frame = ttk.LabelFrame(main_frame, text="Selección de Producto", padding="10")
        product_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(product_frame, text="Producto:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.combo_producto = ttk.Combobox(product_frame, width=40)
        self.combo_producto.grid(row=0, column=1, padx=5, pady=5)
        self.combo_producto.bind("<<ComboboxSelected>>", self.on_product_selected)
        
        # Precio unitario
        ttk.Label(product_frame, text="Precio Unitario:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.label_precio_unitario = ttk.Label(product_frame, text="$0.00")
        self.label_precio_unitario.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Cantidad
        ttk.Label(product_frame, text="Cantidad:").grid(row=2, column=0, sticky=tk.W, pady=5)
        vcmd = (self.window.register(self.validate_quantity), '%P')
        self.entry_cantidad = ttk.Entry(product_frame, width=10, validate='key', validatecommand=vcmd)
        self.entry_cantidad.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.entry_cantidad.bind("<KeyRelease>", self.update_total)
        
        # Frame para el total
        total_frame = ttk.LabelFrame(main_frame, text="Total", padding="10")
        total_frame.pack(fill=tk.X, pady=10)
        
        # Total a pagar
        ttk.Label(total_frame, text="Total a Pagar:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.label_total = ttk.Label(total_frame, text="$0.00", font=('Arial', 12, 'bold'))
        self.label_total.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Frame para el pago
        payment_frame = ttk.LabelFrame(main_frame, text="Pago", padding="10")
        payment_frame.pack(fill=tk.X, pady=10)
        
        # Monto pagado
        ttk.Label(payment_frame, text="Monto Pagado:").grid(row=0, column=0, sticky=tk.W, pady=5)
        vcmd_payment = (self.window.register(self.validate_payment), '%P')
        self.entry_pago = ttk.Entry(payment_frame, width=15, validate='key', validatecommand=vcmd_payment)
        self.entry_pago.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.entry_pago.bind("<KeyRelease>", self.update_change)
        
        # Vuelto
        ttk.Label(payment_frame, text="Vuelto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.label_vuelto = ttk.Label(payment_frame, text="$0.00", font=('Arial', 12, 'bold'))
        self.label_vuelto.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Botón de venta
        self.btn_vender = ttk.Button(main_frame, text="Realizar Venta", command=self.sell_product)
        self.btn_vender.pack(pady=20)
        
        # Cargar productos
        self.load_products()
    
    def validate_quantity(self, new_value):
        """Validar que solo se ingresen números enteros positivos"""
        if new_value == "":
            return True
        try:
            value = int(new_value)
            return value >= 0
        except ValueError:
            return False
    
    def validate_payment(self, new_value):
        """Validar que solo se ingresen números con hasta dos decimales"""
        if new_value == "":
            return True
        try:
            value = float(new_value)
            # Verificar que no tenga más de 2 decimales
            decimals = len(new_value.split('.')[-1]) if '.' in new_value else 0
            return value >= 0 and (decimals <= 2)
        except ValueError:
            return False
    
    def load_products(self):
        """Cargar la lista de productos en el combobox"""
        products = self.app.product_manager.get_products()
        self.products_data = {f"{product[1]} (ID: {product[0]})": 
                            {"id": product[0], "precio": product[3]} 
                            for product in products}
        self.combo_producto['values'] = list(self.products_data.keys())
    
    def on_product_selected(self, event=None):
        """Actualizar el precio unitario cuando se selecciona un producto"""
        selected = self.combo_producto.get()
        if selected in self.products_data:
            self.selected_product_price = self.products_data[selected]["precio"]
            self.label_precio_unitario.config(text=f"${self.selected_product_price:.2f}")
            self.update_total()
        else:
            self.selected_product_price = 0.0
            self.label_precio_unitario.config(text="$0.00")
    
    def update_total(self, event=None):
        """Actualizar el total basado en el producto y la cantidad"""
        try:
            cantidad = int(self.entry_cantidad.get() or 0)
            self.total_amount = self.selected_product_price * cantidad
            self.label_total.config(text=f"${self.total_amount:.2f}")
            self.update_change()  # Actualizar el vuelto también
        except ValueError:
            self.total_amount = 0.0
            self.label_total.config(text="$0.00")
    
    def update_change(self, event=None):
        """Actualizar el vuelto basado en el monto pagado y el total"""
        try:
            monto_pagado = float(self.entry_pago.get() or 0)
            vuelto = monto_pagado - self.total_amount
            self.label_vuelto.config(text=f"${vuelto:.2f}")
            # Cambiar el color del vuelto según si es suficiente o no
            if vuelto >= 0:
                self.label_vuelto.config(foreground="dark green")
            else:
                self.label_vuelto.config(foreground="red")
        except ValueError:
            self.label_vuelto.config(text="$0.00", foreground="black")
    
    def sell_product(self):
        """Realizar la venta"""
        selected = self.combo_producto.get()
        
        if not selected:
            messagebox.showwarning("Error", "Debe seleccionar un producto.")
            return
            
        try:
            cantidad = int(self.entry_cantidad.get() or 0)
            if cantidad <= 0:
                messagebox.showwarning("Error", "La cantidad debe ser mayor a 0.")
                return
                
            monto_pagado = float(self.entry_pago.get() or 0)
            if monto_pagado < self.total_amount:
                messagebox.showwarning("Error", "El monto pagado es insuficiente.")
                return
            
            # Realizar la venta
            producto_id = self.products_data[selected]["id"]
            self.app.sales_manager.sell_product(producto_id, cantidad)
            
            # Mostrar mensaje de éxito
            vuelto = monto_pagado - self.total_amount
            messagebox.showinfo("Venta exitosa", 
                              f"Venta realizada con éxito.\nTotal: ${self.total_amount:.2f}\n"
                              f"Pagado: ${monto_pagado:.2f}\nVuelto: ${vuelto:.2f}")
            
            # Limpiar campos
            self.reset_fields()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def reset_fields(self):
        """Limpiar todos los campos después de una venta"""
        self.combo_producto.set("")
        self.entry_cantidad.delete(0, tk.END)
        self.entry_pago.delete(0, tk.END)
        self.label_precio_unitario.config(text="$0.00")
        self.label_total.config(text="$0.00")
        self.label_vuelto.config(text="$0.00", foreground="black")
        self.selected_product_price = 0.0
        self.total_amount = 0.0

class SalesReportWindow:
    def __init__(self, app):
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title("Cierre de Caja - Heladería")
        self.window.geometry("400x300")

        btn_ver_total = tk.Button(self.window, text="Ver Total de Ventas", command=self.show_total_sales)
        btn_ver_total.pack(pady=20)

    def show_total_sales(self):
        self.app.db.cursor.execute('SELECT SUM(precio_total) FROM Ventas WHERE fecha = DATE("now")')
        total_ventas = self.app.db.cursor.fetchone()[0]
        total_ventas = total_ventas if total_ventas is not None else 0  # Manejar si no hay ventas
        messagebox.showinfo("Total de Ventas", f"Total de ventas del día: ${total_ventas}")

# Código principal
if __name__ == "__main__":
    root = tk.Tk()  # Crea la ventana principal
    app = HeladeriaApp(root)  # Pasa la ventana principal a HeladeriaApp
    root.mainloop()  # Inicia el bucle principal de la interfaz
