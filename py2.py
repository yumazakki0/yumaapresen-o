# componente_modelo.py
class Tarefa:
    def __init__(self, descricao):
        self.descricao = descricao
        self.concluida = False

    def concluir(self):
        self.concluida = True

# componente_repositorio.py
class RepositorioTarefas:
    def __init__(self):
        self.tarefas = []

    def adicionar(self, tarefa):
        self.tarefas.append(tarefa)

    def listar(self):
        return self.tarefas

# componente_interface.py
def exibir_tarefas(tarefas):
    for i, t in enumerate(tarefas):
        status = "[x]" if t.concluida else "[ ]"
        print(f"{i+1}. {status} {t.descricao}")

# main_componentes.py
from componente_modelo import Tarefa
from componente_repositorio import RepositorioTarefas
from componente_interface import exibir_tarefas

repo = RepositorioTarefas()

while True:
    print("\n1. Adicionar Tarefa\n2. Listar Tarefas\n3. Concluir Tarefa\n4. Sair")
    op = input("Opção: ")

    if op == "1":
        desc = input("Descrição: ")
        repo.adicionar(Tarefa(desc))
    elif op == "2":
        exibir_tarefas(repo.listar())
    elif op == "3":
        exibir_tarefas(repo.listar())
        idx = int(input("Número da tarefa a concluir: ")) - 1
        repo.tarefas[idx].concluir()
    elif op == "4":
        break
