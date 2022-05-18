# first project with Python. Have been learing python for couple of days. Wanted to automate a process at work.


from fileinput import filename
from pathlib import Path
import openpyxl
import PySimpleGUI as sg
import xlwings as xw
import os

#Create GUI Interface

layout = [
    [sg.Text('Koodide muutmine')],
    [sg.Text('Vana kood', size=(15,1)), sg.InputText(key='VANA_KOOD')], #Set old value
    [sg.Text('Uus kood', size=(15,1)), sg.InputText(key='UUS_KOOD')], #Set New Value
    [sg.FolderBrowse('Vali Kaust'), sg.In(size=(50,1), enable_events=True ,key='FOLDER'), ], #Path Browse
    [sg.Submit(),sg.Exit()]
]

window = sg.Window('Koodide muutmine',layout)

while True:
    event,values = window.read()
    dir_path = values['FOLDER'] # Make path readable for the IF 'Submit'
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == 'Submit':
        try:
            #beginning of replacement code
            BASE_DIR = Path(__file__).parent #Set parent directory
            INPUT_DIR = BASE_DIR / dir_path #Set path where to look in
            replacement_pair = {}
            replacement_pair[values['VANA_KOOD']] = values['UUS_KOOD'] #Replacement of values from Given User Input.

            files = list(INPUT_DIR.rglob('*.xls*'))
            for file in files:
                wb = openpyxl.load_workbook(file, read_only=False, keep_vba=True)

                for ws in wb.worksheets: #Replace set values in given path
                    for row in ws.iter_rows():
                        for cell in row:
                            if cell.value in replacement_pair.keys():
                                cell.value = replacement_pair.get(cell.value)
                wb.save(INPUT_DIR / f'{file.stem}.xlsm')

                #End of replacement code

            for file in files: # Excecute Macro in each workbook in folder path
                app = xw.App(visible=False) 
                wb = xw.Book(file)
                files = list(INPUT_DIR.rglob('*.xls*'))
                macro1 = wb.macro('Module1.SaveCopies')
                macro1()
                #wb.save()
                wb.close()
                app.quit()
                dir = INPUT_DIR
            for filename in os.listdir(INPUT_DIR): #re-save files in Upper case, as Macro saves files to lower case (in my case needs to be all caps)
                dst = os.path.join(dir,filename)
                src = os.path.join(dir,filename)   
                os.rename(dst,src.upper())

            sg.popup('Koodid muudetud!') #Popup Completed
            
        except PermissionError:
            sg.popup('faili ei saa kasutada') #Error if file can't be used

window.close()