from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
import sqlite3

app = FastAPI(
    title="API de Solicitações Internas",
    description="Sistema para registro e acompanhamento de chamados de manutenção com Banco de Dados."
)

# 1. LIBERANDO A CATRACA (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ROTA PARA MOSTRAR A TELA HTML NA PÁGINA INICIAL
@app.get("/", response_class=HTMLResponse)
def mostrar_tela():
    try:
        with open("index.html", "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        return "<h1>Tela não encontrada. Verifique se o arquivo index.html está na pasta!</h1>"

# 3. CONFIGURAÇÃO DO BANCO DE DADOS
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

# 4. REGRA DE INTEGRIDADE
class NovaSolicitacao(BaseModel):
    titulo: str = Field(..., min_length=3)
    descricao: str = Field(..., min_length=5)
    cep: str = Field(..., min_length=8, max_length=9)

# 5. ROTA: CRIAR CHAMADO
@app.post("/solicitacoes", status_code=201)
def criar_solicitacao(solicitacao: NovaSolicitacao):
    cep_limpo = solicitacao.cep.replace("-", "")
    
    resposta_viacep = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
    if resposta_viacep.status_code != 200 or "erro" in resposta_viacep.json():
        raise HTTPException(status_code=400, detail="CEP inválido.")
    
    dados_endereco = resposta_viacep.json()
    local_completo = f"{dados_endereco['logradouro']}, {dados_endereco['localidade']} - {dados_endereco['uf']}"
    
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO solicitacoes (titulo, descricao, local_atendimento, status) VALUES (?, ?, ?, ?)",
        (solicitacao.titulo, solicitacao.descricao, local_completo, "Aberto")
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    conexao.close()
    
    return {"mensagem": "Sucesso", "id": novo_id}

# 6. ROTA: LISTAR CHAMADOS
@app.get("/solicitacoes")
def listar_solicitacoes():
    conexao = sqlite3.connect("banco.db")
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM solicitacoes")
    linhas = cursor.fetchall()
    conexao.close()
    return [dict(linha) for linha in linhas]

# 7. ROTA: MUDAR STATUS (O botão novo!)
@app.put("/solicitacoes/{id}")
def mudar_status(id: int):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    
    cursor.execute("SELECT status FROM solicitacoes WHERE id = ?", (id,))
    resultado = cursor.fetchone()
    
    if not resultado:
        conexao.close()
        raise HTTPException(status_code=404, detail="Chamado não encontrado.")
        
    novo_status = "Fechado" if resultado[0] == "Aberto" else "Aberto"
    
    cursor.execute("UPDATE solicitacoes SET status = ? WHERE id = ?", (novo_status, id))
    conexao.commit()
    conexao.close()
    
    return {"mensagem": f"Status atualizado para {novo_status}"}
