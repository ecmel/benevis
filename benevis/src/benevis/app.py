"""
Easy Dictation
"""
import json
import os

import sounddevice as sd
import toga
import vosk
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from threading import Thread


class Benevis(toga.App):

    def run_later(self, *args):
        self._impl.loop.call_soon_threadsafe(*args)

    def listen(self):
        file_dir = os.path.dirname(__file__)
        model_dir = os.path.join(
            file_dir, "resources/models/vosk-model-small-en-us-0.15")
        model = vosk.Model(model_dir)
        self.rec = vosk.KaldiRecognizer(model, 16000)

        self.stream = sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            device=None,
            dtype='int16',
            channels=1,
            callback=self.callback
        )

        self.stream.start()

    def do_start(self, widget):
        widget.enabled = False
        self.btn_stop.enabled = True
        
        self.partial = ""

        if self.stream:
            self.stream.start()
        else:
            Thread(target=self.listen).start()

    def do_stop(self, widget):
        widget.enabled = False
        self.btn_start.enabled = True
        self.stream.stop()

    def update(self, result, partial=False):
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
        self.stream = {}

        self.main_window = toga.MainWindow(title=self.name)
        self.multiline_input = toga.MultilineTextInput(style=Pack(flex=1))
        
        self.btn_start = toga.Button(
            "Start", on_press=self.do_start, style=Pack(flex=1))
            
        self.btn_stop = toga.Button(
            "Stop", on_press=self.do_stop, style=Pack(flex=1))
        self.btn_stop.enabled = False

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
