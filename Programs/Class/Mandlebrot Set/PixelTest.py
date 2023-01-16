from Lib.NewDEGraphics import *

win = DEGraphWin("This is a window")
with win:

	Label("This is a label", font = "Verdana 24 bold underline")
	
	with Flow():
		with Stack(padx=10):
			my_label_text = "This text changes"
			my_label = Label(my_label_text)

			Button("Change the above text", font = "Veranda 12 italic")
			def change_that_text():
				if (askYesNo(message = "Change that text?")):
					my_label.text = "OMG it changed"
			Button("(Also changes that text)", command = change_that_text)
			
			with Flow():
				
				Label("Look, this label counts upwards:")

				counting_label = Label("0")
					
				@repeat(1)
				def update_label():
					new_number = int(counting_label.text) + 1
					counting_label.text = str(new_number)
		
		with Stack(padx=10):
			Message("Below is a combination of a stack and two flows, forming a grid", width=140, borderwidth=1, relief=tk.SUNKEN)
			
			Button("Yes / no / cancel")
			def yes_no_cancel():
				response = askYesNoCancel(message = "What do?")
				if response is True:
					showInfo(message = "You pressed yes")
				elif response is False:
					showWarning(message = "You pressed no")
				elif response is None:
					showError(message = "You pressed cancel")
		
	with Flow():
		edit = TextBox("edit me")
		
		Button("<-read edit box")
		def read_edit_box():
			showInfo(message = "Edit box says: " + edit.text)
		
	
	
	with Stack(padx=2, pady=2, borderwidth=1, relief=tk.SUNKEN):
	
		Label("Browse dialogs", font = "Verdana 10 underline")
		
		with Stack(borderwidth=1, relief=tk.SUNKEN):
			file_label = Label("No file or directory picked", font = "Verdana 12 bold")
	
		with Flow():
			Button("Pick file")
			def pick_file():
				with askOpenFile() as file:
					file_label.text = file.name
			
			Button("Pick directory", padx = 10)
			def pick_file():
				file_label.text = askDirectory()
	
	with Flow():
		Button("Enter integer")
		def enter_integer():
			integer = askInteger("Integer", "Write an integer in the box")
			integer_label.text = str(integer)
			
		integer_label = Label("No integer entered yet")
	
	with Stack(padx=2, pady=2, borderwidth=1, relief=tk.SUNKEN):
	
		Label("Scrolled text", font = "Verdana 10 underline")
	
		scrollText = ScrollableText("\n".join(["line "+str(i) for i in range(1,20)]), width=50, height=0)

		CheckBox("Scrolled text is editable?", checked = True, font = "Verdana 10 bold")
		def check(checked):
			scrollText.editable = checked
			
	with Stack(padx=2, pady=2, borderwidth=1, relief=tk.SUNKEN):
	
		Label("Radio buttons", font = "Verdana 10 underline")
		
		Button("What number is it?")
		def show_number():
			if (set.number == 0):
				showInfo(message = "No radio button selected")
			else:
				showInfo(message = "The selected radio button is: " + str(set.number))
			
		with Flow():
		 
			with Stack():
			
				with RadioButtonGroup() as set:
					RadioButton(1, "one")
					RadioButton(2, "two")
					RadioButton(3, "three")
					def val(value):
						radio_label.text = "Radio button: " + str(value)
					
			with Stack():
							
				radio_label = Label("No radio button checked")
				
				
						
	with Flow():
		Label("This is a spin box:")
		Spinner(values=(1, 2, 4, 8))
		def spin(value):
			spin_label.text = str(value)
		spin_label = Label("1")
		
	with Flow():
		Label("These are scale bars:")
		ScaleBar(from_=0, to=100)
		def scale(value):
			scale_bar_2.value = 100-int(value)
		scale_bar_2 = ScaleBar(from_=0, to=100, enabled=False)
		
	with Flow():
		Label("This is an options menu:")
		OptionsMenu("one", "two", "three")
		def opt(option):
			print(option)
			
	Label("This is a list box")
	list_box = ListBox(height=4, values=["one", "two", "three", "four"])
	listButton = Button("list")
	def read_list():
		print(list_box.selection)
  
	ContextMenu(listButton, ["one", "two", "three"], callback = read_list)
 
	ToolTip(listButton, "This is a tooltip")
  
	with Flow():
		Label("This", font = "Verdana 10 bold")
		AutofitLabel("is", font = "Verdana 10 bold")
		AutoWrappingLabel("a", font = "Verdana 10 bold")
		Label("thing", font = "Verdana 10 bold")
		Label("haha", font = "Verdana 10 bold")
		Label("lol", font = "Verdana 4 italic")
 
		bar = ProgressBar(50, 100, "black", "red", 100, 10)
		bar.setValue(25)
  
	Label("Graph:")
	with Stack():
		graph = Graph(
			x_min=-1.0,
			x_max=1.0,
			y_min=0.0,
			y_max=2.0,
			x_tick=0.2,
			y_tick=0.2,
			width=500,
			height=400
		)
		graph.grid(row=0, column=0)
		# create an initial line
		line_0 = [(x/10, x/10) for x in range(10)]
		graph.plot_line(line_0)
  
	Label("Image: ")
	Image("Screenshot 2022-10-20 113914.png", 100, 100)

	Label("Plot:")
	with Stack():
		plt = Plot(100, 100, color_rgb(10, 100, 60))
	for i in range(100):
		plt.plot(i, 10, (255, 0, 0))
	
	# with ScrollableFrame():
	# 	# with Stack():
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")
	# 	Label("3D frame")