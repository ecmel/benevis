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


class Benevis(toga.App):

    def do_start(self, widget):
        widget.enabled = False
        self.btn_stop.enabled = True
        self.stream.start()

    def do_stop(self, widget):
        widget.enabled = False
        self.btn_start.enabled = True
        self.stream.stop()

    def update(self, result):
        self.multiline_input.value += result

    def callback(self, indata, frame_count, time_info, status):
        if self.rec.AcceptWaveform(bytes(indata)):
            result = self.rec.Result()
            print(result)
            text = json.loads(result)["text"]
            if text:
                self._impl.loop.call_soon_threadsafe(self.update, f"{text} ")


    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
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
