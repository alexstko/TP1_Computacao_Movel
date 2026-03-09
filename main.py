from dataclasses import field
import flet as ft
from sympy import sympify, N


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
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20

        # Campo da expressão (novo - por cima)
        self.expression_display = ft.Text(
            value="",
            color=ft.Colors.WHITE54,
            size=16,
            text_align=ft.TextAlign.RIGHT,
        )

        # Campo do resultado (existente)
        self.result = ft.Text(
            value="0",
            color=ft.Colors.WHITE,
            size=40,
            text_align=ft.TextAlign.RIGHT,
        )

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[self.expression_display],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Row(
                    controls=[self.result],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(content="AC", on_click=self.button_clicked),
                        ExtraActionButton(content="+/-", on_click=self.button_clicked),
                        ExtraActionButton(content="%", on_click=self.button_clicked),
                        ActionButton(content="/", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="7", on_click=self.button_clicked),
                        DigitButton(content="8", on_click=self.button_clicked),
                        DigitButton(content="9", on_click=self.button_clicked),
                        ActionButton(content="*", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="4", on_click=self.button_clicked),
                        DigitButton(content="5", on_click=self.button_clicked),
                        DigitButton(content="6", on_click=self.button_clicked),
                        ActionButton(content="-", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="1", on_click=self.button_clicked),
                        DigitButton(content="2", on_click=self.button_clicked),
                        DigitButton(content="3", on_click=self.button_clicked),
                        ActionButton(content="+", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="0", expand=2, on_click=self.button_clicked),
                        DigitButton(content=".", on_click=self.button_clicked),
                        ActionButton(content="=", on_click=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.content
        print(f"Button clicked with data = {data}")

        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.expression_display.value = ""
            self.reset()

        elif data in ("1","2","3","4","5","6","7","8","9","0","."):
            if self.result.value == "0" or self.new_operand:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        elif data in ("+", "-", "*", "/"):
            # Acumula a expressão
            self.expression = self.expression + str(self.result.value) + " " + data + " "
            self.expression_display.value = self.expression
            self.new_operand = True

        elif data == "=":
            # Monta a expressão completa e calcula com SymPy
            full_expression = self.expression + str(self.result.value)
            self.expression_display.value = full_expression + " ="
            self.result.value = self.calculate_expression(full_expression)
            self.reset()

        elif data == "%":
            if float(self.result.value) != 0:
                self.result.value = str(self.format_number(float(self.result.value) / 100))

        elif data == "+/-":
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)
            elif float(self.result.value) < 0:
                self.result.value = str(self.format_number(abs(float(self.result.value))))

        self.update()

    def calculate_expression(self, expression):
        """Calcula expressão numérica completa usando SymPy (suporta PEMDAS/BODMAS)."""
        try:
            result = N(sympify(expression), 10)  # 10 dígitos de precisão
            return str(self.format_number(float(result)))
        except Exception:
            return "Error"

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            # Arredonda para evitar floats como 0.30000000001
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