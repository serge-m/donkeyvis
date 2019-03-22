#!/usr/bin/env python
# coding: utf-8

import importlib
import math
import os

import click
import numpy as np
from donkeycar.parts.datastore import TubGroup
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.lines import Line2D

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


def load_model_class(path_model_class):
    module, name = path_model_class.rsplit('.', maxsplit=1)
    module = importlib.import_module(module)
    return getattr(module, name)


class RecordsReader(object):
    def __init__(self, tub_paths):
        tg = TubGroup(tub_paths)
        self.tub = tg.tubs[0]
        self.index = self.tub.get_index(shuffled=False)

    def get_record(self, id_record):
        return self.tub.get_record(id_record)


class ExtendedRecordsReader(object):
    def __init__(self, tub_paths, model):
        self.model = model
        self.reader = RecordsReader(tub_paths)

    def __getitem__(self, idx):
        if idx < 0 or idx > len(self.reader.index):
            raise IndexError
        id_record = self.reader.index[idx]
        record = self.reader.get_record(id_record)
        record['idx'] = idx
        record['frame_idx'] = id_record
        record["pilot/angle"], record["pilot/throttle"] = self.model.run(record["cam/image_array"])
        return record

    def __len__(self):
        return len(self.reader.index)


def plot_arrow(ax, img, length, angle, **arrow_args):
    angle = math.pi / 2 * angle
    h, w = img.shape[0:2]
    scaling = h * 0.45
    dx = scaling * length * np.sin(angle)
    dy = scaling * length * np.cos(angle)
    ax.arrow(w / 2,
             h / 2,
             dx, -dy,
             **arrow_args)


def plot_sample(ax, img, arrows):
    ax.imshow(img)
    arrow_args = dict(alpha=0.7, head_width=2, head_length=5, linewidth=3)
    for name, throttle, angle, display_params in arrows:
        plot_arrow(ax, img, throttle, angle, **arrow_args, **display_params)
    custom_lines = [Line2D([0], [0], **arrow_args)
                    for _, _, _, arrow_args in arrows]
    custome_titles = ["{:>10s} {:>6.2f} {:>6.3f}".format(name, throttle, angle)
                      for name, throttle, angle, _ in arrows]
    ax.legend(custom_lines, custome_titles)


def plot_extended_record(ax, record):
    img = record["cam/image_array"]
    user_angle = float(record["user/angle"])
    user_throttle = float(record["user/throttle"])
    pilot_angle = float(record["pilot/angle"])
    pilot_throttle = float(record["pilot/throttle"])

    plot_sample(ax, img,
                [
                    ('robot', pilot_throttle, pilot_angle, {'color': 'yellow'}),
                    ('human', user_throttle, user_angle, {'color': 'green'})
                    ]
                )


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, reader):
        super().__init__()
        self._reader = reader
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(static_canvas)
        self.addToolBar(NavigationToolbar(static_canvas, self))
        self._static_ax = static_canvas.figure.subplots()

        self.w1 = _build_slider(num_frames=len(reader))
        layout.addWidget(self.w1)

        self.w1.valueChanged.connect(self._update_canvas)

        self._label_idx = QtWidgets.QLabel('00:00:00')
        layout.addWidget(self._label_idx)

    def _update_canvas(self):
        ax = self._static_ax
        ax.clear()

        img_index = self.w1.value()
        record = self._reader[img_index]
        #         print(record)
        #         print(img_index)
        plot_extended_record(ax, record)
        self._label_idx.setText("{} {}".format(record['idx'], record['frame_idx']))
        ax.figure.canvas.draw()


def _build_slider(num_frames):
    slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    slider.setMinimum(0)
    slider.setMaximum(num_frames - 1)
    slider.setValue(0)
    return slider


@click.command()
@click.option('--model', required=True,
              help='Path to model class. For example: donkeycar.parts.keras.KerasLinear',)
@click.option('--snapshot', required=True,
              help='snapshot of the trained model')
@click.option('--tub', required=True,
              help='path to the data to view')
def visualization(model, snapshot, tub):
    Model = load_model_class(model)
    model = Model()
    model.load(os.path.expanduser(snapshot))

    reader = ExtendedRecordsReader(tub, model)

    qapp = QtWidgets.QApplication([])
    app = ApplicationWindow(reader)
    app.show()
    qapp.exec_()
    print("exited")


if __name__ == '__main__':
    visualization()

