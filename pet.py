import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import threading
import random
import sqlite3
import os
import re

try:
    import winsound
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False

# --- Configurações ---
DB_FILE = 'pet_assistente.db'
MASCOTE_IMG = 'mascote.gif'
POMODORO_DURATION = 25

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS lembretes (
            id INTEGER PRIMARY KEY,
            mensagem TEXT,
            categoria TEXT,
            horario TEXT,
            tipo TEXT,
            repetir TEXT,
            faixa_inicio TEXT,
            faixa_fim TEXT,
            valido_ate TEXT,
            emoji TEXT,
            avatar_estado TEXT,
            avisado INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    return conn

def speak(text):
    print(f"[Pet diz]: {text}")

def interpretar_intencao(texto):
    lembrete_match = re.search(r'(me lembre de|lembrete para|lembre-me de) (.+?) (às|as) (\d{1,2}:\d{2})', texto.lower())
    if lembrete_match:
        mensagem = lembrete_match.group(2).strip()
        horario = lembrete_match.group(4)
        return {'intent': 'criar_lembrete','dados': {'mensagem': mensagem, 'horario': horario}}
    return None

class PetAssistant(tk.Tk):
    def __init__(self, db_conn):
        super().__init__()
        self.conn = db_conn
        self.title("🐶 Pet Assistente Supremo")
        self.geometry("1000x750")
        self.configure(bg='#1e1e1e')

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TButton", font=('Segoe UI', 10), padding=6)
        style.configure("TLabel", font=('Segoe UI', 10), background='#1e1e1e', foreground='white')
        style.configure("Treeview", background="#2e2e2e", fieldbackground="#2e2e2e", foreground="white")
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), background="#3e3e3e", foreground="white")
        style.configure("TNotebook.Tab", font=('Segoe UI', 10, 'bold'), padding=[10, 5])

        self.build_menu()
        self.create_ui()
        speak("Olá! Seu Pet Assistente está pronto.")

    def build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        settings = tk.Menu(menubar, tearoff=0)
        settings.add_command(label='Iniciar Pomodoro', command=self.start_pomodoro)
        settings.add_command(label='Sincronizar Cloud', command=self.sync_cloud)
        settings.add_separator()
        settings.add_command(label='Sair', command=self.quit)
        menubar.add_cascade(label='Ferramentas', menu=settings)

    def create_ui(self):
        top_frame = tk.Frame(self, bg='#1e1e1e')
        top_frame.pack(pady=10)
        tk.Label(top_frame, text='🐾 Bem-vindo ao seu Assistente Virtual!', bg='#1e1e1e', fg='white', font=('Segoe UI', 14, 'bold')).pack()

        mascote_path = os.path.join(os.getcwd(), MASCOTE_IMG)
        if os.path.exists(mascote_path):
            self.mascote_tk = tk.PhotoImage(file=mascote_path)
            tk.Label(self, image=self.mascote_tk, bg='#1e1e1e').pack()

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab_rem = ttk.Frame(notebook)
        notebook.add(self.tab_rem, text='📋 Lembretes')
        self.build_reminders_tab(self.tab_rem)

        self.tab_chat = ttk.Frame(notebook)
        notebook.add(self.tab_chat, text='💬 Chatbot')
        self.build_chat_tab(self.tab_chat)

        self.tab_set = ttk.Frame(notebook)
        notebook.add(self.tab_set, text='⚙️ Configurações')
        self.build_settings_tab(self.tab_set)

    def build_reminders_tab(self, parent):
        frm = ttk.Frame(parent, padding=10)
        frm.pack(fill='x')
        labels = ['Mensagem','Categoria','Horário','Repetir','Aleatório Início','Aleatório Fim','Válido Até']
        for i, label in enumerate(labels):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(frm, textvariable=var, width=50)
            entry.grid(row=i, column=1, pady=2)
            setattr(self, f'var_{i}', var)
        ttk.Button(frm, text='➕ Adicionar', command=self.add_reminder).grid(row=7, column=0, pady=10)
        ttk.Button(frm, text='🔄 Atualizar', command=self.load_tree).grid(row=7, column=1, pady=10)

        cols = ['ID','Msg','Cat','Hora','Rep','Range','Válido','Avisado']
        self.tree = ttk.Treeview(parent, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.load_tree()

    def load_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        c = self.conn.cursor()
        c.execute('SELECT id, mensagem, categoria, horario, repetir, faixa_inicio||"-"||faixa_fim, valido_ate, avisado FROM lembretes')
        for r in c.fetchall():
            self.tree.insert('', tk.END, values=r)

    def add_reminder(self, mensagem=None, horario=None):
        text = mensagem or self.var_0.get().strip()
        if not text:
            return messagebox.showwarning('Erro','Campo vazio')
        params = [getattr(self, f'var_{i}').get() or None for i in range(1, 7)]
        horario_final = horario or params[1]
        emoji = random.choice(['💧','📚','⚽','🍎','🔔'])
        data = (text, params[0], horario_final, 'manual', 'nenhum', params[2], params[3], params[4], emoji, 'feliz')
        c = self.conn.cursor()
        c.execute('''INSERT INTO lembretes(mensagem, categoria, horario, tipo, repetir, faixa_inicio, faixa_fim, valido_ate, emoji, avatar_estado)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        self.conn.commit()
        if SOUND_ENABLED:
            winsound.MessageBeep()
        speak(f'Lembrete adicionado: {text}')
        self.load_tree()

    def build_chat_tab(self, parent):
        frm = ttk.Frame(parent, padding=10)
        frm.pack(fill='both', expand=True)
        self.chat_log = tk.Text(frm, height=15, state='disabled', bg='#2e2e2e', fg='white', insertbackground='white', font=('Segoe UI', 10))
        self.chat_log.pack(fill='both', expand=True)
        self.chat_entry = ttk.Entry(frm, font=('Segoe UI', 10))
        self.chat_entry.pack(fill='x', pady=5)
        self.chat_entry.bind('<Return>', self.handle_chat)

    def handle_chat(self, event=None):
        user = self.chat_entry.get().strip()
        if not user:
            return
        self.chat_entry.delete(0, tk.END)
        self.post_chat('Você', user)

        intencao = interpretar_intencao(user)
        if intencao and intencao['intent'] == 'criar_lembrete':
            dados = intencao['dados']
            self.add_reminder(dados['mensagem'], dados['horario'])
            reply = f'Lembrete criado: "{dados["mensagem"]}" para às {dados["horario"]}. ✅'
        else:
            reply = f"Desculpe, ainda não entendi o que você quis dizer. 😕"

        self.post_chat('Pet', reply)
        speak(reply)

    def post_chat(self, sender, msg):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f'{sender}: {msg}\n')
        self.chat_log.config(state='disabled')
        self.chat_log.see(tk.END)

    def build_settings_tab(self, parent):
        frm = ttk.Frame(parent, padding=20)
        frm.pack(fill='x')
        ttk.Button(frm, text='Backup DB', command=self.backup_db).pack(pady=5)

    def backup_db(self):
        dest = filedialog.asksaveasfilename(defaultextension='.db')
        if dest:
            self.conn.close()
            import shutil
            shutil.copy(DB_FILE, dest)
            self.conn = sqlite3.connect(DB_FILE)
            messagebox.showinfo('Backup', 'Concluído!')
            speak('Backup realizado com sucesso')

    def start_pomodoro(self):
        def run():
            speak('Iniciando Pomodoro de 25 minutos')
            time_end = datetime.now() + timedelta(minutes=POMODORO_DURATION)
            while datetime.now() < time_end:
                pass
            speak('Pomodoro concluído!')
        threading.Thread(target=run, daemon=True).start()

    def sync_cloud(self):
        messagebox.showinfo('Cloud', 'Sincronização concluída (placeholder).')
        speak('Sincronização na nuvem concluída.')

if __name__ == '__main__':
    conn = init_db()
    app = PetAssistant(conn)
    app.mainloop()
