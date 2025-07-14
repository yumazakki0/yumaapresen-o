# model.py
class Tarefa:
    def __init__(self, descricao):
        self.descricao = descricao
        self.concluida = False

    def concluir(self):
        self.concluida = True

# view.py
class TarefaView:
    def mostrar_menu(self):
        print("\n1. Adicionar Tarefa\n2. Listar Tarefas\n3. Concluir Tarefa\n4. Sair")

    def pedir_descricao(self):
        return input("Descrição da tarefa: ")

    def mostrar_tarefas(self, tarefas):
        for i, t in enumerate(tarefas):
            status = "[x]" if t.concluida else "[ ]"
            print(f"{i+1}. {status} {t.descricao}")

    def pedir_indice_para_concluir(self):
        return int(input("Número da tarefa para concluir: ")) - 1

    def pedir_opcao(self):
        return input("Escolha uma opção: ")

# controller.py
from model import Tarefa

class TarefaController:
    def __init__(self, view):
        self.view = view
        self.tarefas = []

    def executar(self):
        while True:
            self.view.mostrar_menu()
            opcao = self.view.pedir_opcao()

            if opcao == "1":
                desc = self.view.pedir_descricao()
                self.tarefas.append(Tarefa(desc))
            elif opcao == "2":
                self.view.mostrar_tarefas(self.tarefas)
            elif opcao == "3":
                self.view.mostrar_tarefas(self.tarefas)
                i = self.view.pedir_indice_para_concluir()
                if 0 <= i < len(self.tarefas):
                    self.tarefas[i].concluir()
            elif opcao == "4":
                break

# main_mvc.py
from view import TarefaView
from controller import TarefaController

view = TarefaView()
controller = TarefaController(view)
controller.executar()
