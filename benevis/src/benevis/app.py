"""
Easy Dictation
"""
import json
import os
from threading import Thread

import sounddevice as sd
import toga
import vosk
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class Benevis(toga.App):

    def run_later(self, *args):
        self._impl.loop.call_soon_threadsafe(*args)

    def listen(self):
        dir = os.path.dirname(__file__)
        model = vosk.Model(os.path.join(dir, self.modelname))
        self.rec = vosk.KaldiRecognizer(model, self.samplerate)

        self.stream = sd.RawInputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            device=self.device,
            dtype='int16',
            channels=1,
            callback=self.callback
        )

        self.stream.start()
        self.run_later(self.enable_stop_button)

    def enable_stop_button(self):
        self.btn_stop.enabled = True

    def start(self, widget):
        widget.enabled = False

        if self.stream:
            self.stream.start()
            self.enable_stop_button()
        else:
            Thread(target=self.listen).start()

    def stop(self, widget):
        widget.enabled = False
        self.btn_start.enabled = True
        self.stream.stop()

    def update(self, result, partial=True):
        value = self.multiline_input.value.removesuffix(self.partial)
        self.partial = result if partial else ""
        self.multiline_input.value = value + result

    def callback(self, indata, frame_count, time_info, status):
        if self.rec.AcceptWaveform(bytes(indata)):
            partial = False
            result = self.rec.Result()
            text = json.loads(result)["text"]
        else:
            partial = True
            result = self.rec.PartialResult()
            text = json.loads(result)["partial"]
        if text:
            self.run_later(self.update, f"{text} ", partial)

    def startup(self):
        self.partial = ""
        self.device = None
        self.stream = None
        self.blocksize = 8000
        self.samplerate = 16000
        self.modelname = "resources/models/vosk-model-small-en-us-0.15"

        self.main_window = toga.MainWindow(title=self.name)

        self.btn_start = toga.Button(
            "Start", on_press=self.start,
            style=Pack(flex=1)
        )

        self.btn_stop = toga.Button(
            "Stop", on_press=self.stop,
            style=Pack(flex=1),
            enabled=False
        )

        self.multiline_input = toga.MultilineTextInput(style=Pack(flex=1))

        btn_box = toga.Box(
            children=[
                self.btn_start,
                self.btn_stop
            ],
            style=Pack(
                direction=ROW,
                padding=0
            )
        )

        outer_box = toga.Box(
            children=[
                btn_box,
                self.multiline_input],
            style=Pack(
                direction=COLUMN,
                padding=0
            )
        )

        self.main_window.content = outer_box
        self.main_window.show()


def main():
    return Benevis()
