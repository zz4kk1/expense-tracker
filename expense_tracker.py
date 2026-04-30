import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker | Трекер расходов")
        self.root.geometry("800x550")
        self.expenses = []
        self.json_file = "expenses.json"

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        # --- Панель ввода ---
        input_frame = ttk.LabelFrame(self.root, text="➕ Добавить расход")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=12)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar(value="Еда")
        categories = ["Еда", "Транспорт", "Развлечения", "Жильё", "Здоровье", "Другое"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=categories, width=12)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=12)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(input_frame, text="Добавить", command=self._add_expense).grid(row=0, column=6, padx=10, pady=5)

        # --- Панель фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтр и Расчёт")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_cat_var = tk.StringVar(value="Все")
        self.filter_cat_combo = ttk.Combobox(filter_frame, textvariable=self.filter_cat_var, 
                                             values=["Все"] + categories, width=12)
        self.filter_cat_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="С:").grid(row=0, column=2, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(filter_frame, width=12)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="По:").grid(row=0, column=4, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(filter_frame, width=12)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(filter_frame, text="Применить", command=self._apply_filter).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(filter_frame, text="Сбросить", command=self._reset_filter).grid(row=0, column=7, padx=5, pady=5)

        # --- Таблица ---
        columns = ("date", "amount", "category")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=12)
        self.tree.heading("date", text="Дата")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.column("date", width=180, anchor="center")
        self.tree.column("amount", width=150, anchor="center")
        self.tree.column("category", width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Нижняя панель ---
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=5)

        self.total_label = ttk.Label(bottom_frame, text="Итого: 0.00 ₽", font=("Segoe UI", 11, "bold"))
        self.total_label.pack(side="left")

        ttk.Button(bottom_frame, text=" Сохранить JSON", command=self._save_data).pack(side="right", padx=5)
        ttk.Button(bottom_frame, text="Загрузить JSON", command=self._load_data).pack(side="right", padx=5)

    # --- Валидация ---
    def _validate_input(self, amount_str, date_str):
        try:
            amount = float(amount_str.replace(",", "."))
            if amount <= 0:
                messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом.")
                return None
            datetime.strptime(date_str, "%Y-%m-%d")
            return amount
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Неверный формат.\nСумма: число > 0\nДата: ГГГГ-ММ-ДД")
            return None

    # --- Логика ---
    def _add_expense(self):
        amount = self._validate_input(self.amount_entry.get(), self.date_entry.get())
        if amount is None:
            return

        expense = {
            "date": self.date_entry.get(),
            "amount": amount,
            "category": self.category_var.get()
        }
        self.expenses.append(expense)
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self._refresh_table(self.expenses)
        self._save_data(auto=True)

    def _apply_filter(self):
        cat_filter = self.filter_cat_var.get()
        start_str = self.start_date_entry.get().strip()
        end_str = self.end_date_entry.get().strip()

        try:
            d_start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else None
            d_end = datetime.strptime(end_str, "%Y-%m-%d") if end_str else None
        except ValueError:
            messagebox.showerror("Ошибка фильтра", "Даты в фильтре должны быть в формате ГГГГ-ММ-ДД")
            return

        filtered = []
        for exp in self.expenses:
            exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
            if cat_filter != "Все" and exp["category"] != cat_filter:
                continue
            if d_start and exp_date < d_start:
                continue
            if d_end and exp_date > d_end:
                continue
            filtered.append(exp)

        self._refresh_table(filtered)
        total = sum(e["amount"] for e in filtered)
        self.total_label.config(text=f"Итого за период: {total:,.2f} ₽")

    def _reset_filter(self):
        self.filter_cat_var.set("Все")
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self._refresh_table(self.expenses)
        total = sum(e["amount"] for e in self.expenses)
        self.total_label.config(text=f"Итого: {total:,.2f} ₽")

    def _refresh_table(self, data):
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Сортировка по дате (новые сверху)
        for exp in sorted(data, key=lambda x: x["date"], reverse=True):
            self.tree.insert("", tk.END, values=(exp["date"], f"{exp['amount']:,.2f}", exp["category"]))

    def _save_data(self, auto=False):
        try:
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=2)
            if not auto:
                messagebox.showinfo("Успех", "Данные сохранены в expenses.json")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def _load_data(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
                self._refresh_table(self.expenses)
                total = sum(e["amount"] for e in self.expenses)
                self.total_label.config(text=f"Итого: {total:,.2f} ₽")
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Файл повреждён. Начинаем с чистого листа.")
                self.expenses = []
        else:
            self.expenses = []
            self._refresh_table([])

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
