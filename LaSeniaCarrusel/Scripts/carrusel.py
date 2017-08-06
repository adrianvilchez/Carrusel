#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Importamos las librerias.

import gi
import shutil, os
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio, Vte

COL_PATH = 0
COL_PIXBUF = 1
COL_IS_DIRECTORY = 2

(TARGET_ENTRY_TEXT, TARGET_ENTRY_PIXBUF) = range(2)
(COLUMN_TEXT, COLUMN_PIXBUF) = range(2)

class Carrusel(Gtk.Window):
	def __init__(self):
		super(Carrusel, self).__init__()
		self.builder = Gtk.Builder()

		# Cargamos el XML glade que hemos creado.
		self.builder.add_from_file("/home/mrpatxi/Github/Carrusel/LaSeniaCarrusel/Glade/carrusel.glade")

		# Creamos una variable para cargar los menejadores de los eventos.
		self.handlers = {
			"on_carrusel_window_destroy": self.on_carrusel_window_destroy,

			"on_save_button_clicked": self.on_save_button_clicked,

			"on_add_button_docs_clicked": self.on_add_button_docs_clicked,
			"on_del_button_docs_clicked": self.on_del_button_docs_clicked,
			"on_icon_view_docs_item_activated": self.on_icon_view_docs_item_activated,

			"on_add_button_pdfs_clicked": self.on_add_button_pdfs_clicked,
			"on_del_button_pdfs_clicked": self.on_del_button_pdfs_clicked,
			"on_icon_view_pdfs_item_activated": self.on_icon_view_pdfs_item_activated,

			"on_add_button_photos_clicked": self.on_add_button_photos_clicked,
			"on_del_button_photos_clicked": self.on_del_button_photos_clicked,
			"on_icon_view_photos_item_activated": self.on_icon_view_photos_item_activated,
			
			"on_generate_button_clicked": self.on_generate_button_clicked,

			"on_label_dnd_docs_drag_data_received": self.on_label_dnd_docs_drag_data_received,
			"on_label_dnd_pdfs_drag_data_received": self.on_label_dnd_pdfs_drag_data_received,
			"on_label_dnd_photos_drag_data_received": self.on_label_dnd_photos_drag_data_received
		}

		# Conectamos los manejadores del archivo glade con las funciones que hemos declarado.
		self.builder.connect_signals(self.handlers)

		# Accedemos al objeto "Window" mediante el identifivador declarado en el XML de "Glade".
		self.window = self.builder.get_object("carrusel_window")

		# Accedemos al objeto "paginas_carrusel mediante el identifivador declarado en el XML de "Glade".
		self.paginas_carrusel = self.builder.get_object("paginas_carrusel")

		# Enlaces
		# Accedemos al objeto "TextView" mediante el identifivador declarado en el XML de "Glade".
		self.text_view_links = self.builder.get_object("text_view_links")

		# Creamos una variable para obtener el buffer del "TextView".
		self.buf = self.text_view_links.get_buffer()
		
		sw_links = self.builder.get_object("desplazamiento_links")
		sw_links.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
		sw_links.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

		sw_links.add(self.text_view_links)

		with open("/home/mrpatxi/senia-carrusel-workspace/enlaces.txt", 'r') as f:
			data = f.read()
			self.buf.set_text(data)

		self.fileIcon = self.get_icon(Gtk.STOCK_FILE)
		self.dirIcon = self.get_icon(Gtk.STOCK_DIRECTORY)

		# Documentos
		################################### icon_view_docs #########################
		self.icon_view_docs = self.builder.get_object("icon_view_docs")

		self.label_dnd_docs = self.builder.get_object("label_dnd_docs")

		self.label_dnd_docs.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)

		self.add_text_targets_docs()

		self.docs_dir = os.path.expanduser('/home/mrpatxi/senia-carrusel-workspace/docs')
		self.cur_dir_docs = self.docs_dir

		sw_docs = self.builder.get_object("desplazamiento_docs")
		sw_docs.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
		sw_docs.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

		self.store_docs = self.create_store_docs()
		self.fill_store_docs()

		self.icon_view_docs.set_model(self.store_docs)
		#icon_view_docs.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
		self.icon_view_docs.set_selection_mode(Gtk.SelectionMode.SINGLE)

		self.icon_view_docs.set_text_column(COL_PATH)
		self.icon_view_docs.set_pixbuf_column(COL_PIXBUF)
		
		sw_docs.add(self.icon_view_docs)
		self.icon_view_docs.grab_focus()
		self.model_docs = self.icon_view_docs.get_model()

		# PDF's
		self.icon_view_pdfs = self.builder.get_object("icon_view_pdfs")

		self.label_dnd_pdfs = self.builder.get_object("label_dnd_pdfs")

		self.label_dnd_pdfs.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)

		self.add_text_targets_pdfs()

		self.pdfs_dir = os.path.expanduser('/home/mrpatxi/senia-carrusel-workspace/pdfs')
		self.cur_dir_pdfs = self.pdfs_dir

		sw_pdfs = self.builder.get_object("desplazamiento_pdfs")
		sw_pdfs.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
		sw_pdfs.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

		self.store_pdfs = self.create_store_pdfs()
		self.fill_store_pdfs()

		self.icon_view_pdfs.set_model(self.store_pdfs)
		self.icon_view_pdfs.set_selection_mode(Gtk.SelectionMode.SINGLE)

		self.icon_view_pdfs.set_text_column(COL_PATH)
		self.icon_view_pdfs.set_pixbuf_column(COL_PIXBUF)
		
		sw_pdfs.add(self.icon_view_pdfs)
		self.icon_view_pdfs.grab_focus()
		self.model_pdfs = self.icon_view_pdfs.get_model()		
		
		# Images
		self.icon_view_photos = self.builder.get_object("icon_view_photos")

		self.label_dnd_photos = self.builder.get_object("label_dnd_photos")

		self.label_dnd_photos.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)

		self.add_text_targets_photos()

		self.photos_dir = os.path.expanduser('/home/mrpatxi/senia-carrusel-workspace/photos')
		self.cur_dir_photos = self.photos_dir

		sw_photos = self.builder.get_object("desplazamiento_photos")
		sw_photos.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
		sw_photos.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

		self.store_photos = self.create_store_photos()
		self.fill_store_photos()

		self.icon_view_photos.set_model(self.store_photos)
		self.icon_view_photos.set_selection_mode(Gtk.SelectionMode.SINGLE)

		self.icon_view_photos.set_text_column(COL_PATH)
		self.icon_view_photos.set_pixbuf_column(COL_PIXBUF)
		
		sw_photos.add(self.icon_view_photos)
		self.icon_view_photos.grab_focus()
		self.model_photos = self.icon_view_photos.get_model()
		
		# Creamos la visiluacizaci�n de los eventos de la ventana.
		
		self.sw_viewport = self.builder.get_object("desplazamiento_viewport")
		self.viewport = self.builder.get_object("viewport")
		
		
		# Creamos la terminal
		self.terminal = Vte.Terminal()
		self.terminal.spawn_sync(
			Vte.PtyFlags.DEFAULT,
			os.environ['HOME'],
			["/bin/sh"],
			[],
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None,
			None,
			)

		self.command = "bash /usr/bin/senia-carrusel\n"
		self.viewport.add(self.terminal)
		
		self.sw_viewport.add(self.viewport)
		self.window.show_all()
			
	################################### on_del_button_docs_clicked #########################
	def on_carrusel_window_destroy(self, *args):
		Gtk.main_quit(*args)

	################################### on_save_button_clicked #############################
	# Funcion para guardar las url en el fichero "enlaces.txt".
	def on_save_button_clicked(self, window):
		# Creamos una variable de la que obtenemos el principio y el final del buffer "TextView".
		texto = self.buf.get_text(self.buf.get_start_iter(), self.buf.get_end_iter(), True)
		
		# Abrimos la ruta del archivo y la sobre-escribimos con los datos almacenados en la variable "texto".
		open("/home/mrpatxi/senia-carrusel-workspace/enlaces.txt", "w").write(texto)

	# Inicio Documentos ###########################################################################
	def on_add_button_docs_clicked(self, widget):
		dialog = Gtk.FileChooserDialog("Seleccione un archivo", None,
		Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
		Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		self.add_filters_docs(dialog)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			origen = dialog.get_filename()

			ruta = os.path.basename(origen)
			destino = "/home/mrpatxi/senia-carrusel-workspace/docs/" + ruta
			shutil.copyfile(origen, destino)

			self.fill_store_docs()
		elif response == Gtk.ResponseType.CANCEL:
			print("[Log]: El usuario ha cancelado la seleccion de archivos.")

		dialog.destroy()

	def on_del_button_docs_clicked(self, data):
		try:
			self.icon_view_docs.item_activated(self.icon_view_docs.get_cursor()[1])
			if self.path:
				filepath_docs = self.cur_dir_docs + os.path.sep + self.path
				os.remove(filepath_docs)
				print("PDF" + filepath_docs + " Se ha eliminado con éxito.")
				self.fill_store_docs()
		except:
			pass

	def add_filters_docs(self, dialog):
		filter_text = Gtk.FileFilter()
		filter_text.set_name("Documentos")
		filter_text.add_mime_type("Documentos/docs")
		filter_text.add_pattern("*.odt")
		filter_text.add_pattern("*.doc")
		filter_text.add_pattern("*.docs")
		dialog.add_filter(filter_text)

	def create_store_docs(self):
		store_docs = Gtk.ListStore(str, GdkPixbuf.Pixbuf, bool)
		store_docs.set_sort_column_id(COL_PATH, Gtk.SortType.ASCENDING)
		return store_docs

	def fill_store_docs(self):
		self.store_docs.clear()

		if self.cur_dir_docs == None:
			return

		for fl in os.listdir(self.cur_dir_docs):
			if not fl[0] == '.': 
				if os.path.isdir(os.path.join(self.cur_dir_docs, fl)):
					self.store_docs.append([fl, self.dirIcon, True])
				else:
					self.store_docs.append([fl, self.fileIcon, False])

	def on_icon_view_docs_item_activated(self, widget, item):
		path = self.model_docs[item][COL_PATH]
		isDir = self.model_docs[item][COL_IS_DIRECTORY]

		if not isDir:
			self.path = path
			return

	def add_text_targets_docs(self, button=None):
		self.label_dnd_docs.drag_dest_set_target_list(None)

		self.label_dnd_docs.drag_dest_add_text_targets()

	def add_text_targets_pdfs(self, button=None):
		self.label_dnd_pdfs.drag_dest_set_target_list(None)

		self.label_dnd_pdfs.drag_dest_add_text_targets()
		
	def add_text_targets_photos(self, button=None):
		self.label_dnd_photos.drag_dest_set_target_list(None)

		self.label_dnd_photos.drag_dest_add_text_targets()

	# Fin Documentos ###########################################################################

	# Inicio PDF's ###########################################################################
	def on_add_button_pdfs_clicked(self, widget):
		dialog_pdfs = Gtk.FileChooserDialog("Seleccione un archivo", None,
		Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
		Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		self.add_filters_pdfs(dialog_pdfs)

		response = dialog_pdfs.run()
		if response == Gtk.ResponseType.OK:
			origen_pdfs = dialog_pdfs.get_filename()

			ruta_pdfs = os.path.basename(origen_pdfs)
			destino_pdfs = "/home/mrpatxi/senia-carrusel-workspace/pdfs/" + ruta_pdfs
			shutil.copyfile(origen_pdfs, destino_pdfs)

			self.fill_store_pdfs()
		elif response == Gtk.ResponseType.CANCEL:
			print("[Log]: El usuario ha cancelado la seleccion de archivos.")

		dialog_pdfs.destroy()

	def add_filters_pdfs(self, dialog_pdfs):
		filter_text = Gtk.FileFilter()
		filter_text.set_name("Documentos")
		filter_text.add_mime_type("Documentos/PDFs")
		filter_text.add_pattern("*.pdf")
		dialog_pdfs.add_filter(filter_text)

	def on_del_button_pdfs_clicked(self, data):
		try:
			#print(str(self.icon_view_docs.get_cursor()[0]))
			self.icon_view_pdfs.item_activated(self.icon_view_pdfs.get_cursor()[1])
			if self.path:
				filepath_pdfs = self.cur_dir_pdfs + os.path.sep + self.path
				os.remove(filepath_pdfs)
				print("PDF" + filepath_pdfs + " Se ha eliminado con éxito.")
				self.fill_store_pdfs()
		except:
			pass

	def get_icon(self, name):
		theme = Gtk.IconTheme.get_default()
		return theme.load_icon(name, 29, 0)

	def create_store_pdfs(self):
		store_pdfs = Gtk.ListStore(str, GdkPixbuf.Pixbuf, bool)
		store_pdfs.set_sort_column_id(COL_PATH, Gtk.SortType.ASCENDING)
		return store_pdfs

	def fill_store_pdfs(self):
		self.store_pdfs.clear()

		if self.cur_dir_pdfs == None:
			return

		for fl in os.listdir(self.cur_dir_pdfs):
			if not fl[0] == '.': 
				if os.path.isdir(os.path.join(self.cur_dir_pdfs, fl)):
					self.store_pdfs.append([fl, self.dirIcon, True])
				else:
					self.store_pdfs.append([fl, self.fileIcon, False])

	def on_icon_view_pdfs_item_activated(self, widget, item):
		#model = widget.get_model()
		path = self.model_pdfs[item][COL_PATH]
		isDir = self.model_pdfs[item][COL_IS_DIRECTORY]

		if not isDir:
			self.path = path
			return

	# Fin PDF's ###########################################################################

	# Inicio Fotos ###########################################################################
	def on_add_button_photos_clicked(self, widget):
		dialog = Gtk.FileChooserDialog("Seleccione un archivo", None,
		Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
		Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		self.add_filters_photos(dialog)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			origen = dialog.get_filename()

			ruta = os.path.basename(origen)
			destino = "/home/mrpatxi/senia-carrusel-workspace/photos/" + ruta
			shutil.copyfile(origen, destino)

			self.fill_store_photos()
		elif response == Gtk.ResponseType.CANCEL:
			print("[Log]: El usuario ha cancelado la seleccion de archivos.")

		dialog.destroy()

	def add_filters_photos(self, dialog):
		filter_text = Gtk.FileFilter()
		filter_text.set_name("Documentos")
		filter_text.add_mime_type("Documentos/Fotos")
		filter_text.add_pattern("*.png")
		filter_text.add_pattern("*.jpg")
		filter_text.add_pattern("*.raw")
		filter_text.add_pattern("*.psd")
		filter_text.add_pattern("*.bmp")
		filter_text.add_pattern("*.tiff")
		filter_text.add_pattern("*.xcf")
		filter_text.add_pattern("*.gif")
		filter_text.add_pattern("*.eps")
		filter_text.add_pattern("*.pcx")
		filter_text.add_pattern("*.pict")
		filter_text.add_pattern("*.dng")
		filter_text.add_pattern("*.wmp")
		filter_text.add_pattern("*.jp2")
		filter_text.add_pattern("*.psb")
		dialog.add_filter(filter_text)

	def on_del_button_photos_clicked(self, data):
		try:
			self.icon_view_photos.item_activated(self.icon_view_photos.get_cursor()[1])
			if self.path:
				filepath_photos = self.cur_dir_photos + os.path.sep + self.path
				os.remove(filepath_photos)
				print("PHOTOS" + filepath_photos + " Se ha eliminado con éxito.")
				self.fill_store_photos()
		except:
			pass

	def create_store_photos(self):
		store_photos = Gtk.ListStore(str, GdkPixbuf.Pixbuf, bool)
		store_photos.set_sort_column_id(COL_PATH, Gtk.SortType.ASCENDING)
		return store_photos

	def fill_store_photos(self):
		self.store_photos.clear()

		if self.cur_dir_photos == None:
			return

		for fl in os.listdir(self.cur_dir_photos):
			if not fl[0] == '.': 
				if os.path.isdir(os.path.join(self.cur_dir_photos, fl)):
					self.store_photos.append([fl, self.dirIcon, True])
				else:
					self.store_photos.append([fl, self.fileIcon, False])
					
	def on_icon_view_photos_item_activated(self, widget, item):
		path = self.model_photos[item][COL_PATH]
		isDir = self.model_photos[item][COL_IS_DIRECTORY]

		if not isDir:
			self.path = path
			return

	# Fin Fotos ###########################################################################

	def on_generate_button_clicked(self, widget):
		length = len(self.command)
		self.terminal.feed_child(self.command, length)
		self.paginas_carrusel.next_page()

	############################# drag_and_drop_docs ###################################

	def on_label_dnd_docs_drag_data_received(self, label_dnd_docs, drag_context, x,y, data,info, time):
		try:
			if info == TARGET_ENTRY_TEXT:
				text = data.get_text()
				
				file =  text.split('/')[-1]
				origen = text.split('file://')[-1]
				origen = origen[:-1]
				origen = origen.rstrip('\r')

				destino = "/home/mrpatxi/senia-carrusel-workspace/docs/" + file

				shutil.copyfile(origen, destino)
				self.fill_store_docs()

		except:
			error = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 'El archivo contiene tildes o espacios.')
			error.run()
			error.destroy()
			pass

	def on_label_dnd_pdfs_drag_data_received(self, label_dnd_pdfs, drag_context, x,y, data,info, time):
		try:
			if info == TARGET_ENTRY_TEXT:
				text = data.get_text()
				
				file =  text.split('/')[-1]
				origen = text.split('file://')[-1]
				origen = origen[:-1]
				origen = origen.rstrip('\r')

				destino = "/home/mrpatxi/senia-carrusel-workspace/pdfs/" + file

				shutil.copyfile(origen, destino)
				self.fill_store_pdfs()

		except:
			error = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 'El archivo contiene tildes o espacios.')
			error.run()
			error.destroy()
			pass

	def on_label_dnd_photos_drag_data_received(self, label_dnd_photos, drag_context, x,y, data,info, time):
		try:
			if info == TARGET_ENTRY_TEXT:
				text = data.get_text()
				
				file =  text.split('/')[-1]
				origen = text.split('file://')[-1]
				origen = origen[:-1]
				origen = origen.rstrip('\r')

				destino = "/home/mrpatxi/senia-carrusel-workspace/photos/" + file

				shutil.copyfile(origen, destino)
				self.fill_store_photos()

		except:
			error = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 'El archivo contiene tildes o espacios.')
			error.run()
			error.destroy()
			pass

def main():
	window = Carrusel()
	Gtk.main()

if __name__ == '__main__':
	main()
