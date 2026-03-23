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
        self.root.geometry("1500x1050")
        self.root.configure(bg='#f5f5f5')

        # Dados
        self.data_dir = Path.home() / "fcc_trainer" / "data"
        self.all_questions = []
        self.filtered_questions = []
        self.current_index = 0
        self.user_answer = None

        # Cores por dificuldade
        self.difficulty_colors = {
            'CRITICO': '#ffcccc',
            'MUITO_IMPORTANTE': '#ffe6cc',
            'IMPORTANTE': '#ffffcc',
            'RECOMENDADO': '#ccffcc',
            'NAO_CATEGORIZADO': '#e6e6e6'
        }

        self.difficulty_emojis = {
            'CRITICO': '🔴',
            'MUITO_IMPORTANTE': '🟠',
            'IMPORTANTE': '🟡',
            'RECOMENDADO': '🟢',
            'NAO_CATEGORIZADO': '⚪'
        }

        # Carregar dados
        self.load_questions()
        self.create_widgets()
        self.update_display()

    def limpar_enunciado(self, texto):
        """Limpar HTML e metadados do enunciado"""
        if not texto:
            return ""

        # Remover HTML tags
        texto = re.sub(r'<[^>]+>', '', texto)

        # Remover tudo antes da primeira letra maiúscula (metadados)
        match = re.search(r'[A-ZÁÉÍÓÚ]', texto)
        if match:
            texto = texto[match.start():]

        # Remover metadados conhecidos
        texto = re.sub(r'Ano:\s*\d{4}.*', '', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'Banca:.*?(?=A\)|B\)|C\)|D\)|E\)|$)', '', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'Prova:.*?(?=A\)|B\)|C\)|D\)|E\)|$)', '', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'TRT.*?(?=A\)|B\)|C\)|D\)|E\)|$)', '', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'Q\d+', '', texto)
        texto = re.sub(r'Alternativas', '', texto, flags=re.IGNORECASE)

        # Remover espaços múltiplos e quebras
        texto = re.sub(r'\s+', ' ', texto).strip()

        # Remover números duplicados no início
        texto = re.sub(r'^(\d+\s+)+', '', texto).strip()

        # Remover disciplinas/assuntos no início
        texto = re.sub(r'^[A-Za-z\s,]+\s+,\s+', '', texto)

        return texto if len(texto) > 30 else ""

    def categorizar_por_dificuldade(self, tema):
        """Categorizar questão por dificuldade"""
        tema_lower = (tema or 'N/A').lower()
        critico = ['segurança', 'criptografia', 'lacp', 'tcp/ip', 'docker', 'kubernetes', 'git']
        muito_importante = ['spring', 'java', 'python', 'javascript', 'sql', 'database', 'api', 'rest', 'cloud']
        importante = ['engenharia', 'scrum', 'agile', 'metodologia', 'design patterns', 'oop']
        recomendado = ['internet', 'email', 'web', 'html', 'css', 'navegador']

        for palavra in critico:
            if palavra in tema_lower:
                return 'CRITICO'
        for palavra in muito_importante:
            if palavra in tema_lower:
                return 'MUITO_IMPORTANTE'
        for palavra in importante:
            if palavra in tema_lower:
                return 'IMPORTANTE'
        for palavra in recomendado:
            if palavra in tema_lower:
                return 'RECOMENDADO'
        return 'NAO_CATEGORIZADO'

    def load_questions(self):
        """Carregar questões"""
        print("📂 Carregando questões...")
        if not self.data_dir.exists():
            messagebox.showerror("Erro", f"Pasta não encontrada: {self.data_dir}")
            return

        # Preferir arquivos "limpo_*"
        json_files = list(self.data_dir.glob("limpo_*.json"))
        if not json_files:
            json_files = list(self.data_dir.glob("questoes_*.json"))
        if not json_files:
            messagebox.showerror("Erro", f"Nenhum JSON em {self.data_dir}")
            return

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)

                carregadas = 0
                for q in questions:
                    enunciado = self.limpar_enunciado(q.get('enunciado', ''))

                    if not enunciado:
                        continue

                    # Parsear alternativas (pode ser dict ou lista)
                    alternativas = {}
                    alt_raw = q.get('alternativas', {})

                    if isinstance(alt_raw, dict):
                        for letra in ['A', 'B', 'C', 'D', 'E']:
                            alt_text = alt_raw.get(letra, '').strip()
                            if alt_text and len(alt_text) > 3:
                                alternativas[letra] = alt_text
                    elif isinstance(alt_raw, list):
                        # Se for lista, tentar mapear
                        for i, alt_text in enumerate(alt_raw):
                            if i < 5 and alt_text and len(str(alt_text)) > 3:
                                alternativas[chr(65 + i)] = str(alt_text)

                    tema = q.get('tema', 'N/A')
                    dificuldade = self.categorizar_por_dificuldade(tema)

                    self.all_questions.append({
                        'numero': q.get('numero', 'N/A'),
                        'enunciado': enunciado,
                        'alternativas': alternativas,
                        'tema': tema,
                        'dificuldade': dificuldade,
                        'ano': q.get('ano', 'N/A'),
                        'tem_alternativas': len(alternativas) >= 4,
                        'pagina': q.get('pagina', 'N/A'),
                    })
                    carregadas += 1

                print(f"✓ {json_file.name}: {carregadas} questões carregadas")
            except Exception as e:
                print(f"❌ Erro em {json_file.name}: {e}")
                import traceback
                traceback.print_exc()

        print(f"✅ Total: {len(self.all_questions)} questões carregadas")
        self.filtered_questions = self.all_questions.copy()

    def apply_filters(self):
        """Aplicar filtros"""
        selected = [d for d, var in self.difficulty_vars.items() if var.get()]
        if not selected:
            self.filtered_questions = []
        else:
            self.filtered_questions = [q for q in self.all_questions if q['dificuldade'] in selected]
        self.current_index = 0
        self.user_answer = None
        self.update_display()

    def create_widgets(self):
        """Criar interface"""

        # === FILTROS ===
        filter_frame = ttk.LabelFrame(self.root, text="🎯 Filtrar por Dificuldade", padding=10)
        filter_frame.pack(fill=tk.X, padx=15, pady=10)

        self.difficulty_vars = {}
        difficulties = [
            ('CRITICO', '🔴 Crítico'),
            ('MUITO_IMPORTANTE', '🟠 Muito Importante'),
            ('IMPORTANTE', '🟡 Importante'),
            ('RECOMENDADO', '🟢 Recomendado'),
            ('NAO_CATEGORIZADO', '⚪ Não Categorizado')
        ]

        for diff_key, diff_label in difficulties:
            var = tk.BooleanVar(value=True)
            self.difficulty_vars[diff_key] = var

            # Criar frame colorido para cada checkbox
            check_frame = tk.Frame(filter_frame, bg=self.difficulty_colors[diff_key], padx=5, pady=5)
            check_frame.pack(side=tk.LEFT, padx=5)

            ttk.Checkbutton(
                check_frame,
                text=diff_label,
                variable=var,
                command=self.apply_filters
            ).pack()

        # === TOOLBAR ===
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=15, pady=10)

        self.progress_label = ttk.Label(toolbar, text="", font=('Arial', 11, 'bold'))
        self.progress_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(toolbar, text="⬅️  Anterior", command=self.prev_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Próxima ➡️", command=self.next_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🔄 Reiniciar", command=self.restart).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🔗 QConcursos", command=self.open_link).pack(side=tk.RIGHT, padx=5)

        # === MAIN ===
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.info_label = ttk.Label(main, text="", font=('Arial', 10))
        self.info_label.pack(anchor=tk.W, pady=(0, 10))

        # Enunciado
        enum_frame = ttk.LabelFrame(main, text="📝 ENUNCIADO", padding=15)
        enum_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.enunciado_widget = tk.Text(
            enum_frame,
            wrap=tk.WORD,
            font=('Arial', 13),
            height=9,
            bg='white',
            fg='#222',
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10
        )
        self.enunciado_widget.pack(fill=tk.BOTH, expand=True)
        self.enunciado_widget.config(state=tk.DISABLED)

        # Configurar tags de formatação
        self.enunciado_widget.tag_configure('normal', font=('Arial', 13), foreground='#333')

        # Alternativas + Respostas
        alt_frame = ttk.LabelFrame(main, text="🔤 ALTERNATIVAS", padding=15)
        alt_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

        # Texto alternativas
        alt_text_frame = ttk.Frame(alt_frame)
        alt_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        self.alternativas_widget = tk.Text(alt_text_frame, wrap=tk.WORD, font=('Courier', 12), height=5, bg='#fafafa')
        self.alternativas_widget.pack(fill=tk.BOTH, expand=True)
        self.alternativas_widget.config(state=tk.DISABLED)

        # Botões resposta
        buttons_frame = tk.Frame(alt_frame, bg='#f5f5f5')
        buttons_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        tk.Label(buttons_frame, text="Sua Resposta:", font=('Arial', 10, 'bold'), bg='#f5f5f5').pack(pady=(0, 10))

        self.answer_buttons = {}
        for letra in ['A', 'B', 'C', 'D', 'E']:
            btn = tk.Button(
                buttons_frame,
                text=letra,
                font=('Arial', 16, 'bold'),
                width=5,
                height=2,
                bg='#f0f0f0',
                fg='#333',
                command=lambda l=letra: self.set_answer(l)
            )
            btn.pack(pady=5)
            self.answer_buttons[letra] = btn

        # Feedback
        self.feedback_label = ttk.Label(main, text="", font=('Arial', 9, 'italic'))
        self.feedback_label.pack(anchor=tk.W, pady=(10, 0))

        # Shortcuts
        for key in ['<Left>', '<Right>', '<a>', '<d>', '<r>']:
            if key == '<Left>':
                self.root.bind(key, lambda e: self.prev_question())
            elif key == '<Right>':
                self.root.bind(key, lambda e: self.next_question())
            elif key == '<r>':
                self.root.bind(key, lambda e: self.restart())

        for letra in ['a', 'b', 'c', 'd', 'e']:
            self.root.bind(letra, lambda e, l=letra.upper(): self.set_answer(l))

    def set_answer(self, letra):
        """Definir resposta"""
        if not self.filtered_questions:
            return

        self.user_answer = letra

        # Destacar botão
        for l in ['A', 'B', 'C', 'D', 'E']:
            if l == letra:
                self.answer_buttons[l].config(bg='#4CAF50', fg='white')
            else:
                self.answer_buttons[l].config(bg='#f0f0f0', fg='#333')

        self.update_feedback()

    def update_feedback(self):
        """Atualizar feedback"""
        if not self.user_answer:
            self.feedback_label.config(text="")
            return

        q = self.filtered_questions[self.current_index]
        feedback = f"✓ Sua resposta: {self.user_answer}"

        if self.user_answer in q['alternativas']:
            feedback += f"\n   {q['alternativas'][self.user_answer]}"
            self.feedback_label.config(text=feedback, foreground='#2196F3')
        else:
            self.feedback_label.config(text=feedback + " (não disponível)", foreground='#FF9800')

    def next_question(self):
        if self.filtered_questions:
            self.current_index = (self.current_index + 1) % len(self.filtered_questions)
            self.user_answer = None
            self.update_display()

    def prev_question(self):
        if self.filtered_questions:
            self.current_index = (self.current_index - 1) % len(self.filtered_questions)
            self.user_answer = None
            self.update_display()

    def restart(self):
        self.current_index = 0
        self.user_answer = None
        self.update_display()

    def open_link(self):
        if self.filtered_questions:
            q = self.filtered_questions[self.current_index]
            webbrowser.open(f"https://www.qconcursos.com/questoes-de-concursos/search?q={q['numero']}")

    def update_display(self):
        if not self.filtered_questions:
            self.enunciado_widget.config(state=tk.NORMAL)
            self.enunciado_widget.delete(1.0, tk.END)
            self.enunciado_widget.insert(1.0, "❌ Nenhuma questão")
            self.enunciado_widget.config(state=tk.DISABLED)
            return

        q = self.filtered_questions[self.current_index]
        emoji = self.difficulty_emojis.get(q['dificuldade'], '')

        # Info
        info = f"{emoji} {q['dificuldade']} | Ano: {q['ano']} | Tema: {q['tema']} | Nº {q['numero']}"
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
        else:
            self.alternativas_widget.insert(1.0, "⚠️  Não disponível")

        self.alternativas_widget.config(state=tk.DISABLED)

        # Resetar botões
        for btn in self.answer_buttons.values():
            btn.config(bg='#f0f0f0', fg='#333', state=tk.NORMAL)

        # Progresso
        num_total = len(self.filtered_questions)
        self.progress_label.config(text=f"Questão {self.current_index + 1} de {num_total}")

        self.feedback_label.config(text="")

def main():
    root = tk.Tk()
    app = QuestionsTrainer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
