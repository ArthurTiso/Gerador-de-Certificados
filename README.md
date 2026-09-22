# Gerador de Certificados — Escola

## Sobre o projeto

Este projeto visa automatizar o processo de criar certificados personalizados, tendo sido criado para facilitar a criação de diplomas para alunos formandos na escola em que estagio.  
Em vez de editar cada certificado manualmente, o sistema insere automaticamente os nomes em cima de um template, utilizando dados de uma planilha Excel.

Seus resultados podem ser exportados como PDF individuais ou um único PDF para impressão.

<img width="1780" height="937" alt="image" src="https://github.com/user-attachments/assets/29321f72-ae03-4a6f-bb74-ce97b8261041" />


---

## Como funciona

O usuário envia uma imagem modelo do certificado.  
É enviada também uma planilha Excel contendo uma coluna chamada 'nome', seguida pelo nome dos alunos.  
O aplicativo ajusta automaticamente o tamanho e posição dos nomes conforme as configurações que o usuário realizar.  
É possível pré-visualizar o resultado final.  
Ao clicar em Gerar certificado, o programa cria o(s) PDF(s).

---

## Fontes utilizadas

O aplicativo permite escolher diferentes fontes disponíveis localmente.  
Para isso, basta criar uma pasta chamada **`fonts`** no mesmo diretório do projeto e colocar nela os arquivos `.ttf` das fontes desejadas.  
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
