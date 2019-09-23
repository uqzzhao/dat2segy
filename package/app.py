import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen
from package.gui.mainwindow import MainWindow

import time



def run():
    
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/icons/windows/deeplisten-logo.png'))

    # splash screen
    # Create and display the splash screen
    splash_pix = QPixmap(':/icons/windows/start.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # Simulate something that takes time
    time.sleep(1)


    mw = MainWindow()
    mw.show()
    splash.finish(mw)

    ##setup stylesheet
    # import qdarkstyle
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    sys.exit(app.exec_())
    
    

if __name__ == '__app__':
    run()

    
