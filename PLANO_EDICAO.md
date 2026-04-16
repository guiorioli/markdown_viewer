# Plano: Adicionar Modo de Edição ao Markdown Viewer

## Situação Atual

O app é um visualizador somente-leitura (`main.py`). Stack:
- **Python + tkinter** para a janela e widgets
- **tkinterweb (`HtmlFrame`)** para renderizar o HTML
- **markdown2** para converter Markdown → HTML
- Arquivo único (`main.py`), sem dependências extras além das já instaladas

O fluxo atual é: abrir arquivo → ler conteúdo → converter para HTML → exibir no `HtmlFrame`. Não há widget de texto editável nem lógica de escrita em disco.

---

## Abordagem Recomendada: Painel Dividido (Split View) com modo de edição explícito

**O app sempre abre em modo de visualização** (comportamento atual preservado). O painel de edição só aparece quando o usuário aciona explicitamente via menu ou atalho de teclado.

Ao entrar no modo de edição: editor de texto aparece à esquerda + preview renderizado à direita, separados por um `PanedWindow` redimensionável. O preview é atualizado automaticamente enquanto o usuário digita (com debounce de ~300 ms para não travar).

**Modos:**
- **Visualização (padrão):** janela inteira usada pelo `HtmlFrame`, idêntico ao comportamento atual
- **Edição:** `PanedWindow` com editor (`tk.Text`) à esquerda e preview à direita

---

## O Que Precisa Ser Feito

### 1. Refatorar o layout da janela

**Arquivo:** `main.py` — método `_setup_frame`

Criar os dois painéis, mas iniciar apenas com o `HtmlFrame` visível:
- **Modo visualização (padrão):** `HtmlFrame` ocupa a janela inteira (igual ao atual)
- **Modo edição:** `PanedWindow` com `tk.Text` à esquerda e `HtmlFrame` à direita

```
Modo visualização (padrão — sem mudança visual):
┌─────────────────────────────────────────────┐
│ Arquivo  Visualizar                          │
├─────────────────────────────────────────────┤
│           Preview (HtmlFrame)               │
│           <h1>Título</h1>                   │
│           texto aqui...                     │
└─────────────────────────────────────────────┘

Modo edição (após acionar Ctrl+E ou menu):
┌─────────────────────────────────────────────┐
│ Arquivo  Visualizar                          │
├──────────────────┬──────────────────────────┤
│  Editor (Text)   │  Preview (HtmlFrame)      │
│  # Título        │  <h1>Título</h1>          │
│  texto aqui...   │  texto aqui...            │
└──────────────────┴──────────────────────────┘
```

### 2. Criar o widget de edição

**Arquivo:** `main.py` — novo método `_setup_editor`

- Usar `tk.Text` com fonte monospace (`Consolas`, `Cascadia Code`, fallback `Courier`)
- Aplicar cores condizentes com o tema (claro/escuro)
- Conectar o evento `<<Modified>>` (ou `<KeyRelease>`) para acionar o preview ao vivo
- Adicionar scrollbar vertical sincronizada

CSS do editor no tema claro:
- Fundo: `#f6f8fa`, texto: `#24292f`, cursor: `#0969da`

CSS do editor no tema escuro:
- Fundo: `#0d1117`, texto: `#e6edf3`, cursor: `#58a6ff`

### 3. Implementar preview ao vivo

**Arquivo:** `main.py` — novo método `_schedule_preview`

- Ao receber evento de tecla no editor, cancelar timer anterior (`after_cancel`) e agendar novo (`after(300, self._update_preview)`)
- `_update_preview` lê o conteúdo do `tk.Text`, chama `_render()` com o texto atual
- Isso evita re-renderizações a cada tecla pressionada

### 4. Carregar arquivo no editor ao abrir

**Arquivo:** `main.py` — método `load_file` (modificar)

Após ler o conteúdo do arquivo:
1. Inserir o texto no widget `tk.Text` (limpar antes com `delete("1.0", tk.END)`)
2. Marcar como "não modificado" (`self._modified = False`)
3. Chamar `_render()` para o preview (comportamento atual mantido)

### 5. Salvar arquivo

**Arquivo:** `main.py` — novo método `save_file`

- Se `self.current_file` existir: escrever `text_widget.get("1.0", tk.END)` no arquivo (UTF-8)
- Atualizar `self._modified = False` e remover `*` do título
- Atalho: `Ctrl+S`

### 6. Salvar Como

**Arquivo:** `main.py` — novo método `save_file_as`

- Abrir `filedialog.asksaveasfilename` com `defaultextension=".md"`
- Escrever conteúdo no novo caminho
- Atualizar `self.current_file` e o título da janela
- Atalho: `Ctrl+Shift+S`

### 7. Rastrear alterações não salvas

**Arquivo:** `main.py` — atributo `self._modified`

- Inicializar como `False`
- Setar `True` ao primeiro `<<Modified>>` do editor
- Ao setar `True`: adicionar `*` no início do título (`* filename.md — Markdown Viewer`)
- Ao salvar: voltar para `False` e remover `*`
- No evento `WM_DELETE_WINDOW` (fechar janela) e em `open_file_dialog`: checar `_modified` e perguntar ao usuário se deseja salvar antes de sair/abrir outro arquivo

### 8. Criar novo arquivo

**Arquivo:** `main.py` — novo método `new_file`

- Checar alterações não salvas (mesma lógica do item 7)
- Limpar o editor e o preview
- Setar `self.current_file = None`
- Resetar título para `APP_TITLE`
- Atalho: `Ctrl+N`

### 9. Alternar modo editor (mostrar/ocultar painel de edição)

**Arquivo:** `main.py` — novo método `toggle_edit_mode`

- **Estado inicial sempre é visualização** (`self._edit_mode = False`)
- Ao ativar: trocar o `HtmlFrame` solto pelo `PanedWindow` (com editor + preview lado a lado)
- Ao desativar: voltar para `HtmlFrame` ocupando a janela inteira
- Checkbutton no menu reflete o estado atual
- Atalho: `Ctrl+E` ou `F2`
- **Não** persistir essa preferência — o app sempre abre em visualização, independente da sessão anterior

### 10. Atualizar o menu

**Arquivo:** `main.py` — método `_setup_menu`

Adicionar ao menu **Arquivo**:
```
Novo              Ctrl+N
Abrir...          Ctrl+O
──────────────
Salvar            Ctrl+S       (desabilitado se não houver arquivo/alterações)
Salvar Como...    Ctrl+Shift+S
──────────────
Recarregar        F5
──────────────
Sair              Esc
```

Adicionar ao menu **Visualizar**:
```
[x] Modo Edição   Ctrl+E
[x] Tema Escuro   Ctrl+D
```

### 11. Atualizar `_bind_keys`

**Arquivo:** `main.py` — método `_bind_keys`

Adicionar:
```python
self.bind("<Control-n>", lambda e: self.new_file())
self.bind("<Control-s>", lambda e: self.save_file())
self.bind("<Control-S>", lambda e: self.save_file_as())  # Ctrl+Shift+S
self.bind("<Control-e>", lambda e: self.toggle_edit_mode())
self.bind("<F2>",        lambda e: self.toggle_edit_mode())
```

---

## Ordem de Implementação Sugerida

| # | Tarefa | Complexidade |
|---|--------|-------------|
| 1 | Refatorar layout com `PanedWindow` | Média |
| 2 | Criar widget `tk.Text` como editor | Baixa |
| 3 | Carregar arquivo no editor ao abrir | Baixa |
| 4 | Preview ao vivo com debounce | Baixa |
| 5 | Salvar arquivo (Ctrl+S) | Baixa |
| 6 | Rastrear alterações não salvas + título `*` | Baixa |
| 7 | Aviso ao fechar/abrir com alterações pendentes | Baixa |
| 8 | Salvar Como (Ctrl+Shift+S) | Baixa |
| 9 | Novo arquivo (Ctrl+N) | Baixa |
| 10 | Toggle modo editor (Ctrl+E) | Média |
| 11 | Atualizar menu e atalhos | Baixa |
| 12 | Estilizar editor (tema claro/escuro) | Baixa |

---

## Dependências

Nenhuma dependência nova é necessária. Tudo usa tkinter puro (`tk.Text`, `tk.PanedWindow`), que já está disponível.

---

## Arquivos que serão modificados

| Arquivo | Tipo de mudança |
|---------|----------------|
| `main.py` | Único arquivo a modificar — todas as alterações ficam aqui |

---

## Considerações

- **Encoding:** sempre ler/escrever UTF-8 (já feito no `load_file`, manter no `save_file`)
- **Linha final:** `tk.Text.get("1.0", tk.END)` adiciona `\n` extra no final — remover com `.rstrip("\n") + "\n"` ao salvar
- **Recarregar (F5):** se houver alterações não salvas, perguntar antes de recarregar do disco
- **Sintaxe highlight:** fora do escopo deste plano (exigiria `pygments` + lógica de tags no `tk.Text`)
