import os
import sys
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QFileDialog
from PyQt5.QtCore import QThread,pyqtSignal
from pip_ui import *

class Pip_Win(QMainWindow):
    def __init__(self):
        super().__init__(None)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(self.width(), self.height())

        self.ui.Btn_Install_page.clicked.connect(lambda :self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.Btn_update_page.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.Btn_clear_page.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.Btn_update_module_page.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))
        self.ui.Btn_r_page.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(5))

        self.ui.Btn_Install.clicked.connect(self.Install_Click)
        self.ui.Btn_update.clicked.connect(self.Update_Click)
        self.ui.Btn_clear.clicked.connect(self.Clear_Click)
        self.ui.Btn_clear_cache.clicked.connect(self.clean_cache)
        self.ui.Btn_show_list.clicked.connect(self.Show_list)
        self.ui.Btn_look_update_list.clicked.connect(self.Look_module)
        self.ui.Btn_file.clicked.connect(self.Load_file_path)
        self.ui.Btn_r_Install.clicked.connect(self.R_Install)

        self.show()

    # 安装模块
    def Install_Click(self):
        if self.ui.line_cmd.text() == "":
            QMessageBox.warning(self,"警告","请输入要安装的模块")
            return
        self.ui.cmd_textEdit.clear()
        self.ui.cmd_textEdit.setLineWrapMode(0)

        self.Cmd_thread(cmd=self.ui.line_cmd.text(), source=self.ui.com_source.currentText(),Edit_object=self.ui.cmd_textEdit, flag="Install")

    def Update_Click(self):
        if self.ui.lineEdit_update.text() == "":
            QMessageBox.warning(self,"警告","请输入要安装的模块")
            return
        self.ui.update_textEdit.clear()
        self.ui.update_textEdit.setLineWrapMode(0)

        self.Cmd_thread(cmd=self.ui.lineEdit_update.text(),source=self.ui.com_sources.currentText(),Edit_object=self.ui.update_textEdit, flag="Update")

    # 删除模块
    def Clear_Click(self):
        if self.ui.line_clear_text.text() == "":
            QMessageBox.warning(self,"警告","请输入要删除的模块")
            return
        self.ui.text_clear_Edit.clear()
        self.ui.text_clear_Edit.setLineWrapMode(0)

        self.Cmd_thread(cmd=self.ui.line_clear_text.text(),Edit_object=self.ui.text_clear_Edit, flag="Delete")

    # 清空缓存
    def clean_cache(self):
        self.Cmd_thread(flag="Cache")
        QMessageBox.information(self,"清空缓存","清除缓存成功")

    # 查看本地安装模块
    def Show_list(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.model_list_text.clear()
        self.ui.model_list_text.setLineWrapMode(0)

        self.Cmd_thread(Edit_object=self.ui.model_list_text,flag="Show")

    # 查看可更新模块
    def Look_module(self):
        self.ui.textEdit_update_module.clear()
        self.ui.textEdit_update_module.setLineWrapMode(0)

        self.Cmd_thread(Edit_object=self.ui.textEdit_update_module,flag="look_update_module")

    # 加载requirement 文件
    def Load_file_path(self):
        r_path = QFileDialog.getOpenFileName(self,"requirement.txt文件")[0]
        if not r_path:
            return

        self.ui.line_r_path.setText(r_path)

    # 安装requirement 依赖包
    def R_Install(self):
        if self.ui.line_r_path == "":
            QMessageBox.information(self,"path","requirement.txt 路径为空")
            return
        self.ui.text_r_edit.setLineWrapMode(0)
        self.ui.text_r_edit.clear()

        self.Cmd_thread(cmd=self.ui.line_r_path.text(),source=self.ui.com_r_source.currentText(),Edit_object=self.ui.text_r_edit,flag="R_Install")

    # 线程调用函数
    def Cmd_thread(self,cmd=None,source=None,Edit_object=None,flag=None):
        try:
            thread = Cmd_thread(cmd,source, flag, self)
            thread.result_text.connect(lambda str: Edit_object.setText(str))
            thread.start()
        except Exception as e:
            QMessageBox.warning(self, "警告", "出现异常错误，请重试")


class Cmd_thread(QThread):
    result_text = pyqtSignal(str)

    def __init__(self,cmd=None,source_text=None,flag=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cmd = cmd
        self.sources_text = source_text
        self.sources = {
            "官方源": "https://pypi.python.org/simple",
            "阿里源": "https://mirrors.aliyun.com/pypi/simple/",
            "清华源": "https://pypi.tuna.tsinghua.edu.cn/simple/"
        }
        self.flag = flag

    def Cmd_Cache(self):
        os.system(r"pip cache purge")

    def PIP_CMD(self,cmd):
        file_object = os.popen(cmd)
        result = file_object.read()
        file_object.close()
        self.result_text.emit(result)

    def run(self):
        match self.flag:
            case "Install":
                # print(r"pip install {0} -i {1}".format(self.cmd,self.sources[self.sources_text]))
                self.PIP_CMD(r"pip install {0} -i {1}".format(self.cmd,self.sources[self.sources_text]))
            case "Update":
                self.PIP_CMD(r"pip install --upgrade {0} -i {1}".format(self.cmd,self.sources[self.sources_text]))
            case "Delete":
                # print(r"pip uninstall -y {0}".format(self.cmd))
                self.PIP_CMD(r"pip uninstall -y {0}".format(self.cmd))
            case "Cache":
                self.Cmd_Cache()
            case "Show":
                self.PIP_CMD(r"pip list")
            case "look_update_module":
                self.PIP_CMD(r"pip list --outdate")
            case "R_Install":
                self.PIP_CMD(r"pip install -r {0} -i {1}".format(self.cmd, self.sources[self.sources_text]))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Pip_Win()
    win.show()
    sys.exit(app.exec_())