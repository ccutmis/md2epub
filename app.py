from CustomAdd import *





if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    with open("resource\\styles.qss") as f:
        app.setStyleSheet(f.read())

    ui_path = "resource\\md2epub_form.ui"
    w = Ui2(ui_path)

    w.setWindowFlags(Qt.WindowType.MSWindowsFixedSizeDialogHint)
    w.statusbar. setSizeGripEnabled(False) # 隱藏狀態列
    w.window_title='Markdown To EPUB 轉換程式'
    w.setWindowTitle(w.window_title)
    w.setting=w.read_book_dict(w.setting_file_path)
    w.set_value_to_all_input(w.setting)
    w.button_go.clicked.connect(w.on_go_clicked)
    w.show()  # show window
    sys.exit(app.exec())
