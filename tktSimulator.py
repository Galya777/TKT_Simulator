import tkinter as tk
from tkinter import messagebox
import random
import PyPDF2
import re
import time

# ==== НАСТРОЙКИ ====
NUM_QUESTIONS = 20
PDF_FILE = "aDanceWithFire.pdf"  # смени с твоя файл

MODE_MULTIPLE = "Multiple Choice"
MODE_INPUT = "Свободен отговор"
TYPE_TRAINING = "Training"
TYPE_MOCK = "Mock"

# ==== ФУНКЦИИ ====

def extract_questions_from_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return extract_questions_from_text(full_text)



def extract_questions_from_text(text):
    lines = text.splitlines()
    questions = []
    current_question_lines = []
    current_answer_lines = []
    reading_answer = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Начало на нов въпрос
        if line.startswith("Въпрос "):
            # Ако имаме предишен въпрос и отговор — запазваме
            if current_question_lines and current_answer_lines:
                question = "\n".join(current_question_lines).strip()
                answer = "\n".join(current_answer_lines).strip()
                questions.append((question, answer))

            # Нова инициализация
            question_match = re.match(r'^Въпрос \d+:?\s*(.*)$', line)
            current_question_lines = []
            if question_match:
                current_question_lines.append(question_match.group(1).strip())
            else:
                current_question_lines.append(line.strip())

            current_answer_lines = []
            reading_answer = False
            continue

        # Начало на отговор
        if line.startswith("Отговор"):
            reading_answer = True
            answer_part = line[len("Отговор"):].lstrip(": ").strip()
            if answer_part:
                current_answer_lines.append(answer_part)
            continue

        if reading_answer:
            current_answer_lines.append(line)
        else:
            current_question_lines.append(line)

    # Добавяне на последния въпрос и отговор
    if current_question_lines and current_answer_lines:
        question = "\n".join(current_question_lines).strip()
        answer = "\n".join(current_answer_lines).strip()
        questions.append((question, answer))

    return questions






# ==== UI КЛАС ====
class QuizApp:
    def __init__(self, root, questions):
        self.root = root
        self.root.title("TKT Simulator")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2f")

        self.all_questions = questions
        self.questions = random.sample(questions, min(NUM_QUESTIONS, len(questions)))
        self.index = 0
        self.score = 0
        self.user_answers = []

        self.mode = tk.StringVar(value=MODE_MULTIPLE)
        self.test_type = tk.StringVar(value=TYPE_TRAINING)
        self.username = tk.StringVar()

        self.start_time = None

        self.setup_ui()

    def setup_ui(self):
        self.clear()

        title_font = ("Segoe UI", 24, "bold")
        label_font = ("Segoe UI", 12)
        btn_font = ("Segoe UI", 12, "bold")

        tk.Label(self.root, text="🚀 Добре дошли в TKT Simulator!", font=title_font, bg="#1e1e2f", fg="#61dafb").pack(pady=20)

        tk.Label(self.root, text="Въведи име:", font=label_font, bg="#1e1e2f", fg="white").pack(pady=(10,0))
        tk.Entry(self.root, textvariable=self.username, font=label_font, width=30).pack()

        tk.Label(self.root, text="Избери режим:", font=label_font, bg="#1e1e2f", fg="white").pack(pady=(20, 0))
        modes_frame = tk.Frame(self.root, bg="#1e1e2f")
        modes_frame.pack()
        tk.Radiobutton(modes_frame, text=MODE_MULTIPLE, variable=self.mode, value=MODE_MULTIPLE, font=label_font, bg="#1e1e2f", fg="white", selectcolor="#282c34", activebackground="#282c34").pack(side="left", padx=10)
        tk.Radiobutton(modes_frame, text=MODE_INPUT, variable=self.mode, value=MODE_INPUT, font=label_font, bg="#1e1e2f", fg="white", selectcolor="#282c34", activebackground="#282c34").pack(side="left", padx=10)

        tk.Label(self.root, text="Тип тест:", font=label_font, bg="#1e1e2f", fg="white").pack(pady=(20, 0))
        type_frame = tk.Frame(self.root, bg="#1e1e2f")
        type_frame.pack()
        tk.Radiobutton(type_frame, text=TYPE_TRAINING, variable=self.test_type, value=TYPE_TRAINING, font=label_font, bg="#1e1e2f", fg="white", selectcolor="#282c34", activebackground="#282c34").pack(side="left", padx=10)
        tk.Radiobutton(type_frame, text=TYPE_MOCK, variable=self.test_type, value=TYPE_MOCK, font=label_font, bg="#1e1e2f", fg="white", selectcolor="#282c34", activebackground="#282c34").pack(side="left", padx=10)

        start_btn = tk.Button(self.root, text="🚀 Стартирай теста", font=btn_font, bg="#61dafb", fg="#1e1e2f", activebackground="#21a1f1", activeforeground="white", command=self.start_test)
        start_btn.pack(pady=40, ipadx=10, ipady=5)

    def start_test(self):
        if not self.username.get().strip():
            messagebox.showwarning("Внимание", "Моля, въведете име!")
            return

        self.index = 0
        self.score = 0
        self.user_answers = []
        self.start_time = time.time()
        self.show_question()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_question(self):
        self.clear()

        if self.index >= len(self.questions):
            self.show_result()
            return

        question, correct_answer = self.questions[self.index]
        bg_color = "#1e1e2f"
        fg_color = "white"
        btn_bg = "#3b3f58"

        # Създаваме Canvas и Scrollbar
        canvas = tk.Canvas(self.root, bg=bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Заглавие и въпрос
        tk.Label(scrollable_frame, text=f"Въпрос {self.index + 1}/{len(self.questions)}",
                 font=("Segoe UI", 16, "bold"), bg=bg_color, fg="#61dafb").pack(pady=15)

        question_label = tk.Label(scrollable_frame, text=question.strip(), wraplength=750,
                                  font=("Segoe UI", 14), bg=bg_color, fg=fg_color, justify="center")
        question_label.pack(pady=10)

        # Изходен бутон
        exit_btn_top = tk.Button(scrollable_frame, text="❌ Изход", font=("Segoe UI", 10, "bold"),
                                 bg="#f44336", fg="white", command=self.setup_ui)
        exit_btn_top.pack(anchor="ne", padx=10, pady=5)

        if self.mode.get() == MODE_MULTIPLE:
            options = [correct_answer]
            while len(options) < 4:
                opt = random.choice(self.all_questions)[1]
                if opt not in options:
                    options.append(opt)
            random.shuffle(options)

            self.buttons = []

            for opt in options:
                btn = tk.Button(scrollable_frame, text=opt, width=80, wraplength=600, bg=btn_bg, fg="white",
                                font=("Segoe UI", 12), relief="raised", anchor="center",
                                command=lambda opt=opt: self.check_mc_answer(opt))
                btn.pack(pady=5)
                self.buttons.append((btn, opt))

            self.feedback = tk.Label(scrollable_frame, text="", font=("Segoe UI", 12, "bold"), bg=bg_color)
            self.feedback.pack(pady=10)

            nav_frame = tk.Frame(scrollable_frame, bg=bg_color)
            nav_frame.pack(pady=10)
            next_btn = tk.Button(nav_frame, text="➡️ Напред", font=("Segoe UI", 12, "bold"),
                                 bg="#61dafb", fg=bg_color, command=self.next_question, state="disabled", width=10)
            next_btn.pack(side="left")

            exit_btn = tk.Button(nav_frame, text="❌ Изход", font=("Segoe UI", 12, "bold"),
                                 bg="#f44336", fg="white", command=self.setup_ui, width=10)
            exit_btn.pack(side="left", padx=15)

            self.next_btn = next_btn

        else:  # режим свободен отговор
            self.answer_entry = tk.Text(scrollable_frame, width=80, height=8, font=("Segoe UI", 12))
            self.answer_entry.pack(pady=10)

            btn_frame = tk.Frame(scrollable_frame, bg=bg_color)
            btn_frame.pack(pady=10)

            check_btn = tk.Button(btn_frame, text="✅ Потвърди отговор", font=("Segoe UI", 12, "bold"), bg="#61dafb",
                                  fg=bg_color, command=lambda: self.check_input_answer(correct_answer))
            check_btn.pack(side="left", padx=10)

            skip_btn = tk.Button(btn_frame, text="⏭️ Пропусни", font=("Segoe UI", 12, "bold"), bg="#3b3f58",
                                 fg="white", command=self.next_question)
            skip_btn.pack(side="left", padx=10)

            exit_btn = tk.Button(btn_frame, text="❌ Изход", font=("Segoe UI", 12, "bold"), bg="#f44336", fg="white",
                                 command=self.setup_ui)
            exit_btn.pack(side="left", padx=10)

            self.feedback = tk.Label(scrollable_frame, text="", font=("Segoe UI", 12, "bold"), bg=bg_color)
            self.feedback.pack(pady=10)

    def check_mc_answer(self, selected):
        question, correct_answer = self.questions[self.index]

        def is_example_question(q):
            keywords = ["пример", "Пример", "пример на", "Примери"]
            return any(k in q for k in keywords)

        corrects = [s.strip() for s in re.split(r'[•,\n]', correct_answer) if s.strip()]
        selected_clean = selected.strip().lower()

        if is_example_question(question):
            is_correct = any(sel in selected_clean for sel in [c.lower() for c in corrects])
        else:
            is_correct = selected.strip().lower() == correct_answer.strip().lower()

        for btn, opt in self.buttons:
            btn.config(state="disabled")
            if opt == selected:
                if is_correct:
                    btn.config(bg="#4CAF50")
                else:
                    btn.config(bg="#f44336")
            elif opt == correct_answer:
                btn.config(bg="#4CAF50")

        if is_correct:
            self.score += 1
            self.feedback.config(text="✅ Верен отговор!", fg="#4CAF50")
        else:
            self.feedback.config(text=f"❌ Грешен отговор! Верният е:\n{correct_answer}", fg="#f44336")

        self.user_answers.append((question, selected, is_correct))
        self.next_btn.config(state="normal")

    def check_input_answer(self, correct_answer):
        user_ans = self.answer_entry.get("1.0", "end").strip().lower()
        correct_answer_clean = correct_answer.strip().lower()

        def is_example_question(q):
            keywords = ["пример", "Пример", "пример на", "Примери"]
            return any(k in q for k in keywords)

        corrects = [s.strip().lower() for s in re.split(r'[•,\n]', correct_answer) if s.strip()]

        if is_example_question(self.questions[self.index][0]):
            is_correct = any(c in user_ans for c in corrects)
        else:
            is_correct = user_ans == correct_answer_clean

        if is_correct:
            self.score += 1
            self.feedback.config(text="✅ Верен отговор!", fg="#4CAF50")
        else:
            self.feedback.config(text=f"❌ Грешен отговор! Верният е:\n{correct_answer}", fg="#f44336")

        self.user_answers.append((self.questions[self.index][0], user_ans, is_correct))
        self.answer_entry.config(state="disabled")

        next_btn = tk.Button(self.root, text="➡️ Напред", font=("Segoe UI", 12, "bold"), bg="#61dafb", fg="#1e1e2f",
                             command=self.next_question)
        next_btn.pack(pady=10)
        self.next_btn = next_btn

    def next_question(self):
        self.index += 1
        self.show_question()

    def show_result(self):
        self.clear()
        total = len(self.questions)
        time_taken = time.time() - self.start_time
        minutes = int(time_taken // 60)
        seconds = int(time_taken % 60)

        bg_color = "#1e1e2f"
        fg_color = "#61dafb"
        self.root.configure(bg=bg_color)

        tk.Label(self.root, text=f"🎉 Тестът завърши, {self.username.get()}!", font=("Segoe UI", 22, "bold"), bg=bg_color, fg=fg_color).pack(pady=20)
        tk.Label(self.root, text=f"Точки: {self.score} от {total}", font=("Segoe UI", 18), bg=bg_color,
                 fg="white").pack(pady=10)

        # Добавяме съобщение в зависимост от резултата
        if self.score >= 14:
            tk.Label(self.root, text="Преминахте успешно теста!", font=("Segoe UI", 16), bg=bg_color,
                     fg="lightgreen").pack(pady=5)
        else:
            tk.Label(self.root, text="Слаб 2. Пробвай пак!", font=("Segoe UI", 16), bg=bg_color, fg="red").pack(pady=5)

        tk.Label(self.root, text=f"Време: {minutes} мин. и {seconds} сек.", font=("Segoe UI", 16), bg=bg_color, fg="white").pack(pady=10)

        btn_frame = tk.Frame(self.root, bg=bg_color)
        btn_frame.pack(pady=30)

        retry_btn = tk.Button(btn_frame, text="🔄 Опитай отново", font=("Segoe UI", 14, "bold"), bg="#61dafb", fg=bg_color, command=self.restart)
        retry_btn.pack(side="left", padx=15, ipadx=10, ipady=5)

        exit_btn = tk.Button(btn_frame, text="❌ Изход", font=("Segoe UI", 14, "bold"), bg="#f44336", fg="white", command=self.setup_ui)
        exit_btn.pack(side="left", padx=15, ipadx=10, ipady=5)

    def restart(self):
        self.questions = random.sample(self.all_questions, min(NUM_QUESTIONS, len(self.all_questions)))
        self.index = 0
        self.score = 0
        self.user_answers = []
        self.start_time = None
        self.setup_ui()


# ==== ГЛАВНА ====

def main():
    try:
        questions = extract_questions_from_pdf(PDF_FILE)
    except Exception as e:
        print(f"Грешка при зареждане на PDF: {e}")
        questions = []

    if not questions:
        print("Няма намерени въпроси в PDF-а или файлът не е открит.")
        return

    root = tk.Tk()
    app = QuizApp(root, questions)
    root.mainloop()


if __name__ == "__main__":
    main()
