from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv
from fpdf import FPDF
import openai  # ✅ ESSA LINHA É ESSENCIAL
import io
import os
import httpx


# Carrega variáveis de ambiente e chave da OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print(f"Chave OpenAI carregada: {'OK' if openai.api_key else 'FALHA'}")

app = FastAPI()

# Corrija para permitir qualquer origem (para teste) — use apenas para depuração!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem (atenção: não recomendado em produção)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API de Otimização de CV com IA está ativa."}

@app.get("/healthcheck")
def healthcheck():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "OPENAI_API_KEY não configurada"}
    return {"status": "ok", "openai_configurada": True}

async def check_openai_api():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {openai.api_key}"},
                timeout=5
            )
            return response.status_code == 200
    except Exception:
        return False

@app.post("/optimize")
async def optimize_cv(
    cv_text: str = Form(...),
    job_description: str = Form(...)
):
    print("📥 Rota /optimize acionada — iniciando processamento...")

    # Verifica se a chave da OpenAI está configurada
    if not openai.api_key:
        return JSONResponse(
            status_code=503,
            content={"status": "fail", "message": "OPENAI_API_KEY não configurada no backend."}
        )

    if not await check_openai_api():
        return JSONResponse(
            status_code=503,
            content={"status": "fail", "message": "Falha na conexão com a API OpenAI."}
        )

    if not cv_text.strip():
        return JSONResponse(
            status_code=400,
            content={"status": "fail", "message": "Texto do CV não pode ser vazio."}
        )

    prompt = f"""
Você é um especialista em RH com foco em currículos otimizados para ATS (Applicant Tracking Systems).
Recebeu o seguinte CV:

{cv_text[:2000]}

E a seguinte descrição de vaga:

{job_description[:1500]}

Com base nisso, reescreva e otimize o CV, adaptando-o para essa vaga, destacando os pontos relevantes.
Não invente informações, apenas reorganize, ajuste a linguagem e destaque habilidades e experiências alinhadas.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
    except openai.error.AuthenticationError:
        return JSONResponse(
            status_code=401,
            content={"status": "fail", "message": "Chave de API OpenAI inválida ou expirada."}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "fail", "message": f"Erro ao enviar prompt para OpenAI: {str(e)}"}
        )

    try:
        optimized_text = response["choices"][0]["message"]["content"]
        if not optimized_text.strip():
            return JSONResponse(
                status_code=500,
                content={"status": "fail", "message": "Resposta da OpenAI está vazia."}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "fail", "message": f"Erro ao processar resposta da OpenAI: {str(e)}"}
        )

    # Gera PDF com o texto otimizado
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in optimized_text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    headers = {
        "Content-Disposition": 'attachment; filename="cv_otimizado.pdf"'
    }

    return StreamingResponse(pdf_output, media_type="application/pdf", headers=headers)
