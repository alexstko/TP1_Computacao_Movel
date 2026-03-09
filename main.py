from dataclasses import field
import flet as ft
from sympy import sympify, N, sqrt, log, sin, pi


@ft.control
class CalcButton(ft.Button):
    expand: int = field(default_factory=lambda: 1)


@ft.control
class DigitButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.WHITE24
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


@ft.control
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self.width = 400
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20

        self.expression_display = ft.Text(
            value="",
            color=ft.Colors.WHITE54,
            size=16,
            text_align=ft.TextAlign.RIGHT,
        )

        self.result = ft.Text(
            value="0",
            color=ft.Colors.WHITE,
            size=40,
            text_align=ft.TextAlign.RIGHT,
        )

        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.expression_display], alignment=ft.MainAxisAlignment.END),
                ft.Row(controls=[self.result], alignment=ft.MainAxisAlignment.END),

                # Linha 1: botões matemáticos extra
                ft.Row(
                    controls=[
                        MathButton(content="√", on_click=self.button_clicked),
                        MathButton(content="xʸ", on_click=self.button_clicked),
                        MathButton(content="sin", on_click=self.button_clicked),
                        MathButton(content="log", on_click=self.button_clicked),
                    ]
                ),

                # Linha 2: AC, CE, ⬅, /
                ft.Row(
                    controls=[
                        ExtraActionButton(content="AC", on_click=self.button_clicked),
                        ExtraActionButton(content="CE", on_click=self.button_clicked),
                        ExtraActionButton(content="⬅", on_click=self.button_clicked),
                        ActionButton(content="/", on_click=self.button_clicked),
                    ]
                ),

                # Linha 3: (, ), %, *
                ft.Row(
                    controls=[
                        ExtraActionButton(content="(", on_click=self.button_clicked),
                        ExtraActionButton(content=")", on_click=self.button_clicked),
                        ExtraActionButton(content="%", on_click=self.button_clicked),
                        ActionButton(content="*", on_click=self.button_clicked),
                    ]
                ),

                # Linha 4
                ft.Row(
                    controls=[
                        DigitButton(content="7", on_click=self.button_clicked),
                        DigitButton(content="8", on_click=self.button_clicked),
                        DigitButton(content="9", on_click=self.button_clicked),
                        ActionButton(content="-", on_click=self.button_clicked),
                    ]
                ),

                # Linha 5
                ft.Row(
                    controls=[
                        DigitButton(content="4", on_click=self.button_clicked),
                        DigitButton(content="5", on_click=self.button_clicked),
                        DigitButton(content="6", on_click=self.button_clicked),
                        ActionButton(content="+", on_click=self.button_clicked),
                    ]
                ),

                # Linha 6
                ft.Row(
                    controls=[
                        DigitButton(content="1", on_click=self.button_clicked),
                        DigitButton(content="2", on_click=self.button_clicked),
                        DigitButton(content="3", on_click=self.button_clicked),
                        ActionButton(content="+/-", on_click=self.button_clicked),
                    ]
                ),

                # Linha 7
                ft.Row(
                    controls=[
                        DigitButton(content="0", expand=2, on_click=self.button_clicked),
                        DigitButton(content=".", on_click=self.button_clicked),
                        ActionButton(content="=", on_click=self.button_clicked),
                    ]
                ),
            ]
        )

    def format_with_thousands(self, value_str):
        """Formata número com espaço como separador de milhares."""
        try:
            num = float(str(value_str).replace(" ", ""))
            if num % 1 == 0:
                num = int(num)
                return "{:,}".format(num).replace(",", " ")
            else:
                formatted = "{:,.10f}".format(num).replace(",", " ").rstrip("0")
                return formatted if "." in formatted else formatted
        except Exception:
            return value_str

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
            if len(raw) > 1:
                self.result.value = self.format_with_thousands(raw[:-1])
            else:
                self.result.value = "0"

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
            if self.result.value == "0":
                self.result.value = data
            else:
                self.result.value = self.result.value + data
            self.new_operand = False

        elif data == "=":
            raw = self.result.value.replace(" ", "")
            full_expression = self.expression + raw
            self.expression_display.value = full_expression + " ="
            result = self.calculate_expression(full_expression)
            self.result.value = self.format_with_thousands(str(result))
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
                self.expression_display.value = f"√({int(raw) if raw % 1 == 0 else raw}) ="
                self.result.value = self.format_with_thousands(str(self.format_number(result)))

        elif data == "xʸ":
            raw = self.result.value.replace(" ", "")
            self.expression = raw + "**"
            self.expression_display.value = f"{raw} ^ "
            self.result.value = "0"
            self.new_operand = True

        elif data == "sin":
            raw = float(self.result.value.replace(" ", ""))
            result = float(N(sin(raw * pi / 180), 10))
            self.expression_display.value = f"sin({int(raw) if raw % 1 == 0 else raw}°) ="
            self.result.value = self.format_with_thousands(str(self.format_number(result)))

        elif data == "log":
            raw = float(self.result.value.replace(" ", ""))
            if raw <= 0:
                self.result.value = "Error"
            else:
                result = float(N(log(raw, 10), 10))
                self.expression_display.value = f"log({int(raw) if raw % 1 == 0 else raw}) ="
                self.result.value = self.format_with_thousands(str(self.format_number(result)))

        self.update()

    def calculate_expression(self, expression):
        try:
            result = N(sympify(expression), 10)
            return self.format_number(float(result))
        except Exception:
            return "Error"

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return round(num, 10)

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True
        self.expression = ""


def main(page: ft.Page):
    page.title = "Calc App"
    calc = CalculatorApp()
    page.add(calc)


ft.app(target=main)