#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 43):
#
# Github Co-pilot & <jens@bennerhq.com> wrote this file.  As long as you 
# retain this notice you can do whatever you want with this stuff. If we meet 
# some day, and you think this stuff is worth it, you can buy me a beer in 
# return.   
# 
# /benner
# ----------------------------------------------------------------------------

import sys
import os
import yaml
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QTime, QDateTime, QPoint, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QGuiApplication

# Function to load configuration from YAML file
default_config = {
    'hour_mark_color': '#000000',
    'minute_mark_color': '#000000',
    'second_hand_color': '#FF0000',
    'hour_hand_color': '#000000',
    'minute_hand_color': '#000000',
    'dial_color': '#FFFFFF00',
    'date_background_color': "#000000",
    'date_color': "#FFFFFF",
    'window': {
        'x': -200,
        'y': -200,
        'width': 200,
        'height': 200
    }
}

def get_color(config, key: str) -> QColor:
    value = config.get(key, default_config[key])

    try:
        if value.lower() in ["none", "", "transparent"]:
            return QColor(0, 0, 0, 0)

        if len(value) == 9 and value.startswith('#'):
            r = int(value[1:3], 16)
            g = int(value[3:5], 16)
            b = int(value[5:7], 16)
            a = int(value[7:9], 16)
            return QColor(r, g, b, a)

        if value.startswith('rgb(') and value.endswith(')'):
            r, g, b = map(int, value[4:-1].split(','))
            return QColor(r, g, b)

        if value.startswith('rgba(') and value.endswith(')'):
            r, g, b, a = map(int, value[5:-1].split(','))
            return QColor(r, g, b, a)
    except Exception:
        return QColor(0, 0, 0)

    qcolor = QColor(value)
    return qcolor

def load_config(yaml_filename : str) -> dict:
    if os.path.exists(yaml_filename):
        with open(yaml_filename, 'r') as file:
            config = yaml.safe_load(file)
    else:
        config = default_config

    return {
        'hour_mark_color': get_color(config, 'hour_mark_color'),
        'minute_mark_color': get_color(config, 'minute_mark_color'),
        'second_hand_color': get_color(config, 'second_hand_color'),
        'hour_hand_color': get_color(config, 'hour_hand_color'),
        'minute_hand_color': get_color(config, 'minute_hand_color'),
        'dial_color': get_color(config, 'dial_color'),
        'date_background_color': get_color(config, 'date_background_color'),
        'date_color': get_color(config, 'date_color'),
        'window': config.get('window', default_config['window'])
    }

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        if config['second_hand_color'].alpha() != 0:
            self.timer.start(100)  # Update every 100 milliseconds
        else:
            self.timer.start(1000) # Update every second
        self.setMinimumSize(100, 100)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        current_time = QTime.currentTime()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2

        painter.translate(center)
        painter.scale(radius / 100.0, radius / 100.0)

        # Fill background 
        if (config['dial_color'].alpha() != 0):
            painter.setBrush(config['dial_color'])
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-100, -100, 200, 200)

        # Draw hour marks
        if config['hour_mark_color'].alpha() != 0:
            painter.setPen(QPen(config['hour_mark_color'], 2))
            for i in range(12):
                painter.drawLine(88, 0, 96, 0)
                painter.rotate(30)

        # Draw minute marks
        if config['minute_mark_color'].alpha() != 0:
            painter.setPen(QPen(config['minute_mark_color'], 1))
            for i in range(60):
                if i % 5 != 0:
                    painter.drawLine(92, 0, 96, 0)
                painter.rotate(6)

        # Draw hour hand
        if config['hour_hand_color'].alpha() != 0:
            painter.setPen(QPen(config['hour_hand_color'], 6, Qt.SolidLine, Qt.RoundCap))
            painter.save()
            painter.rotate(30 * (current_time.hour() + current_time.minute() / 60.0))
            painter.drawLine(0, 0, 0, -50)
            painter.restore()

        # Draw minute hand
        if config['minute_hand_color'].alpha() != 0:
            painter.setPen(QPen(config['minute_hand_color'], 4, Qt.SolidLine, Qt.RoundCap))
            painter.save()
            painter.rotate(6 * (current_time.minute() + current_time.second() / 60.0))
            painter.drawLine(0, 0, 0, -70)
            painter.restore()

        # Draw second hand if enabled
        if config['second_hand_color'].alpha() != 0:
            painter.setPen(QPen(config['second_hand_color'], 2, Qt.SolidLine, Qt.RoundCap))
            painter.save()
            seconds_with_fraction = current_time.second() + current_time.msec() / 1000.0
            painter.rotate(6 * seconds_with_fraction)
            painter.drawLine(0, 0, 0, -90)
            painter.restore()

        # Draw day number at 15:00 o'clock
        if config['date_background_color'].alpha() != 0:
            today = QDateTime.currentDateTime().toString("dd")
            painter.setPen(Qt.NoPen)
            painter.setBrush(config['date_background_color'])
            painter.save()
            painter.rotate(90)  # Rotate to 15:00 o'clock position
            painter.drawRoundedRect(-10, -100, 20, 20, 5, 5)
            painter.restore()

            painter.setPen(QPen(config['date_color'], 1))
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.save()
            painter.rotate(90)  # Rotate to 15:00 o'clock position
            painter.drawText(QRect(-10, -100, 20, 20), Qt.AlignRight | Qt.AlignTop, today)
            painter.restore()


class ClockWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analog Clock")
        
        screen = QGuiApplication.primaryScreen().geometry()
        window_config = config['window']
        
        x = int(window_config['x'])
        if x < 0:
            x = screen.width() + x
        
        y = int(screen.height());
        if y < 0:
            y = screen.height() + y

        width = int(window_config['width'])
        height = int(window_config['height'])

        self.setGeometry(x, y, width, height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)

        self.central_widget = QWidget()
        self.central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.clock_widget = ClockWidget()
        self.layout.addWidget(self.clock_widget)

        self.old_pos = None
        self.resizing = False
        self.resize_margin = 0

    def is_on_edge(self, pos):
        rect = self.rect()
        return (pos.x() >= rect.width() - self.resize_margin or
                pos.y() >= rect.height() - self.resize_margin)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            if self.is_on_edge(event.pos()):
                self.resizing = True

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            if self.resizing:
                delta = -self.old_pos
                new_width = self.width() + delta.x()
                new_height = self.height() + delta.y()
                self.setGeometry(self.x(), self.y(), new_width, new_height)
            else:
                delta = QPoint(event.globalPos() - self.old_pos)
                self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
            self.resizing = False

    def wheelEvent(self, event):
        dir = -10 if event.angleDelta().y() > 0 else 10
        self.resize(self.width() + dir, self.height() + dir)

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'wclock.yaml'
    config = load_config(config_path)

    app = QApplication(sys.argv)
    win = ClockWindow()
    win.show()
    sys.exit(app.exec_())
