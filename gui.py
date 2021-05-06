from tkinter import *
import steuerung
from functools import partial
import mapping

root = Tk()
root.title("QRadar-Jira Schnittstelle")
root.geometry('800x700')

#Hier findet der Login statt und ruft bei Erfolg das nächste Fenster auf:
class login():
    def __init__(self):
        self.font = "Verdana 16"
        self.labelUsr = Label(root, text = "Nutzername", font = self.font)
        self.labelPwd = Label(root, text = "Passwort", font = self.font)
        self.usr = Entry(root, font = self.font)
        self.pwd = Entry(root, show="*", font = self.font)
        self.loginButton = Button(root, text="LOGIN", font = self.font, command=lambda: self.click_login(str.lower(self.usr.get()),self.pwd.get()))
        self.labelLoginFail = Label(root, text = "Login nicht erfolgreich", font = self.font)
        self.labelLoginSuceed = Label(root, text = "Login erfolgreich. Daten werden geladen...", font = self.font)
    
        self.labelUsr.pack()
        self.usr.pack()
        self.labelPwd.pack()
        self.pwd.pack()
        self.loginButton.pack()
    
    def click_login(self, user, password):
        if steuerung.login_check(user,password) == True:
            self.labelLoginFail.destroy()
            self.labelLoginSuceed.pack()
            root.update()

            mainClass = steuerung.Main(user, password)
            windowStartseite = OffensesWithoutCase(mainClass)
            
            self.labelUsr.destroy()
            self.usr.destroy()
            self.labelPwd.destroy()
            self.pwd.destroy()
            self.labelLoginSuceed.destroy()
            self.labelLoginFail.destroy()
            self.loginButton.destroy()
        
        else:
            self.labelLoginFail.pack()
                  
class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self, width=600, height=300)
        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class OffensesWithoutCase():

    def __init__(self, mainClass):
        self.font = "Verdana 16"
        self.frame = ScrollableFrame(root)
        self.frame.pack()
        
        self.windowCreateCaseInstanz = CreateCase(mainClass)
      
        row = 0
        for offenseId in mainClass.offensesWithCase:
            if mainClass.offensesWithCase[offenseId] == False:
                self.OffenseLabel = Label(self.frame.scrollable_frame, text = "Die Offense " + str(offenseId) + " hat keinen Vorgang", font = self.font)
                self.OffenseLabel.grid(row=row, column = 0)
                createCaseButton = Button(self.frame.scrollable_frame, text = "Case anlegen", font = self.font)
                createCaseButton['command'] = partial(self.windowCreateCaseInstanz.create_open_case, mainClass, offenseId, createCaseButton, row)
                createCaseButton.grid(row=row, column = 1)
                row = row + 1

    def case_angelegt(self, row):
        self.CreatedCaseLabel = Label(self.frame.scrollable_frame, text ="Vorgang angelegt", bg ="green", font = self.font)
        self.CreatedCaseLabel.grid(row=row, column=1)
        
                
class CreateCase():

    def __init__(self, mainClass):
        self.font = "Verdana 10"
        self.frame = ScrollableFrame2(root)
    
    def create_open_case(self, mainClass, offenseId, caseAnlegenButton, rowInOffensesWithoutCase):
        self.caseInfoLabel = Label(self.frame.scrollable_frame, font = self.font)
        self.ConfirmCreateCaseButton = Button(self.frame.scrollable_frame, text ="Vorgang anlegen bestätigen", font = self.font)
        self.frame.pack()
        
        offenseObject = mainClass.get_offense_object(offenseId)
        self.caseInfoLabel['text'] = "Vorgang zu Offense " + str(offenseObject.id) + " anlegen:"
        self.caseInfoLabel.grid(row=0,column=0)
        
        
        #Dieses Dictionary enthält {JiraFeldNameInKlartext:FeldmitInhaltDazu}
        fieldNameToButtonDictionary = {}
        row=1
        for jiraFieldName in mapping.mapping:
            value = self.create_open_case_line(jiraFieldName, row, getattr(offenseObject, str(mapping.mapping[jiraFieldName][0]), "Kein Inhalt"))
            fieldNameToButtonDictionary.update({jiraFieldName:value})
            fieldNameToButtonDictionary[jiraFieldName].grid(row=row, column=1)
            row = row+1

        self.ConfirmCreateCaseButton.grid(row=row, column=0)
        self.ConfirmCreateCaseButton['command'] = lambda: self.case_bestaetigen(mainClass, fieldNameToButtonDictionary, caseAnlegenButton)
        
        #Hier wird zwischen ein- und mehrzeilig unterschieden
    def create_open_case_line(self, jiraFieldName, row, offenseFieldContent):  
        if mapping.mapping[jiraFieldName][1] == "einzeilig":
            self.labelJiraFieldName = Label(self.frame.scrollable_frame, font = self.font, text = str(jiraFieldName))
            self.labelJiraFieldName.grid(row=row, column=0)
            self.entryField = Entry(self.frame.scrollable_frame, font = self.font, width = 35)
            self.entryField.insert(END, offenseFieldContent)
            
        if mapping.mapping[jiraFieldName][1] == "mehrzeilig":
            self.labelJiraFieldName = Label(self.frame.scrollable_frame, font = self.font, text = str(jiraFieldName))
            self.labelJiraFieldName.grid(row=row, column=0)
            self.entryField = Text(self.frame.scrollable_frame, font = self.font, height = 10, width = 35)
            self.entryField.insert(END, offenseFieldContent)
            
        else:
            pass
        return self.entryField
    
    def case_bestaetigen(self, mainClass, fieldNameToButtonDictionary, CreateCaseButton):
        dictionaryforCreateCase = {}
        for key in fieldNameToButtonDictionary:
            try:
                value = str(fieldNameToButtonDictionary[key].get('1.0', END))
                dictionaryforCreateCase.update({key:value})
            except:
                value = str(fieldNameToButtonDictionary[key].get())
                dictionaryforCreateCase.update({key:value})                
            
        mainClass.create_case(dictionaryforCreateCase)
        CreateCaseButton.destroy()
        self.frame.destroy()
        self.frame = ScrollableFrame(root)
        
login = login()

root.mainloop()