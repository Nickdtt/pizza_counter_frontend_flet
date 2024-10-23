import flet as ft

from app import PizzaCompetitionApp




def main(page: ft.Page):
    page.title = "Pizza Battle!"
    page.bgcolor = ft.colors.YELLOW_100  # Cor amarelo claro, inspiração do queijo
    page.padding = 20  # Espaçamento geral
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER  # Centralizando horizontalmente
    app = PizzaCompetitionApp()
    page.add(app.build())


ft.app(target=main)



