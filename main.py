from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests
import sqlite3 # <- Trazendo o SQLite para o nosso projeto!

app = FastAPI(
    title="API de Solicitações Internas",
    description="Sistema para registro e acompanhamento de chamados de manutenção com Banco de Dados."
)

# --- 1. CONFIGURAÇÃO DO BANCO DE DADOS SQLITE ---
# Ao iniciar, o Python cria um arquivo 'banco.db' e monta a nossa tabela (se ela não existir)
conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS solicitacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT NOT NULL,
        local_atendimento TEXT NOT NULL,
        status TEXT NOT NULL
    )
''')
conexao.commit()
conexao.close()
# ------------------------------------------------

# 2. Regra de INTEGRIDADE (Obriga o preenchimento correto)
class NovaSolicitacao(BaseModel):
    titulo: str = Field(..., min_length=3, description="Título do chamado (ex: Computador não liga)")
    descricao: str = Field(..., min_length=5, description="Descrição detalhada do problema")
    cep: str = Field(..., min_length=8, max_length=9, description="CEP da unidade para a visita técnica")

# 3. Rota para CRIAR a solicitação e SALVAR no Banco de Dados
@app.post("/solicitacoes", status_code=201)
def criar_solicitacao(solicitacao: NovaSolicitacao):
    
    cep_limpo = solicitacao.cep.replace("-", "")
    
    # INTEGRAÇÃO: Consultando a API pública do ViaCEP
    url_viacep = f"https://viacep.com.br/ws/{cep_limpo}/json/"
    resposta_viacep = requests.get(url_viacep)
    
    if resposta_viacep.status_code != 200 or "erro" in resposta_viacep.json():
        raise HTTPException(status_code=400, detail="CEP inválido ou não encontrado. Verifique o número e tente novamente.")
    
    dados_endereco = resposta_viacep.json()
    local_completo = f"{dados_endereco['logradouro']}, {dados_endereco['localidade']} - {dados_endereco['uf']}"
    status_inicial = "Aberto"
    
    # --- SALVANDO NO BANCO DE DADOS ---
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO solicitacoes (titulo, descricao, local_atendimento, status) VALUES (?, ?, ?, ?)",
        (solicitacao.titulo, solicitacao.descricao, local_completo, status_inicial)
    )
    conexao.commit()
    novo_id = cursor.lastrowid # Pega o ID numérico que acabou de ser gerado
    conexao.close()
    
    return {
        "id": novo_id,
        "titulo": solicitacao.titulo,
        "descricao": solicitacao.descricao,
        "local_atendimento": local_completo,
        "status": status_inicial,
        "mensagem": "Sucesso! Chamado gravado no Banco de Dados SQLite."
    }

# 4. Rota para LISTAR as solicitações lendo do Banco de Dados
@app.get("/solicitacoes")
def listar_solicitacoes():
    conexao = sqlite3.connect("banco.db")
    conexao.row_factory = sqlite3.Row # Ajuda a formatar a resposta bonitinha
    cursor = conexao.cursor()
    
    # Busca tudo na tabela
    cursor.execute("SELECT * FROM solicitacoes")
    linhas = cursor.fetchall()
    conexao.close()
    
    # Converte os dados do banco para o formato que a API e o navegador entendem
    resultado = [dict(linha) for linha in linhas]
    return resultado