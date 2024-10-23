import flet as ft
import httpx
import asyncio


BASE_URL = "http://localhost:8000"


class PizzaCompetitionApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.competition_id = None
        self.ws = None
        self.competitor_name = None
        self.slices = 0
        self.opponent_slices = 0

    async def create_competition(self, name):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/competition/", json={"name": name})
            if response.status_code == 200:
                self.competition_id = response.json()["id"]
                return True
            return False

    async def register_competitor(self, name):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/competition/{self.competition_id}/register/", json={"name": name})
            return response.json()["message"]

    async def connect_websocket(self):
        self.ws = ft.WebSocket(f"ws://localhost:8000/ws/{self.competition_id}")
        await self.ws.connect()

        async def receive_messages():
            while True:
                message = await self.ws.recv()
                if message:
                    name, slices = message.split(":")
                    self.opponent_slices = int(slices)
                    self.update_scores()

        asyncio.create_task(receive_messages())

    def build(self):
        self.page_title = ft.Text(
            value="Pizza Battle!",
            style="headlineMedium",
            color=ft.colors.RED_ACCENT_700,  
        )
        self.content_area = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,  
            horizontal_alignment=ft.CrossAxisAlignment.CENTER  
        )
        self.change_screen("home")

        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,  
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  
            controls=[
                self.page_title,
                self.content_area
            ]
        )

    def change_screen(self, screen):
        self.content_area.controls.clear()
        if screen == "home":
            self.home_screen()
        elif screen == "competition":
            self.competition_screen()

    def home_screen(self):
        self.competition_name_input = ft.TextField(label="Nome da Competição")
        self.creator_name_input = ft.TextField(label="Seu Nome")  # Nome do criador da competição
        self.create_button = ft.ElevatedButton(
            text="Criar Competição",
            on_click=lambda e: self.create_competition_action(),
            bgcolor=ft.colors.RED_ACCENT_400,  # Botão vermelho chamativo
            color=ft.colors.WHITE  # Texto em branco para contraste
        )
        
        self.competition_id_input = ft.TextField(label="ID da Competição (para entrar)")
        self.enter_name_input = ft.TextField(label="Seu Nome")  # Nome do competidor que vai entrar
        self.enter_button = ft.ElevatedButton(
            text="Entrar em Competição",
            on_click=lambda e: self.enter_competition_action(),
            bgcolor=ft.colors.RED_ACCENT_400,
            color=ft.colors.WHITE
        )
        
        self.output_area = ft.Column()

        
        pizza_image = ft.Image(
            src="https://img.icons8.com/plasticine/2x/pizza.png",  
            width=200,
            height=200
        )

      
        self.content_area.controls.extend([
            pizza_image,  # Imagem de pizza
            self.competition_name_input,
            self.creator_name_input,
            self.create_button,
            self.competition_id_input,
            self.enter_name_input,
            self.enter_button,
            self.output_area
        ])

    async def create_competition_action(self):
        name = self.competition_name_input.value
        self.competitor_name = self.creator_name_input.value
        if await self.create_competition(name):
            await self.register_competitor(self.competitor_name)
            self.output_area.add(ft.Text(f"Competição '{name}' criada com ID: {self.competition_id}"))
            self.change_screen("competition")
            await self.connect_websocket()
        else:
            self.output_area.add(ft.Text("Erro ao criar competição."))

    async def enter_competition_action(self):
        self.competition_id = self.competition_id_input.value
        self.competitor_name = self.enter_name_input.value
        message = await self.register_competitor(self.competitor_name)
        self.output_area.add(ft.Text(message))
        self.change_screen("competition")
        await self.connect_websocket()

    def competition_screen(self):
        self.slices_display = ft.Text(
            f"Suas fatias: {self.slices}",
            style="headlineMedium",
            color=ft.colors.BLACK  # Texto preto para contraste
        )
        self.opponent_display = ft.Text(
            f"Fatias do Oponente: {self.opponent_slices}",
            style="headlineMedium",
            color=ft.colors.BLACK
        )
        self.add_slice_button = ft.ElevatedButton(
            text="+1 Fatia",
            on_click=lambda e: self.add_slice_action(),
            bgcolor=ft.colors.GREEN_ACCENT_700,  # Verde para lembrar o botão de continuar na imagem
            color=ft.colors.WHITE
        )
        
        self.content_area.controls.extend([
            self.slices_display,
            self.opponent_display,
            self.add_slice_button
        ])

    async def add_slice_action(self):
        self.slices += 1
        async with httpx.AsyncClient() as client:
            await client.post(f"{BASE_URL}/competition/{self.competition_id}/increment/", json={"name": self.competitor_name})
        
        self.update_scores()

    def update_scores(self):
        self.slices_display.value = f"Suas fatias: {self.slices}"
        self.opponent_display.value = f"Fatias do Oponente: {self.opponent_slices}"
        self.page.update()