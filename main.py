from dataclasses import field
from datetime import datetime
from typing import Callable
import flet as ft
from sympy import sympify, N, sqrt, log, sin, pi
import duckdb

# ── Base de dados DuckDB ──────────────────────────────────────────────────────
DB_PATH = "history.parquet"
DUCK_DB = "history.db"


def init_db():
    con = duckdb.connect(DUCK_DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS history (
            index INTEGER,
            timestamp TEXT,
            expression TEXT,
            result TEXT
        )
    """)
    con.close()


def save_to_db(entries: list):
    con = duckdb.connect(DUCK_DB)
    con.execute("DELETE FROM history")
    for entry in entries:
        con.execute(
            "INSERT INTO history VALUES (?, ?, ?, ?)",
            [entry["index"], entry["timestamp"], entry["expression"], entry["result"]]
        )
    con.execute(f"COPY history TO '{DB_PATH}' (FORMAT PARQUET)")
    con.close()


def load_from_db() -> list:
    con = duckdb.connect(DUCK_DB)
    try:
        rows = con.execute("SELECT * FROM history ORDER BY index DESC").fetchall()
        return [{"index": r[0], "timestamp": r[1], "expression": r[2], "result": r[3]} for r in rows]
    except Exception:
        return []
    finally:
        con.close()


# ── Classe que representa um elemento do histórico ────────────────────────────
@ft.control
class HistoryEntry(ft.Column):
    index: int = 0
    timestamp: str = ""
    expression: str = ""
    result: str = ""
    on_delete: Callable[["HistoryEntry"], None] = field(default=lambda entry: None)

    def __init__(self, index, timestamp, expression, result, on_delete):
        super().__init__()
        self.index = index
        self.timestamp = timestamp
        self.expression = expression
        self.result = result
        self.on_delete = on_delete

        self.controls = [
            ft.Container(
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=10,
                padding=10,
                margin=ft.Margin(0, 0, 0, 6),
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(f"#{self.index}", color=ft.Colors.BLUE_GREY_400, size=12),
                                ft.Text(self.timestamp, color=ft.Colors.BLUE_GREY_400, size=12),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(
                            self.expression + " =",
                            color=ft.Colors.WHITE_54,
                            size=13,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    self.result,
                                    color=ft.Colors.WHITE,
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    expand=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Apagar",
                                    on_click=lambda e: self.on_delete(self),
                                ),
                            ]
                        ),
                    ]
                ),
            )
        ]


# ── Botões ────────────────────────────────────────────────────────────────────
@ft.control
class CalcButton(ft.Button):
    expand: int = field(default_factory=lambda: 1)


@ft.control
class DigitButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.WHITE_24
    color: ft.Colors = ft.Colors.WHITE


@ft.control
class ActionButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.ORANGE
    color: ft.Colors = ft.Colors.WHITE


@ft.control
class ExtraActionButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.BLUE_GREY_100
    color: ft.Colors = ft.Colors.BLACK


@ft.control
class MathButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.BLUE_GREY_700
    color: ft.Colors = ft.Colors.WHITE


# ── App principal ─────────────────────────────────────────────────────────────
@ft.control
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self._history_counter = 0
        self.show_history = False
        self.width = 400
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20

        self.expression_display = ft.Text(
            value="",
            color=ft.Colors.WHITE_54,
            size=16,
            text_align=ft.TextAlign.RIGHT,
        )

        self.result = ft.Text(
            value="0",
            color=ft.Colors.WHITE,
            size=40,
            text_align=ft.TextAlign.RIGHT,
        )

        self.history_list = ft.Column(
            controls=[],
            visible=False,
            scroll=ft.ScrollMode.AUTO,
            height=300,
        )

        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.expression_display], alignment=ft.MainAxisAlignment.END),
                ft.Row(controls=[self.result], alignment=ft.MainAxisAlignment.END),
                ft.Row(
                    controls=[
                        MathButton(content="√", on_click=self.button_clicked),
                        MathButton(content="xʸ", on_click=self.button_clicked),
                        MathButton(content="sin", on_click=self.button_clicked),
                        MathButton(content="log", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(content="AC", on_click=self.button_clicked),
                        ExtraActionButton(content="CE", on_click=self.button_clicked),
                        ExtraActionButton(content="⬅", on_click=self.button_clicked),
                        ActionButton(content="/", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(content="(", on_click=self.button_clicked),
                        ExtraActionButton(content=")", on_click=self.button_clicked),
                        ExtraActionButton(content="%", on_click=self.button_clicked),
                        ActionButton(content="*", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="7", on_click=self.button_clicked),
                        DigitButton(content="8", on_click=self.button_clicked),
                        DigitButton(content="9", on_click=self.button_clicked),
                        ActionButton(content="-", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="4", on_click=self.button_clicked),
                        DigitButton(content="5", on_click=self.button_clicked),
                        DigitButton(content="6", on_click=self.button_clicked),
                        ActionButton(content="+", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="1", on_click=self.button_clicked),
                        DigitButton(content="2", on_click=self.button_clicked),
                        DigitButton(content="3", on_click=self.button_clicked),
                        ActionButton(content="+/-", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="0", expand=2, on_click=self.button_clicked),
                        DigitButton(content=".", on_click=self.button_clicked),
                        ActionButton(content="=", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Button(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.HISTORY, color=ft.Colors.WHITE),
                                    ft.Text("Histórico", color=ft.Colors.WHITE),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            bgcolor=ft.Colors.BLUE_GREY_800,
                            expand=True,
                            on_click=self.toggle_history,
                        )
                    ]
                ),
                self.history_list,
            ]
        )

    def load_history(self, page: ft.Page):
        """Carrega histórico do DuckDB."""
        entries = load_from_db()
        for entry in entries:
            if entry["index"] > self._history_counter:
                self._history_counter = entry["index"]
            item = HistoryEntry(
                index=entry["index"],
                timestamp=entry["timestamp"],
                expression=entry["expression"],
                result=entry["result"],
                on_delete=self.delete_history_entry,
            )
            self.history_list.controls.append(item)

    def save_history(self, page: ft.Page = None):
        """Guarda histórico no DuckDB e exporta para Parquet."""
        entries = []
        for item in self.history_list.controls:
            entries.append({
                "index": item.index,
                "timestamp": item.timestamp,
                "expression": item.expression,
                "result": item.result,
            })
        save_to_db(entries)

    def toggle_history(self, e):
        self.show_history = not self.show_history
        self.history_list.visible = self.show_history
        self.update()

    def add_to_history(self, expression: str, result: str):
        self._history_counter += 1
        entry = HistoryEntry(
            index=self._history_counter,
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            expression=expression,
            result=result,
            on_delete=self.delete_history_entry,
        )
        self.history_list.controls.insert(0, entry)

        if len(self.history_list.controls) > 10:
            self.history_list.controls.pop()

        self.save_history()

    def delete_history_entry(self, entry: HistoryEntry):
        self.history_list.controls.remove(entry)
        self.save_history()
        self.update()

    def format_with_thousands(self, value_str):
        try:
            num = float(str(value_str).replace(" ", ""))
            if num % 1 == 0:
                return "{:,}".format(int(num)).replace(",", " ")
            else:
                formatted = "{:,.10f}".format(num).replace(",", " ").rstrip("0")
                return formatted
        except Exception:
            return value_str

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        return round(num, 10)

    def button_clicked(self, e):
        data = e.control.content

        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.expression_display.value = ""
            self.reset()

        elif data == "CE":
            self.result.value = "0"

        elif data == "⬅":
            raw = self.result.value.replace(" ", "")
            self.result.value = self.format_with_thousands(raw[:-1]) if len(raw) > 1 else "0"

        elif data in ("1","2","3","4","5","6","7","8","9","0","."):
            raw = self.result.value.replace(" ", "")
            if raw == "0" or self.new_operand:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.format_with_thousands(raw + data)

        elif data in ("+", "-", "*", "/"):
            raw = self.result.value.replace(" ", "")
            self.expression = self.expression + raw + " " + data + " "
            self.expression_display.value = self.expression
            self.new_operand = True

        elif data in ("(", ")"):
            self.result.value = data if self.result.value == "0" else self.result.value + data
            self.new_operand = False

        elif data == "=":
            raw = self.result.value.replace(" ", "")
            full_expression = self.expression + raw
            self.expression_display.value = full_expression + " ="
            result = self.calculate_expression(full_expression)
            result_str = self.format_with_thousands(str(result))
            self.add_to_history(full_expression, result_str)
            self.result.value = result_str
            self.reset()

        elif data == "%":
            raw = float(self.result.value.replace(" ", ""))
            self.result.value = self.format_with_thousands(str(self.format_number(raw / 100)))

        elif data == "+/-":
            raw = float(self.result.value.replace(" ", ""))
            if raw > 0:
                self.result.value = "-" + self.result.value
            elif raw < 0:
                self.result.value = self.format_with_thousands(str(self.format_number(abs(raw))))

        elif data == "√":
            raw = float(self.result.value.replace(" ", ""))
            if raw < 0:
                self.result.value = "Error"
            else:
                result = float(N(sqrt(raw), 10))
                expr = f"√({int(raw) if raw % 1 == 0 else raw})"
                result_str = self.format_with_thousands(str(self.format_number(result)))
                self.expression_display.value = expr + " ="
                self.add_to_history(expr, result_str)
                self.result.value = result_str

        elif data == "xʸ":
            raw = self.result.value.replace(" ", "")
            self.expression = raw + "**"
            self.expression_display.value = f"{raw} ^ "
            self.result.value = "0"
            self.new_operand = True

        elif data == "sin":
            raw = float(self.result.value.replace(" ", ""))
            result = float(N(sin(raw * pi / 180), 10))
            expr = f"sin({int(raw) if raw % 1 == 0 else raw}°)"
            result_str = self.format_with_thousands(str(self.format_number(result)))
            self.expression_display.value = expr + " ="
            self.add_to_history(expr, result_str)
            self.result.value = result_str

        elif data == "log":
            raw = float(self.result.value.replace(" ", ""))
            if raw <= 0:
                self.result.value = "Error"
            else:
                result = float(N(log(raw, 10), 10))
                expr = f"log({int(raw) if raw % 1 == 0 else raw})"
                result_str = self.format_with_thousands(str(self.format_number(result)))
                self.expression_display.value = expr + " ="
                self.add_to_history(expr, result_str)
                self.result.value = result_str

        self.update()

    def calculate_expression(self, expression):
        try:
            result = N(sympify(expression), 10)
            return self.format_number(float(result))
        except Exception:
            return "Error"

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True
        self.expression = ""


def main(page: ft.Page):
    page.title = "Calc App"
    init_db()
    calc = CalculatorApp()
    page.add(calc)
    calc.load_history(page)
    calc.update()


ft.run(main)