# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 13:37:23 2017

@author: Swopnil Ojha
"""
import numpy as np 
from PyQt4 import QtGui,QtCore
import sys

class section:
    def __init__(self,b,D,d,d_,ast,asc,fck,fy):
        self.b = b
        self.D = D
        self.d = d
        self.d_ = d_
        self.deff = D-d
        self.ast = ast
        self.asc = asc 
        self.fck = fck
        self.fy = fy 
        
    def concrete_stressstrain(self):
        pass
    
    
    def rebar_stressstrain(self,es):
        
        if self.fy == 415:
            x = np.array([0.00000,0.00144,0.00163,0.00192,0.00241,0.00276,0.00380])
            y = np.array([0.0,288.7,306.7,324.8,342.8,351.8,360.9])
            return np.interp(es,x,y)
            
        if self.fy == 500:
            x = np.array([0.00000,0.00174,0.00195,0.00226,0.00277,0.00312,0.00417])
            y = np.array([0.0,347.8,369.6,391.3,413.0,423.9,434.8])
            return np.interp(es,x,y)
            
    def xulim(self):
        return 0.0035/(0.0055+0.87*self.fy/2e05)
        
    def xu(self):
        #for singly reinforced sections 
        if self.asc == 0:
            xu = 0.87*self.fy*self.ast/(0.362*self.fck*self.b)
            xumax = self.xulim()*self.deff
            est = 0.0035*(self.deff/xu-1)
            fst = self.rebar_stressstrain(est)
            if xu<=xumax:
                return xu,fst 
            else:
                xu = (xumax+xu)*0.5
                est = 0.0035*(self.deff/xu-1)
                fst = self.rebar_stressstrain(est)
                xu_new = fst*self.ast/(0.362*self.fck*self.b)
                
                tries = 1
                condition = False
                while abs(xu_new-xu)>=1:
                    xu = (xu_new+xu)*0.5
                    est = 0.0035*(self.deff/xu-1)
                    fst = self.rebar_stressstrain(est)
                    xu_new = fst*self.ast/(0.362*self.fck*self.b)
                    tries = tries + 1 
                    if tries >= 100:
                        condition = True                        
                        break 
                if condition:
                    print("Solution was unable to converge after 100 tries")
                return xu_new,fst
                
        # for doubly reinforced sections     
        else:
            xu = ((0.87*self.fy*self.ast)-(0.87*self.fy-0.447*self.fck)* \
                    self.asc)/(0.362*self.fck*self.b)
            xumax = self.xulim()*self.deff
            esc = 0.0035*(1-self.d_/xu)
            ey = 0.87*self.fy/2e05+0.002
            fsc = self.rebar_stressstrain(esc)
            if xu<=xumax and esc>ey:
                return xu,fsc
            else:
                xu = (xumax+xu)*0.5
                est = 0.0035*(self.deff/xu-1)
                esc = 0.0035*(1-self.d_/xu)
                fst = self.rebar_stressstrain(est)
                fsc = self.rebar_stressstrain(esc)
                xu_new = (fst*self.ast-(fsc-0.447*self.fck)*self.asc)/(0.362*self.fck*self.b)
                
                tries = 1
                condition = False 
                while abs(xu_new-xu)>=1:
                    xu = (xu_new+xu)*0.5
                    est = 0.0035*(self.deff/xu-1)
                    esc = 0.0035*(1-self.d_/xu)
                    fst = self.rebar_stressstrain(est)
                    fsc = self.rebar_stressstrain(esc)
                    xu_new = (fst*self.ast-(fsc-0.447*self.fck)*self.asc)/(0.362*self.fck*self.b)
                    tries = tries+1
                    if tries >= 100:
                        condition = True
                        break
                if condition:
                    print("Solution was unable to converge after 100 tries")
                    
                return xu_new,fsc
        
    def Mur(self):
        xu,fsc = self.xu()
        return 0.362*self.fck*self.b*xu*(self.deff-0.416*xu)+(fsc-0.447*self.fck) \
                    *self.asc*(self.deff-self.d_)
                    
    def Mlim(self):
        xumax = self.xulim()*self.deff
        esc = 0.0035*(1-self.d_/xumax)
        fsc = self.rebar_stressstrain(esc)
        return 0.362*self.fck*self.b*xumax*(self.deff-0.416*xumax)+(fsc-0.447*self.fck) \
                    *self.asc*(self.deff-self.d_)
                    
        
class Interface(QtGui.QWidget):
    
    def __init__(self):
        super(Interface,self).__init__()
        self.initUI()

    def initUI(self):
        Inputlabel = QtGui.QLabel()
        Inputlabel.setText("Input Parameters")
        font = QtGui.QFont()
        font.setBold(True)
        Inputlabel.setFont(font)
        
        b_label  = QtGui.QLabel()
        b_label.setText('Width (mm)')
        self.b_input = QtGui.QLineEdit()
        self.b_input.setText('230')        
        
        D_label = QtGui.QLabel()
        D_label.setText('Total Depth (mm)')
        self.D_input = QtGui.QLineEdit()
        self.D_input.setText('350')
                
        d_label = QtGui.QLabel()
        d_label.setText('Cover to Centroid (bottom) mm')
        self.d_input = QtGui.QLineEdit()
        self.d_input.setText('50')
        
        ddash_label = QtGui.QLabel()
        ddash_label.setText('Cover to Centroid (top) mm')
        self.ddash_input = QtGui.QLineEdit()
        self.ddash_input.setText('50')
        
        ast_label = QtGui.QLabel()
        ast_label.setText('Ast (mm2)')
        self.ast_input = QtGui.QLineEdit()
        self.ast_input.setText('804')
        
        asc_label = QtGui.QLabel()
        asc_label.setText('Asc (mm2)')
        self.asc_input = QtGui.QLineEdit()
        self.asc_input.setText('603')
        
        fck_label = QtGui.QLabel()
        fck_label.setText('fck (mpa)')
        self.fck_input = QtGui.QLineEdit()
        self.fck_input.setText('20')
        
        fy_label = QtGui.QLabel()
        fy_label.setText('fy (mpa)')
        self.fy_input = QtGui.QLineEdit()
        self.fy_input.setText('500')
        
        output_label = QtGui.QLabel()
        output_label.setText('Output')
        output_label.setFont(font)
        
        calculate_button = QtGui.QPushButton('Perform Analysis')
        calculate_button.setFixedWidth(120)
        calculate_button.clicked.connect(self.calculation)
        
        xulim_label = QtGui.QLabel()
        xulim_label.setText('xu max (mm)')
        self.xulim_output = QtGui.QLabel()
                
        xu_label = QtGui.QLabel()
        xu_label.setText('xu (mm)')
        self.xu_output = QtGui.QLabel()
                
        Mulim_label = QtGui.QLabel()
        Mulim_label.setText('Mulim (kNm)')
        self.Mulim_output = QtGui.QLabel()
                
        Mu_label = QtGui.QLabel()
        Mu_label.setText('Mu (kNm)')
        self.Mu_output = QtGui.QLabel()
        
        self.status = QtGui.QLabel() 
           
        
        Grid = QtGui.QGridLayout()
        Grid.addWidget(Inputlabel,0,0)
        Grid.addWidget(b_label,1,0)
        Grid.addWidget(self.b_input,1,1)
        Grid.addWidget(D_label,1,2)
        Grid.addWidget(self.D_input,1,3)
        Grid.addWidget(d_label,1,4)
        Grid.addWidget(self.d_input,1,5)
        Grid.addWidget(ddash_label,1,6)
        Grid.addWidget(self.ddash_input,1,7)
        Grid.addWidget(ast_label,2,0)
        Grid.addWidget(self.ast_input,2,1)
        Grid.addWidget(asc_label,2,2)
        Grid.addWidget(self.asc_input,2,3)
        Grid.addWidget(fck_label,2,4)
        Grid.addWidget(self.fck_input,2,5)
        Grid.addWidget(fy_label,2,6)
        Grid.addWidget(self.fy_input,2,7)
        Grid.addWidget(output_label,3,0)
        Grid.addWidget(calculate_button,3,3)
        Grid.addWidget(xulim_label,4,0)
        Grid.addWidget(self.xulim_output,4,1)
        Grid.addWidget(xu_label,5,0)
        Grid.addWidget(self.xu_output,5,1)
        Grid.addWidget(Mulim_label,6,0)
        Grid.addWidget(self.Mulim_output,6,1)
        Grid.addWidget(Mu_label,7,0)
        Grid.addWidget(self.Mu_output,7,1)
        Grid.addWidget(self.status,3,4)
        
        self.setLayout(Grid)        
        self.setGeometry(300,200,600,150)
        self.setWindowTitle("Section Analyzer")
        
    def calculation(self):
        
        b = eval(self.b_input.text())
        D = eval(self.D_input.text())
        d = eval(self.d_input.text())
        d_ = eval(self.ddash_input.text())
        ast = eval(self.ast_input.text())
        asc = eval(self.asc_input.text())
        fck = eval(self.fck_input.text())
        fy = eval(self.fy_input.text())
        sec = section(b,D,d,d_,ast,asc,fck,fy)
        xulim = sec.xulim()*sec.deff
        xu,_ = sec.xu()
        Mulim = sec.Mlim()/10**6
        Mu = sec.Mur()/10**6
        self.xulim_output.setText(str('{0:.3f}'.format(xulim)))
        self.xu_output.setText(str('{0:.3f}'.format(xu)))
        self.Mulim_output.setText(str('{0:.3f}'.format(Mulim)))
        self.Mu_output.setText(str('{0:.3f}'.format(Mu)))
        font = QtGui.QFont('Times')
        font.setItalic(True)
        font.setPointSize(12)
        palette = QtGui.QPalette()
        
        if xu>xulim:
            self.status.setText('Over-reinforced section')
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
            self.status.setPalette(palette)
            self.status.setFont(font)
            
        elif xu==xulim:
            self.status.setText('Balanced section')
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.yellow)
            self.status.setPalette(palette)
            self.status.setFont(font)
        
        else:
            self.status.setText('Under-reinforced section')
            palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.green)
            self.status.setPalette(palette)
            self.status.setFont(font)
            
        
        
def main():
    app = QtGui.QApplication(sys.argv)
    runas = Interface()
    runas.show()
    sys.exit(app.exec_())
        
        
if __name__=="__main__":
    main()
           
     
