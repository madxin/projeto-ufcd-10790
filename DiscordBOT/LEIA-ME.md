# src/

Esta pasta contém todo o código fonte Python do projeto,
responsável pelo desenvolvimento de um bot de Discord para gestão de servidores RP,
organizado segundo uma arquitetura em três camadas.

## Estrutura

```
src/ 
│
├── main.py     ← Ponto de entrada — inicializa e executa o bot 
│ 
├── dal/    ← Data Access Layer (Acesso à Base de Dados) 
│   ├── __init__.py 
│   └── [nome]_dal.py ← ex: ticket_dal.py, application_dal.py 
│ 
├── bll/    ← Business Logic Layer (Lógica de Negócio) 
│   ├── __init__.py 
│   └── [nome]_bll.py ← ex: ticket_bll.py, role_bll.py
│
└── ui/ ← Interface com o utilizador (Discord) 
    ├── __init__.py 
    └── commands.py     ← Comandos, botões e interações do Discord
```

## Responsabilidades de cada camada

### `main.py`
Inicializa a aplicação — cria a ligação à BD, instancia o DAL e o BLL,
e arranca a interface. Não deve conter lógica de negócio.

```python
from dal.produto_dal import ProdutoDAL
from bll.produto_bll import ProdutoBLL
from ui.menu import Menu

if __name__ == "__main__":
    dal = ProdutoDAL("database.db")
    bll = ProdutoBLL(dal)
    menu = Menu(bll)
    menu.iniciar()
```

### `dal/`
Responsável pela comunicação com a base de dados SQLite. Cada ficheiro corresponde a uma entidade do sistema, como tickets, candidaturas ou configurações do bot.

```python
# dal/ticket_dal.py
import sqlite3 

class TicketDAL: 
    def __init__(self, db_path):
        self._db = db_path 
    
    def obter_todos(self): 
        conn = sqlite3.connect(self._db) 
        try: cursor = conn.cursor() 
            cursor.execute("SELECT * FROM tickets") 
            return cursor.fetchall() 
        finally: 
            conn.close()
```

### `bll/`
Contém as regras de negócio do sistema. Esta camada processa as operações do bot e delega o acesso aos dados para o DAL.

```python
# bll/ticket_bll.py 
class TicketBLL: 
    def __init__(self, dal): 
        self._dal = dal 
    
    def listar_tickets(self): 
        return self._dal.obter_todos() 
    
    def criar_ticket(self, utilizador_id): 
        return self._dal.inserir(utilizador_id)
```

### `ui/`
Gere toda a interação com os utilizadores através do Discord, incluindo comandos, botões, menus e mensagens. Não deve conter lógica de negócio nem acesso direto à base de dados.

```python
# ui/commands.py
class DiscordBot:
    def __init__(self, bll):
        self._bll = bll

    def iniciar(self):
        print("Bot iniciado e pronto para receber comandos.")

    def listar_tickets(self):
        tickets = self._bll.listar_tickets()
        for ticket in tickets:
            print(ticket)
```

## Nota sobre `__init__.py`

Os ficheiros __init__.py (que podem estar vazios) são necessários para que o Python trate as pastas dal/, bll/ e ui/ como módulos importáveis, facilitando a organização e manutenção do projeto.
