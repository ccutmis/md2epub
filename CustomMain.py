from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtCore import Qt

import codecs
import os

class Ui(QtWidgets.QMainWindow):
    def __init__(self,ui_path):
        super(Ui, self).__init__()
        uic.loadUi(ui_path, self)
        self.file_path=""
        self.setting_file_path="resource\\setting.txt"
        self.table_data_all=None

    def open_file(self):
        path = QFileDialog.getOpenFileName(self, "Open")[0]
        if path:
            if self.detect_by_bom(path) == 'utf-8':
                with open(path, 'r', encoding='utf-8') as f:
                    tmp = f.read()
            else: #utf-16
                with open(path,'rb') as f:
                    tmp = f.read()
                tmp = str(tmp, 'utf-16')
            self.file_path = path
            # custom modify here
            # 這裡的 tabWidget 及 tab_2 都是在 .ui 裡面定義的物件，在成功讀取path文件內容後切換到有表格的tab_2
            self.tabWidget.setCurrentWidget(self.tab_2)
            # 接著要把讀取的內容寫入到 QTableWidget 表格裡 
            return ( tmp )
        else:
            return None

    def close_app(self): self.close()

    def detect_by_bom(self,path, default='utf-8'):
        with open(path, 'rb') as f:
            raw = f.read(4)  # will read less if the file is smaller
        for enc, boms in \
                ('utf-8-sig', (codecs.BOM_UTF8,)),\
                ('utf-16', (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)),\
                ('utf-32', (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
            if any(raw.startswith(bom) for bom in boms):
                return enc
        return default 

    def read_setting(self):
        app_current_path = os.getcwd()+'\\'
        self.label_app_loc_val.setText(app_current_path)
        if os.path.exists(self.setting_file_path)==False: # 找不到設定檔
            self.le_temp_dir.setText(app_current_path+'TEMP\\')
            self.temp_dir=app_current_path.replace('\\','\\\\')+'TEMP\\\\'
            self.le_book_name.setText('My_Book')
            self.book_name='My_Book'
            with open(self.setting_file_path,'w+',encoding='utf-8') as f:
                f.write("TEMP_DIR	"+self.temp_dir+"\nBOOK_NAME	"+self.book_name+"\n")
        else:
            if self.detect_by_bom(self.setting_file_path) == 'utf-8':
                with open(self.setting_file_path, 'r', encoding='utf-8') as f:
                    tmp = f.read()
            else: #utf-16
                with open(self.setting_file_path,'rb') as f:
                    tmp = f.read()
                tmp = str(tmp, 'utf-16')
            tmp_ls=tmp.split('\n')
            for i in tmp_ls:
                if i.replace('\n','').replace('\t','').strip()!='':
                    if i.find('TEMP_DIR')!=-1:
                        self.le_temp_dir.setText(i.split('\t')[1].strip().replace("\\\\","\\"))
                        self.temp_dir=i.split('\t')[1].strip()
                    elif i.find('BOOK_NAME')!=-1:
                        self.le_book_name.setText(i.split('\t')[1].strip())
                        self.book_name=i.split('\t')[1].strip()
                    else:
                        pass

    def save_setting(self):
        temp_dir_val=self.le_temp_dir.text().replace("\\","\\\\")
        book_name_val=self.le_book_name.text().replace(" ","_")
        with open(self.setting_file_path,'w+',encoding='utf-8') as f:
            f.writelines("TEMP_DIR	"+temp_dir_val+"\nBOOK_NAME	"+book_name_val+"\n")
        self.temp_dir=temp_dir_val
        self.book_name=book_name_val
        self.show_info_dialog()

class TableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_V and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            selection = self.selectedIndexes()

            if selection:
                row_anchor = selection[0].row()
                column_anchor = selection[0].column()
                clipboard = QApplication.clipboard()
                rows = clipboard.text().split('\n')
                for indx_row, row in enumerate(rows):
                    values = row.split('\t')
                    for indx_col, value in enumerate(values):
                        item = QTableWidgetItem(value)
                        self.setItem(row_anchor + indx_row, column_anchor + indx_col, item)
            super().keyPressEvent(event)

    def clearTableData(self):
        try:
            for row in range(self.rowCount()):
                tmp_col_txt=''
                for col in range(self.columnCount()):
                    self.setItem(row,col, QtWidgets.QTableWidgetItem(''))
            return True
        except:
            return False

    def readTableData(self):
        tmp_all_txt=''
        try:
            for row in range(self.rowCount()):
                tmp_col_txt=''
                for col in range(self.columnCount()):
                    tmp_col_txt+=(self.item(row,col).text())+'\t'
                tmp_col_txt+='\n'
                #print(tmp_col_txt)
                if tmp_col_txt.replace('\t','').replace('\n','').strip()!='':
                    tmp_all_txt+=tmp_col_txt
        except:
            print("READ TABLE DATA FAIL!")
        print(tmp_all_txt)
        if tmp_all_txt!="":
            return tmp_all_txt
        else:
            return None
            #with open('test_table_data','w+',encoding='utf-8') as f:
            #    f.write(tmp_all_txt)


