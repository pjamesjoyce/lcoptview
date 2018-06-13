from tkinter import *
from tkinter import ttk
from tkinter import filedialog  # , simpledialog
from lcoptview.flask_gui import app
import webbrowser
import socket


def main():
   
    def load_model(*args):
        print("Load")
        root.withdraw()

        titleString = "Choose a model to open"
        filetypesList = [('Lcopt model files', '.lcoptview')]
        file_path = filedialog.askopenfilename(title=titleString, filetypes=filetypesList)
        
        if file_path:
            app.config['CURRENT_FILE'] = file_path

            for port in range(5000, 5100):

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', port))
                
                if result != 0:
                    break
                else:
                    print("port {} is in use, checking {}".format(port, port + 1))

            url = 'http://127.0.0.1:{}/'.format(port)
            webbrowser.open_new(url)
            #print ("running from the module")
            
            app.run(port=port, use_reloader=False)

        root.destroy()

    root = Tk()
    root.title("LCOPTVIEW Launcher")
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    initial_width = 310
    initial_height = 100
    initial_x = int(screen_width / 2 - initial_width / 2)
    initial_y = int(screen_height / 2 - initial_height / 2)

    root.geometry('{}x{}+{}+{}'.format(initial_width, initial_height, initial_x, initial_y))

    #TODO: Maybe figure out how to use a custom icon - not urgent 
    #img = PhotoImage(file = r'C:\Users\pjjoyce\Dropbox\04. REDMUD IP LCA Project\04. Modelling\lcopt\static\img\lcoptIcon2.gif')
    #root.tk.call('wm', 'iconphoto', root._w, img)

    mainframe = ttk.Frame(root, padding="20 20 20 20") # padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    ttk.Label(mainframe, text="Welcome to the LCOPTVIEW Launcher").grid(column=1, row=1) #, columnspan=3)
    ttk.Button(mainframe, text="Choose file...", command=load_model).grid(column=1, row=2) #, sticky=E)

    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.mainloop()
    #root.update()
    print('bye')


if __name__ == "__main__":
    main()
