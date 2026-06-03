# UC06 - Situação de Aprendizagem: Implantação em Nuvem com Integração via API

## 1. Identificação
- **Equipe:** Grupo 2º Módulo
- **Integrantes:** Caroline Bento e Janaina Santos
- **Turma/Turno:** 2º Módulo
- **Data de entrega:** 02/06/2026

## 2. Contexto do MVP
Este projeto entrega um **MVP de solicitações internas** (ex.: manutenção/TI/suporte), com uma **API** para registro e acompanhamento de solicitações, persistência de dados e integração com a API pública do ViaCEP para busca automática de endereços.

## 3. Link da aplicação em nuvem
- **URL:** [Vamos colar o link do Render aqui depois de publicar!]
- **Como validar rapidamente:** Acesse a URL da nuvem acrescentando `/docs` no final para abrir a documentação interativa (Swagger UI) e testar os endpoints.

## 4. Requisitos não funcionais adotados (resumo)

### Qualidade
- RNF-Q1: O sistema deve gerar sua própria documentação técnica de forma dinâmica.
  - Evidência: Uso do framework FastAPI que gera a interface Swagger UI automaticamente na rota `/docs`.
- RNF-Q2: O sistema deve ter persistência de dados simples para o MVP.
  - Evidência: Implementação do banco de dados relacional embutido SQLite (arquivo `banco.db`).

### Integridade
- RNF-I1: O sistema não pode aceitar solicitações sem título, descrição ou com CEPs incompletos.
  - Evidência: Uso da biblioteca Pydantic com o método `Field(..., min_length=X)` nas classes de modelo.
- RNF-I2: O CEP deve ser limpo e formatado antes de ser enviado para a integração externa.
  - Evidência: Uso da função `.replace("-", "")` no código antes de acionar o ViaCEP.

### Usabilidade (técnica)
- RNF-U1: As respostas de erro da API devem ser compreensíveis para o usuário final.
  - Evidência: Uso de `HTTPException` retornando mensagens em português como "CEP inválido ou não encontrado".
- RNF-U2: O formato de resposta da criação do chamado deve incluir todos os dados processados e formatados.
  - Evidência: A rota `POST` retorna um JSON claro contendo o logradouro e UF processados.

### Segurança da informação
- RNF-S1: O repositório não deve conter exposição de chaves ou segredos.
  - Evidência: Criação do arquivo `.env.example` e ausência de hardcoding de credenciais sensíveis.
- RNF-S2: Os dados de entrada (como o CEP) devem ter limite rígido de caracteres para evitar injeção de dados longos (buffer overflow).
  - Evidência: O campo `cep` possui a restrição de `max_length=9`.

## 5. Tecnologias e justificativas
- **Linguagem:** Python
- **Framework:** FastAPI
- **Bibliotecas relevantes:** Uvicorn (servidor local), Requests (consumo de API externa) e Pydantic (validação de dados).
- **Persistência:** SQLite
- **Nuvem/Deploy:** Render (Web Service Gratuito)

**Justificativa vinculada aos RNFs:**
- O Python + FastAPI foi escolhido pois atende aos RNF-Q1 e RNF-I1, permitindo validação rápida de integridade e geração automática de documentação para usabilidade técnica.
- O SQLite atende ao RNF-Q2, facilitando o deploy na nuvem sem necessidade de configurar servidores de banco de dados pesados neste MVP.

## 6. Integração via API (o que foi integrado)
- **Serviço externo utilizado:** ViaCEP (API pública de consulta de CEPs).
- **Tipo de integração:** Consumo
**Fluxo integrado:**
1) O usuário envia uma solicitação com Título, Descrição e CEP.
2) O sistema aciona o serviço externo via método GET para validar o CEP e resgatar Rua, Cidade e Estado.
3) O sistema junta as informações, salva no banco e retorna a solicitação enriquecida para o cliente.

## 7. Endpoints do MVP (API)
| Método | Rota | Descrição |
|---|---|---|
| POST | /solicitacoes | Cria uma solicitação, busca o endereço via integração e salva no banco. |
| GET | /solicitacoes | Lista todas as solicitações cadastradas no banco de dados. |

## 8. Como executar localmente
### Pré-requisitos
- Python 3.x
### Passos
1. Instale as dependências: `pip install fastapi uvicorn requests pydantic`
2. Execute o servidor: `uvicorn main:app --reload`
3. Acesse no navegador: `http://127.0.0.1:8000/docs`
