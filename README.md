# Gerador de Certificados — Escola

## Sobre o projeto

Este projeto visa automatizar o processo de criar certificados personalizados, tendo sido criado para facilitar a criação de diplomas para alunos formandos na escola em que estagio.  
Em vez de editar cada certificado manualmente, o sistema insere automaticamente os nomes em cima de um template, utilizando dados de uma planilha (Excel ou CSV) ou nomes digitados diretamente no aplicativo.

Seus resultados podem ser exportados como PDF individuais ou um único PDF para impressão.

<img width="1780" height="937" alt="image" src="https://github.com/user-attachments/assets/29321f72-ae03-4a6f-bb74-ce97b8261041" />


---

## Como funciona

O usuário envia uma imagem modelo do certificado.  
Em seguida, escolhe a origem dos nomes:
- **Planilha (.xlsx / .csv):** um arquivo com uma coluna chamada `nome`, seguida pelo nome dos alunos. Se a coluna não existir, a primeira coluna é usada. Em CSV, o separador (`;` ou `,`) é detectado automaticamente.
- **Digitar manualmente:** digite um nome e aperte **Enter** para adicioná-lo à lista. Nomes podem ser removidos individualmente ou a lista inteira pode ser limpa.

O aplicativo ajusta automaticamente o tamanho e posição dos nomes conforme as configurações que o usuário realizar.  
É possível pré-visualizar o resultado final.  
Ao clicar em Gerar certificado, o programa cria o(s) PDF(s).

---

## Estrutura do código

- `app_certificados.py`: interface (Streamlit).
- `gerador_core.py`: regras de negócio, sem dependência do Streamlit. Organizado em fontes, nomes, renderização e exportação.

Toda origem de nomes apenas produz uma lista de nomes. Para adicionar uma nova origem, basta criar uma função em `gerador_core.py` que devolva essa lista (passando por `normalizar_nomes`) e uma opção na interface. A geração e a exportação não mudam.

---

## Fontes utilizadas

O aplicativo permite escolher diferentes fontes disponíveis localmente.  
Para isso, basta criar uma pasta chamada **`fonts`** no mesmo diretório do projeto e colocar nela os arquivos `.ttf` ou `.otf` das fontes desejadas.  
Essas fontes aparecerão automaticamente na lista de seleção dentro do aplicativo.

---

## Instalação e execução

**Acesso online:**  
[https://certificadorv1.streamlit.app/](https://certificadorv1.streamlit.app/)

---

**Acesso remoto:**

Crie o ambiente:
```bash
python -m venv venv
```

Ative o ambiente:
```bash
venv/Scripts/activate
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

Execute:
```bash
streamlit run app_certificados.py
```

---

Desenvolvido por Arthur como ferramenta de automação para o ambiente escolar.  
Criado com Python + Streamlit, com foco em produtividade e usabilidade.
