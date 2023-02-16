from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtCore import Qt

from CustomMain import TableWidget,Ui # 匯入自訂類別

from MdToEpub import MdToEpub
import os

class Ui2(Ui):
    def init():
        self.setting=None

    def set_value_to_all_input(self,setting_dict):
        #print(setting_dict)
        self.txt_fileName.setText(setting_dict['fileName'])
        self.txt_bookName.setText(setting_dict['bookName'])
        self.txt_author.setText(setting_dict['author'])
        self.txt_EBOOK_ENGINE.setText(setting_dict['EBOOK_ENGINE'])
        self.txt_SOURCE_DIR_ROOT.setText(setting_dict['SOURCE_DIR_ROOT'])
        self.txt_TEMP_DIR_ROOT.setText(setting_dict['TEMP_DIR_ROOT'])
        self.txt_RESULT_DIR_ROOT.setText(setting_dict['RESULT_DIR_ROOT'])
        self.txt_EPUB_DIR_ROOT.setText(setting_dict['EPUB_DIR_ROOT'])
        self.txt_IMAGES_DIR_ROOT.setText(setting_dict['IMAGES_DIR_ROOT'])
        self.txt_CSS_LOC.setText(setting_dict['CSS_LOC'])
        self.txt_ncx_fname.setText(setting_dict['ncx_fname'])
        self.txt_opf_fname.setText(setting_dict['opf_fname'])


    def read_book_dict(self,book_dict_url):
        if not os.path.exists(book_dict_url): #找不到 setting file
            cwd = os.getcwd()
            cwd=cwd.replace("\\",'\\\\')
            tmp_dict={}
            tmp_dict['fileName'] = "md2epub使用教學.md"
            tmp_dict['bookName'] = "md2epub使用教學"
            tmp_dict['author'] = "Your Name"
            tmp_dict['EBOOK_ENGINE'] = "C:\\Calibre2\\ebook-convert.exe"
            tmp_dict['SOURCE_DIR_ROOT'] = cwd+r"\\SOURCE\\"
            tmp_dict['TEMP_DIR_ROOT'] = cwd+r"\\TEMP\\"
            tmp_dict['RESULT_DIR_ROOT'] = cwd+r"\\RESULT\\"
            tmp_dict['EPUB_DIR_ROOT'] = cwd+r"\\EPUB\\"
            tmp_dict['IMAGES_DIR_ROOT'] = cwd+r"\\SOURCE\\images\\"
            tmp_dict['CSS_LOC'] = cwd+r"\\stylesheet.css"
            tmp_dict['ncx_fname'] = "toc.ncx"
            tmp_dict['opf_fname'] = "book-metadata.opf"
            #print(tmp_dict)
            write_str="fileName	"+(tmp_dict['fileName'])+"\nbookName	"+(tmp_dict['bookName'])+"\nauthor	"+(tmp_dict['author'])+"\nEBOOK_ENGINE	"+(tmp_dict['EBOOK_ENGINE'])+"\nSOURCE_DIR_ROOT	"+(tmp_dict['SOURCE_DIR_ROOT'])+"\nTEMP_DIR_ROOT	"+(tmp_dict['TEMP_DIR_ROOT'])+"\nRESULT_DIR_ROOT	"+(tmp_dict['RESULT_DIR_ROOT'])+"\nEPUB_DIR_ROOT	"+(tmp_dict['EPUB_DIR_ROOT'])+"\nIMAGES_DIR_ROOT	"+(tmp_dict['IMAGES_DIR_ROOT'])+"\nCSS_LOC	"+(tmp_dict['CSS_LOC'])+"\nncx_fname	"+(tmp_dict['ncx_fname'])+"\nopf_fname	"+(tmp_dict['opf_fname'])+"\n"
            with open(book_dict_url,'w+',encoding='utf-8') as f:
                f.write(write_str)
            return tmp_dict
        else:
            return dict([i.replace('\n','').replace('\\\\','\\').split('\t') for i in open(book_dict_url,'r',encoding='utf-8').readlines() if i!='\n'])

    def save_setting_to_csv(self,csv_file):
        fileName=(self.txt_fileName.text())
        bookName=(self.txt_bookName.text())
        author=(self.txt_author.text())
        EBOOK_ENGINE=(self.txt_EBOOK_ENGINE.text().replace("\\","\\\\"))
        SOURCE_DIR_ROOT=(self.txt_SOURCE_DIR_ROOT.text().replace("\\","\\\\"))
        TEMP_DIR_ROOT=(self.txt_TEMP_DIR_ROOT.text().replace("\\","\\\\"))
        RESULT_DIR_ROOT=(self.txt_RESULT_DIR_ROOT.text().replace("\\","\\\\"))
        EPUB_DIR_ROOT=(self.txt_EPUB_DIR_ROOT.text().replace("\\","\\\\"))
        IMAGES_DIR_ROOT=(self.txt_IMAGES_DIR_ROOT.text().replace("\\","\\\\"))
        CSS_LOC=(self.txt_CSS_LOC.text().replace("\\","\\\\"))
        ncx_fname=(self.txt_ncx_fname.text())
        opf_fname=(self.txt_opf_fname.text())
        tmp_txt="fileName	%s\nbookName	%s\nauthor	%s\nEBOOK_ENGINE	%s\nSOURCE_DIR_ROOT	%s\nTEMP_DIR_ROOT	%s\nRESULT_DIR_ROOT	%s\nEPUB_DIR_ROOT	%s\nIMAGES_DIR_ROOT	%s\nCSS_LOC	%s\nncx_fname	%s\nopf_fname	%s\n"%(fileName,bookName,author,EBOOK_ENGINE,SOURCE_DIR_ROOT,TEMP_DIR_ROOT,RESULT_DIR_ROOT,EPUB_DIR_ROOT,IMAGES_DIR_ROOT,CSS_LOC,ncx_fname,opf_fname)
        #print(tmp_txt)
        with open(csv_file,"w+",encoding="utf-8") as f:
            f.write(tmp_txt)
        return True

    def on_go_clicked(self):
        #self.qlFreeText.setText("hello")
        # save setting.csv first, and then do convert( aa.main() )
        if self.save_setting_to_csv(self.setting_file_path):
            aa=MdToEpub()
            aa.main()
            alert = QtWidgets.QMessageBox()
            alert.setText("轉檔成功!")
            alert.exec()
