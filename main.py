import sys
# import os  # Décommenter si nécessaire
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter

from ui.main_window import MainWindow


class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(600, 350)
        pixmap.fill(QColor('#1a1f2e'))
        super().__init__(pixmap)
        self.setWindowOpacity(0.95)
        
        # Dessiner AVANT d'afficher
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Titre principal
        painter.setPen(QColor('#64b5f6'))
        font = QFont('Segoe UI', 22, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "RPA 2024")
        
        # Sous-titre
        font2 = QFont('Segoe UI', 11)
        painter.setFont(font2)
        painter.setPen(QColor('#90a0b7'))
        painter.drawText(pixmap.rect().adjusted(0, 50, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                        "Calcul Parasismique - Moteurs RPA")
        
        # Message de chargement
        painter.setPen(QColor('#4a5568'))
        font3 = QFont('Segoe UI', 9)
        painter.setFont(font3)
        painter.drawText(pixmap.rect().adjusted(0, 80, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                        "Chargement en cours...")
        painter.end()
        
        self.setPixmap(pixmap)
        self.show()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    splash = SplashScreen()
    app.processEvents()

    window = MainWindow()
    QTimer.singleShot(1500, lambda: _finish(splash, window))
    
    sys.exit(app.exec())


def _finish(splash, window):
    window.show()
    splash.finish(window)


if __name__ == '__main__':
    main()