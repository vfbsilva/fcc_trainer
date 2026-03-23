#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path
import textwrap
import webbrowser

class QuestionsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Questões TRT - FCC (Informática)")
        self.root.geometry("1400x900")

        # Dados
        self.questions_path = Path.home() / "Documentos" / "Editais_TRTs" / "questoes_estruturadas"
        self.all_questions = []
        self.filtered_questions = []
        self.current_index = 0

        # Cores
        self.colors = {
            'CRITICO': '#ffdddd',
            'MUITO_IMPORTANTE': '#fff5dd',
            'IMPORTANTE': '#fffadd',
            'RECOMENDADO': '#ddffdd',
            'NAO_CATEGORIZADO': '#f0f0f0'
        }

        self.difficulty_colors = {
            'CRITICO': '🔴 CRÍTICO',
            'MUITO_IMPORTANTE': '🟠 MUITO IMPORTANTE',
            'IMPORTANTE': '🟡 IMPORTANTE',
            'RECOMENDADO': '🟢 RECOMENDADO',
            'NAO_CATEGORIZADO': '⚪ NÃO CATEGORIZADO'
        }

        # Carregar questões
        self.load_questions()
        self.create_widgets()
        self.update_display()

    def load_questions(self):
        """Carregar questões estruturadas"""
        print("📂 Carregando questões...")

        if not self.questions_path.exists():
            messagebox.showerror("Erro", f"Pasta não encontrada: {self.questions_path}")
            return

        for difficulty_folder in self.questions_path.iterdir():
            if not difficulty_folder.is_dir():
                continue

            difficulty = difficulty_folder.name
            json_file = difficulty_folder / 'questoes.json'

            if not json_file.exists():
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)

                for q in questions:
                    self.all_questions.append({
                        'numero': q.get('numero', 'N/A'),
                        'enunciado': q.get('enunciado', ''),
                        'alternativas': q.get('alternativas', {}),
                        'temAlternativas': q.get('temAlternativasEstruturadas', False),
                        'tema': q.get('tema', 'N/A'),
                        'dificuldade': difficulty,
                        'dificuldade_label': self.difficulty_colors.get(difficulty, difficulty),
                        'pagina': q.get('pagina', 'N/A'),
                        'idGlobal': q.get('idGlobal', 0)
                    })

                print(f"✓ {difficulty}: {len(questions)} questões")
            except Exception as e:
                print(f"❌ Erro ao carregar {difficulty}: {e}")

        print(f"✅ Total: {len(self.all_questions)} questões")
        self.filtered_questions = self.all_questions.copy()

    def create_widgets(self):
        """Criar interface"""

        # === FRAME SUPERIOR (Filtros) ===
        filter_frame = ttk.LabelFrame(self.root, text="Filtros de Dificuldade", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        self.difficulty_vars = {}
        difficulties = ['CRITICO', 'MUITO_IMPORTANTE', 'IMPORTANTE', 'RECOMENDADO', 'NAO_CATEGORIZADO']

        for i, difficulty in enumerate(difficulties):
            var = tk.BooleanVar(value=True)
            self.difficulty_vars[difficulty] = var

            label_text = self.difficulty_colors[difficulty]

            cb = ttk.Checkbutton(
                filter_frame,
                text=label_text,
                variable=var,
                command=self.apply_filters
            )
            cb.pack(side=tk.LEFT, padx=10)

        # === FRAME CENTRAL (Questão) ===
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Info ---
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.info_label = ttk.Label(info_frame, text="", font=('Arial', 10, 'bold'))
        self.info_label.pack(anchor=tk.W, side=tk.LEFT)

        self.link_button = ttk.Button(info_frame, text="🔗 Ver no QConcursos", command=self.open_link)
        self.link_button.pack(anchor=tk.E, side=tk.RIGHT)

        # --- Enunciado ---
        enum_label = ttk.Label(main_frame, text="ENUNCIADO:", font=('Arial', 9, 'bold'))
        enum_label.pack(anchor=tk.W, pady=(5, 0))

        self.enunciado_widget = tk.Text(
            main_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            height=8,
            bg='white',
            fg='black'
        )
        self.enunciado_widget.pack(fill=tk.BOTH, expand=False, pady=5)
        self.enunciado_widget.config(state=tk.DISABLED)

        # --- Alternativas ---
        alt_label = ttk.Label(main_frame, text="ALTERNATIVAS:", font=('Arial', 9, 'bold'))
        alt_label.pack(anchor=tk.W, pady=(10, 0))

        self.alternativas_widget = tk.Text(
            main_frame,
            wrap=tk.WORD,
            font=('Courier', 10),
            height=6,
            bg='#f9f9f9',
            fg='black'
        )
        self.alternativas_widget.pack(fill=tk.BOTH, expand=False, pady=5)
        self.alternativas_widget.config(state=tk.DISABLED)

        # --- Status alternativas ---
        self.alt_status_label = ttk.Label(main_frame, text="", font=('Arial', 8, 'italic'), foreground='gray')
        self.alt_status_label.pack(anchor=tk.W)

        # === FRAME INFERIOR (Navegação) ===
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(nav_frame, text="⬅️  Anterior", command=self.prev_question).pack(side=tk.LEFT, padx=5)

        self.progress_label = ttk.Label(nav_frame, text="", font=('Arial', 10, 'bold'))
        self.progress_label.pack(side=tk.LEFT, padx=20)

        ttk.Button(nav_frame, text="Próxima ➡️", command=self.next_question).pack(side=tk.LEFT, padx=5)

        ttk.Button(nav_frame, text="🔄 Reiniciar", command=self.restart).pack(side=tk.RIGHT, padx=5)

    def apply_filters(self):
        """Aplicar filtros"""
        selected = [d for d, var in self.difficulty_vars.items() if var.get()]

        if not selected:
            self.filtered_questions = []
        else:
            self.filtered_questions = [q for q in self.all_questions if q['dificuldade'] in selected]

        self.current_index = 0
        self.update_display()

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
        # URL de busca no QConcursos (seria ideal ter ID da questão)
        search_url = f"https://www.qconcursos.com/questoes-de-concursos/search?q={q['numero']}"
        webbrowser.open(search_url)

    def update_display(self):
        """Atualizar tela"""
        if not self.filtered_questions:
            self.enunciado_widget.config(state=tk.NORMAL)
            self.enunciado_widget.delete(1.0, tk.END)
            self.enunciado_widget.insert(1.0, "❌ Nenhuma questão com os filtros selecionados.")
            self.enunciado_widget.config(state=tk.DISABLED)

            self.alternativas_widget.config(state=tk.NORMAL)
            self.alternativas_widget.delete(1.0, tk.END)
            self.alternativas_widget.config(state=tk.DISABLED)

            self.info_label.config(text="")
            self.progress_label.config(text="")
            self.alt_status_label.config(text="")
            return

        q = self.filtered_questions[self.current_index]

        # Info
        info_text = f"{q['dificuldade_label']} | Tema: {q['tema']} | Nº {q['numero']} | Página {q['pagina']}"
        self.info_label.config(text=info_text)

        # Enunciado
        self.enunciado_widget.config(state=tk.NORMAL)
        self.enunciado_widget.delete(1.0, tk.END)
        texto = q['enunciado'] or "[Enunciado não disponível]"
        wrapped = '\n'.join(textwrap.wrap(texto, width=120))
        self.enunciado_widget.insert(1.0, wrapped)
        self.enunciado_widget.config(state=tk.DISABLED)

        # Alternativas
        self.alternativas_widget.config(state=tk.NORMAL)
        self.alternativas_widget.delete(1.0, tk.END)

        if q['temAlternativas'] and q['alternativas']:
            alt_text = ""
            for letra in ['A', 'B', 'C', 'D', 'E']:
                if letra in q['alternativas']:
                    alt_text += f"{letra}) {q['alternativas'][letra]}\n\n"
            self.alternativas_widget.insert(1.0, alt_text)
            self.alt_status_label.config(text="✓ Alternativas extraídas automaticamente", foreground='green')
        else:
            self.alternativas_widget.insert(1.0, "[Alternativas não disponíveis nesta questão]\n\nClique em '🔗 Ver no QConcursos' para visualizar no site original.")
            self.alt_status_label.config(text="⚠️  Consulte o site original para as alternativas completas", foreground='orange')

        self.alternativas_widget.config(state=tk.DISABLED)

        # Progresso
        num_total = len(self.filtered_questions)
        progress = f"Questão {self.current_index + 1} de {num_total}"
        self.progress_label.config(text=progress)

def main():
    root = tk.Tk()
    app = QuestionsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
