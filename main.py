import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel
import re
from transformers import pipeline

# Initialize the pipeline for text classification
pipe = pipeline("text-classification", model="Hate-speech-CNERG/dehatebert-mono-english")


def remove_repeating_symbols(text):
    cleaned_text = re.sub(r'\b[^\w\s]+\b', '', text)
    return cleaned_text


def symbol_detector(text):
    if re.search('[^a-zA-Z0-9\\s,.\'?]', text):
        text = remove_repeating_symbols(text)
        symbol_map = {'0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '@': 'a', '!': 'i',
                      '$': 's', '(': 'c'}
        output_chars = [symbol_map.get(char.lower(), char) for char in list(text)]
        return ''.join(output_chars)
    else:
        return text


def identifier(text):
    results = pipe(text)
    first_result = results[0]
    label = first_result['label']
    score = first_result['score']

    result_text = f"We cannot say that this is hate nor non-hate due to the lack of confidence: {(score * 100):.2f}%"
    if score >= 0.72:
        if label == 'NON_HATE':
            label_text = "Non-Hate"
        else:
            label_text = "Hate Speech"
        result_text = f"Classification: {label_text}\nConfidence: {(score * 100):.2f}%"

    results_display.config(state=tk.NORMAL)
    results_display.delete('1.0', tk.END)
    results_display.insert(tk.INSERT, result_text)
    results_display.config(state=tk.DISABLED)


def analyze_text():
    input_text = text_input.get("1.0", tk.END).strip().lower()
    if not input_text:
        messagebox.showinfo("Invalid Input", "Please input a valid message")
        return
    converted_input = symbol_detector(input_text)
    identifier(converted_input)


def create_report_dialog():
    def submit():
        report_type = var.get()
        if report_type and report_type != "Select type":
            with open("reported_texts.txt", "a") as file:
                file.write(f"Report Type: {report_type}, Reported Text: {text_input.get('1.0', 'end').strip()}\n")
            messagebox.showinfo("Report Submitted", "Thank you for your report.")
            dialog.destroy()
        else:
            messagebox.showerror("Selection Error", "Please select a valid report type")

    dialog = Toplevel(root)
    dialog.title("Report Type")
    var = tk.StringVar(dialog)
    var.set("Select type")  # default value

    options = ["Hate", "Offensive", "Neither"]
    option_menu = OptionMenu(dialog, var, *options)
    option_menu.pack(pady=10, padx=10)

    submit_button = Button(dialog, text="Submit", command=submit)
    submit_button.pack(pady=5)

    dialog.transient(root)  # set to be on top of the main window
    dialog.grab_set()  # modal
    root.wait_window(dialog)


def report_text():
    if not text_input.get("1.0", "end").strip():
        messagebox.showinfo("Invalid Input", "Please input a text to report")
    else:
        create_report_dialog()


# Initialize main window
root = tk.Tk()
root.title("Hate Speech Detector")

text_input_label = tk.Label(root, text="Enter text:")
text_input_label.pack()
text_input = scrolledtext.ScrolledText(root, height=10)
text_input.pack(fill=tk.BOTH, expand=True)

button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X)

submit_button = tk.Button(button_frame, text="Analyze", command=analyze_text)
submit_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

report_button = tk.Button(button_frame, text="Report", command=report_text)
report_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

exit_button = tk.Button(button_frame, text="Exit", command=root.destroy)
exit_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)

results_display = scrolledtext.ScrolledText(root, height=5, state=tk.DISABLED)
results_display.pack(fill=tk.BOTH, expand=True)

root.mainloop()
