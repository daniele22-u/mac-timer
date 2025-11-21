import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer spegnimento Mac")
        self.root.resizable(False, False)

        self.running = False
        self.seconds = 0

        self.minutes_var = tk.IntVar(value=30)
        self.action_var = tk.StringVar(value="shutdown")
        self.status = tk.StringVar(value="Pronto")

        self.build_ui()

    def build_ui(self):
        # stile base
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        main = ttk.Frame(self.root, padding=15)
        main.grid(row=0, column=0, sticky="nsew")

        # titolo
        title_label = ttk.Label(
            main,
            text="Timer spegnimento",
            font=("Helvetica", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # slider minuti
        minutes_label = ttk.Label(main, text="Minuti:")
        minutes_label.grid(row=1, column=0, sticky="w")

        self.minutes_value_label = ttk.Label(main, text="30 min")
        self.minutes_value_label.grid(row=1, column=1, sticky="e")

        minutes_scale = ttk.Scale(
            main,
            from_=1,
            to=240,
            orient="horizontal",
            variable=self.minutes_var,
            command=self.on_scale_change,
        )
        minutes_scale.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 10))

        # azioni (radio button)
        action_label = ttk.Label(main, text="Azione:")
        action_label.grid(row=3, column=0, sticky="w", pady=(5, 0))

        actions_frame = ttk.Frame(main)
        actions_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=(2, 10))

        actions = [
            ("Spegni", "shutdown"),
            ("Riavvia", "restart"),
            ("Sleep", "sleep"),
        ]
        for i, (text, value) in enumerate(actions):
            rb = ttk.Radiobutton(
                actions_frame,
                text=text,
                value=value,
                variable=self.action_var,
            )
            rb.grid(row=0, column=i, padx=5)

        # countdown grande
        self.countdown_label = ttk.Label(
            main,
            text="00:00",
            font=("Helvetica", 20, "bold")
        )
        self.countdown_label.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        # bottoni
        buttons_frame = ttk.Frame(main)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=(0, 5))

        self.start_button = ttk.Button(buttons_frame, text="Start", command=self.start)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(
            buttons_frame, text="Stop", command=self.stop, state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=5)

        # stato
        status_label = ttk.Label(main, textvariable=self.status, foreground="gray")
        status_label.grid(row=7, column=0, columnspan=2, pady=(5, 0))

        # allarga un po' la finestra
        self.root.geometry("320x260")
        self.root.columnconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        # inizializza countdown
        self.update_labels()

    def on_scale_change(self, _event=None):
        # aggiornare etichetta minuti quando muovi lo slider
        value = int(self.minutes_var.get())
        self.minutes_value_label.config(text=f"{value} min")

    def start(self):
        if self.running:
            return

        minutes = int(self.minutes_var.get())
        if minutes <= 0:
            self.status.set("Minuti non validi")
            return

        self.seconds = minutes * 60
        self.running = True
        self.status.set("Timer avviato")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        t = threading.Thread(target=self.run_timer, daemon=True)
        t.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.status.set("Annullato")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def run_timer(self):
        while self.running and self.seconds > 0:
            self.root.after(0, self.update_labels)
            time.sleep(1)
            self.seconds -= 1

        if not self.running:
            return

        # timer finito
        self.root.after(0, self.update_labels)
        self.root.after(0, lambda: self.status.set("Eseguo azione..."))
        self.execute_action()
        self.root.after(0, self.reset_ui)

    def update_labels(self):
        mins = self.seconds // 60
        sec = self.seconds % 60
        self.countdown_label.config(text=f"{mins:02d}:{sec:02d}")

        # aggiorna anche etichetta minuti se il timer non è ancora partito
        if not self.running:
            self.minutes_value_label.config(text=f"{self.minutes_var.get()} min")

    def reset_ui(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status.set("Pronto")

    def execute_action(self):
        action = self.action_var.get()
        if action == "shutdown":
            script = 'tell application "System Events" to shut down'
        elif action == "restart":
            script = 'tell application "System Events" to restart'
        else:
            script = 'tell application "System Events" to sleep'

        subprocess.run(["osascript", "-e", script])


def main():
    root = tk.Tk()
    TimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()