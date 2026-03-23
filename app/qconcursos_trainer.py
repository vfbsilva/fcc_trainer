#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
import re
import webbrowser

class QuestionsTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 FCC Trainer - TRT Informática")
        self.root.geometry("1400x950")
        self.root.configure(bg='#f5f5f5')

        # Dados
        self.data_dir = Path.home() / "fcc_trainer" / "data"
        self.all_questions = []
        self.filtered_questions = []
        self.current_index = 0

        # Carregar dados
        self.load_questions()
        self.create_widgets()
        self.update_display()

    def limpar_enunciado(self, texto):
        """Limpar HTML e metadados do enunciado"""
        # Remover HTML tags
        texto = re.sub(r'<[^>]+>', '', texto)

        # Remover metadados
        texto = re.sub(r'Ano:\s*\d{4}.*', '', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'Banca:.*?Prova:.*?\|', '', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'TRT.*?Especialidade.*?Tecnologia.*?\|', '', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'Q\d+', '', texto)
        texto = re.sub(r'Alternativas', '', texto, flags=re.IGNORECASE)
        texto = re.sub(r'Engenharia de Software.*?Ferramentas.*?,', '', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'Metodologia de desenvolvimento.*?,', '', texto, flags=re.IGNORECASE | re.DOTALL)

        # Remover espaços em branco múltiplos
        texto = re.sub(r'\s+', ' ', texto).strip()

        # Remover números iniciais (Questão 4 4 4)
        texto = re.sub(r'^(\d+\s+){2,}', '', texto).strip()

        return texto

    def load_questions(self):
        """Carregar questões dos JSONs"""
        print("📂 Carregando questões...")

        if not self.data_dir.exists():
            messagebox.showerror("Erro", f"Pasta não encontrada: {self.data_dir}")
            return

        json_files = list(self.data_dir.glob("*.json"))

        if not json_files:
            messagebox.showerror("Erro", f"Nenhum arquivo JSON em {self.data_dir}")
            return

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)

                for q in questions:
                    # Limpar enunciado
                    enunciado = self.limpar_enunciado(q.get('enunciado', ''))

                    # Filtrar alternativas válidas (não vazias)
                    alternativas = {}
                    for letra in ['A', 'B', 'C', 'D', 'E']:
                        alt_text = q.get('alternativas', {}).get(letra, '').strip()
                        if alt_text and len(alt_text) > 3:
                            alternativas[letra] = alt_text

                    if enunciado.strip():  # Só adicionar se tem enunciado
                        self.all_questions.append({
                            'numero': q.get('numero', 'N/A'),
                            'enunciado': enunciado,
                            'alternativas': alternativas,
                            'tema': q.get('tema', 'N/A'),
                            'ano': q.get('ano', 'N/A'),
                            'tem_alternativas': len(alternativas) >= 4,
                            'pagina': q.get('pagina', 'N/A'),
                        })

                print(f"✓ {json_file.name}: {len(questions)} questões")
            except Exception as e:
                print(f"❌ Erro em {json_file.name}: {e}")

        print(f"✅ Total: {len(self.all_questions)} questões carregadas")
        self.filtered_questions = self.all_questions.copy()

    def create_widgets(self):
        """Criar interface"""

        # === TOOLBAR ===
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=15, pady=10)

        # Progresso
        self.progress_label = ttk.Label(toolbar, text="", font=('Arial', 11, 'bold'), foreground='#333')
        self.progress_label.pack(side=tk.LEFT, padx=10)

        # Navegação
        ttk.Button(toolbar, text="⬅️  Anterior (A)", command=self.prev_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Próxima (D) ➡️", command=self.next_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🔄 Reiniciar", command=self.restart).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🔗 Ver no QConcursos", command=self.open_link).pack(side=tk.RIGHT, padx=5)

        # === MAIN FRAME ===
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # --- INFO ---
        info_frame = ttk.Frame(main)
        info_frame.pack(fill=tk.X, pady=(0, 15))

        self.info_label = ttk.Label(info_frame, text="", font=('Arial', 10), foreground='#666')
        self.info_label.pack(anchor=tk.W)

        # --- ENUNCIADO ---
        enum_frame = ttk.LabelFrame(main, text="📝 ENUNCIADO", padding=15)
        enum_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.enunciado_widget = tk.Text(
            enum_frame,
            wrap=tk.WORD,
            font=('Arial', 12),
            height=10,
            bg='white',
            fg='#333',
            relief=tk.FLAT,
            bd=0
        )
        self.enunciado_widget.pack(fill=tk.BOTH, expand=True)
        self.enunciado_widget.config(state=tk.DISABLED)

        # Scrollbar enunciado
        scrollbar_enum = ttk.Scrollbar(enum_frame, orient=tk.VERTICAL, command=self.enunciado_widget.yview)
        scrollbar_enum.pack(side=tk.RIGHT, fill=tk.Y)
        self.enunciado_widget.config(yscrollcommand=scrollbar_enum.set)

        # --- ALTERNATIVAS ---
        alt_frame = ttk.LabelFrame(main, text="🔤 ALTERNATIVAS", padding=15)
        alt_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

        self.alternativas_widget = tk.Text(
            alt_frame,
            wrap=tk.WORD,
            font=('Courier', 13),
            height=7,
            bg='#fafafa',
            fg='#333',
            relief=tk.FLAT,
            bd=0
        )
        self.alternativas_widget.pack(fill=tk.BOTH, expand=True)
        self.alternativas_widget.config(state=tk.DISABLED)

        # Scrollbar alternativas
        scrollbar_alt = ttk.Scrollbar(alt_frame, orient=tk.VERTICAL, command=self.alternativas_widget.yview)
        scrollbar_alt.pack(side=tk.RIGHT, fill=tk.Y)
        self.alternativas_widget.config(yscrollcommand=scrollbar_alt.set)

        # --- STATUS ---
        status_frame = ttk.Frame(main)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame, text="", font=('Arial', 9), foreground='#999')
        self.status_label.pack(anchor=tk.W)

        # === SHORTCUTS ===
        self.root.bind('<a>', lambda e: self.prev_question())
        self.root.bind('<d>', lambda e: self.next_question())
        self.root.bind('<r>', lambda e: self.restart())
        self.root.bind('<Left>', lambda e: self.prev_question())
        self.root.bind('<Right>', lambda e: self.next_question())

    def next_question(self):
        """Próxima"""
        if self.filtered_questions:
            self.current_index = (self.current_index + 1) % len(self.filtered_questions)
            self.update_display()

    def prev_question(self):
        """Anterior"""
        if self.filtered_questions:
            self.current_index = (self.current_index - 1) % len(self.filtered_questions)
            self.update_display()

    def restart(self):
        """Reiniciar"""
        self.current_index = 0
        self.update_display()

    def open_link(self):
        """Abrir no QConcursos"""
        if not self.filtered_questions:
            return
        q = self.filtered_questions[self.current_index]
        webbrowser.open(f"https://www.qconcursos.com/questoes-de-concursos/search?q={q['numero']}")

    def update_display(self):
        """Atualizar tela"""
        if not self.filtered_questions:
            self.enunciado_widget.config(state=tk.NORMAL)
            self.enunciado_widget.delete(1.0, tk.END)
            self.enunciado_widget.insert(1.0, "❌ Nenhuma questão encontrada")
            self.enunciado_widget.config(state=tk.DISABLED)
            self.alternativas_widget.config(state=tk.NORMAL)
            self.alternativas_widget.delete(1.0, tk.END)
            self.alternativas_widget.config(state=tk.DISABLED)
            self.progress_label.config(text="")
            self.info_label.config(text="")
            self.status_label.config(text="")
            return

        q = self.filtered_questions[self.current_index]

        # Info
        info = f"Ano: {q['ano']} | Tema: {q['tema']} | Nº {q['numero']} | Página {q['pagina']}"
        self.info_label.config(text=info)

        # Enunciado
        self.enunciado_widget.config(state=tk.NORMAL)
        self.enunciado_widget.delete(1.0, tk.END)
        self.enunciado_widget.insert(1.0, q['enunciado'])
        self.enunciado_widget.config(state=tk.DISABLED)

        # Alternativas
        self.alternativas_widget.config(state=tk.NORMAL)
        self.alternativas_widget.delete(1.0, tk.END)

        if q['tem_alternativas']:
            alt_text = ""
            for letra in ['A', 'B', 'C', 'D', 'E']:
                if letra in q['alternativas']:
                    alt_text += f"{letra})  {q['alternativas'][letra]}\n\n"
            self.alternativas_widget.insert(1.0, alt_text)
            self.status_label.config(text="✓ Alternativas disponíveis", foreground='green')
        else:
            self.alternativas_widget.insert(1.0, "⚠️  Alternativas não disponíveis\n\nClique em 'Ver no QConcursos' para ver a questão completa")
            self.status_label.config(text="⚠️  Consulte o site para alternativas completas", foreground='orange')

        self.alternativas_widget.config(state=tk.DISABLED)

        # Progresso
        num_total = len(self.filtered_questions)
        progress = f"Questão {self.current_index + 1} de {num_total}"
        self.progress_label.config(text=progress)

def main():
    root = tk.Tk()
    app = QuestionsTrainer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
