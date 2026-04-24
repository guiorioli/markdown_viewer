# Markdown Viewer

Aplicação desktop leve para Windows que visualiza arquivos Markdown e JSON com suporte a tema claro/escuro, integração ao "Abrir com" do Explorer e compilação para `.exe` standalone.

## Funcionalidades

- Renderização completa de Markdown (cabeçalhos, tabelas, código, listas, blockquotes, imagens, links)
- Leitura e prettify de arquivos JSON com indentação e syntax highlight
- Busca no conteúdo com destaque de ocorrências (Ctrl+F)
- Tema claro e escuro com preferência persistida entre sessões
- Abertura via argumento de linha de comando ("Abrir com" do Windows)
- Diálogo de seleção de arquivo
- Recarregamento manual do arquivo atual
- Tela de boas-vindas quando nenhum arquivo está aberto

## Tecnologias

| Camada        | Tecnologia                          |
|---------------|-------------------------------------|
| Linguagem     | Python 3.14                         |
| UI            | tkinter (built-in) + tkinterweb     |
| Parser MD     | markdown2                           |
| Parser JSON   | json (built-in)                     |
| Distribuição  | PyInstaller (`.exe` único)          |

## Estrutura

```
markdown_viewer/
├── main.py           # Ponto de entrada da aplicação
├── requirements.txt  # Dependências pip
├── build.bat         # Script de compilação para .exe (Windows)
├── build.sh          # Script de compilação para .exe (Linux/Mac)
└── README.md
```

## Configuração persistida

A preferência de tema é salva em:

```
~/.markdown_viewer_config.json
```

## Como executar (desenvolvimento)

```bash
# Instalar dependências
python -m pip install -r requirements.txt

# Abrir um arquivo Markdown
python main.py caminho/para/arquivo.md

# Abrir um arquivo JSON (exibido com prettify)
python main.py caminho/para/arquivo.json

# Sem argumento — exibe tela de boas-vindas com diálogo de seleção
python main.py
```

## Como compilar (.exe)

```bat
build.bat
```

O executável gerado fica em `dist/markdown_viewer.exe`.

## Associar ao "Abrir com" no Windows

1. Clique com o botão direito em qualquer arquivo `.md`
2. Selecione **Abrir com > Escolher outro aplicativo**
3. Navegue até `dist/markdown_viewer.exe`
4. Marque **Sempre usar este aplicativo** e confirme

A partir daí, clicar duas vezes em qualquer `.md` abrirá o Markdown Viewer automaticamente.

## Atalhos

| Tecla    | Ação                          |
|----------|-------------------------------|
| Ctrl+O   | Abrir arquivo                 |
| F5       | Recarregar arquivo atual      |
| Ctrl+D   | Alternar tema claro/escuro    |
| Ctrl+F   | Abrir busca no conteúdo       |
| Escape   | Fechar busca / Fechar aplicação |

## Busca (Ctrl+F)

A busca abre uma barra na parte inferior da janela. Digite o termo desejado e pressione **Enter** para navegar entre as ocorrências. As correspondências são destacadas no texto. Pressione **Escape** para fechar a barra de busca.
