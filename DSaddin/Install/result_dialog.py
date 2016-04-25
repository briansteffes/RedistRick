import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _tkinter
import Tkinter as tk
import tkMessageBox
import tkFileDialog
import arcpy
from district_stats import DistrictStats
from arcpy import env
import pythonaddins


class RedistrictingResults(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master.title('Redistricting Results')
        self.grid()
        self.configureGrid()
        # if tkMessageBox.askquestion("Redistricting Plan",
        #                             "Continue defining districts?") is False:
        #     self.quit()
        self.district_fc = sys.argv[1]
        self.createWidgets()

    def configureGrid(self):
        top = self.winfo_toplevel()
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.columnconfigure(2, weight=1)
        top.rowconfigure(0, weight=1)
        top.rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

    def createWidgets(self):
        self.diretions = tk.Label(self, justify=tk.LEFT,
                                  text=(
                                    "The results of the redistricting plan "
                                    "you designed can be summarized here.\n"
                                    "Export will allow you to save a new "
                                    "shapefile with polygons\nof these "
                                    "boundaries.\nReport lets you export "
                                    "a CSV file containing summary "
                                    "statistics\nbased on the fields chosen "
                                    "below in the select boxes."
                                  ))
        self.diretions.grid(columnspan=3, sticky=tk.E+tk.W)
        self.buildFieldSelect()
        self.createActionButtons()

    def createActionButtons(self):
        self.actionsFrame = tk.Frame(self)
        self.actionsFrame.grid(columnspan=3)

        self.reportButton = tk.Button(self.actionsFrame, text='Report',
                                      command=self.report, justify=tk.RIGHT)
        self.exportButton = tk.Button(self.actionsFrame, text='Export',
                                      command=self.export, justify=tk.RIGHT)
        self.quitButton = tk.Button(self.actionsFrame, text='Save',
                                    command=self.quit, justify=tk.RIGHT)

        self.reportButton.grid(column=0, row=0, sticky=tk.E+tk.W)
        self.exportButton.grid(column=1, row=0, sticky=tk.E+tk.W)
        self.quitButton.grid(column=2, row=0, sticky=tk.E+tk.W)

    def buildFieldSelect(self):
        self.fieldLabel = tk.Label(self, justify=tk.RIGHT,
                                   text='Field to Summarize:')
        self.fieldLabel.grid(column=1, row=1, sticky=tk.E)

        # TODO read from district_fc instead
        # fieldList = arcpy.ListFields(self.district_fc)
        # print 'fieldList', fieldList
        fieldList = ['Several','Strings','Here']
        self.selectedField = tk.StringVar()
        self.selectedField.set(None)

        self.fieldSelector = tk.OptionMenu(self,
                                           self.selectedField,
                                           *fieldList,
                                           command=self.fieldChange)
        self.fieldSelector.grid(column=2, row=1, sticky=tk.E+tk.W)

    def fieldChange(self, value):
        tkMessageBox.showinfo("You changed stuff.", "Now you say " + value)

    def export(self):
        pythonaddins.GPToolDialog(os.path.join(
                                  os.path.dirname(os.path.abspath(__file__)),
                                  "Redistricting.pyt"),
                                  "Build_Districts_Tool")

    def report(self):
        output_file = tkFileDialog.asksaveasfilename()
        stats = DistrictStats(self.district_fc)
        stats.csv([self.selectedField], output_file)
        tkMessageBox.showinfo("You changed stuff.", 'You clicked Report.')

if __name__ == "__main__":
    app = RedistrictingResults()
    app.mainloop()
