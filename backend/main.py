from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from fpdf import FPDF
import io
import os
import openai
import httpx

load_dotenv()
print(f"Chave OpenAI: {os.getenv('OPENAI_API_KEY')}")
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

origins = [
    "https://ats-optimizer-2.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
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
async def optimize_cv(cv_file: UploadFile = File(...), job_description: str = Form(...)):
    print("📥 Rota /optimize acionada — iniciando processamento...")

    # 1) Verificar conexão com OpenAI
    if not await check_openai_api():
        return JSONResponse(
            status_code=503,
            content={"status": "fail", "message": "Falha na conexão com a API OpenAI."}
        )

    # 2) Ler e validar PDF (OCULTO: apenas simula texto)
    try:
        # contents = await cv_file.read()
        # pdf_reader = PdfReader(io.BytesIO(contents))
        # cv_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
        # if not cv_text.strip():
        #     return JSONResponse(
        #         status_code=400,
        #         content={"status": "fail", "message": "PDF não pôde ser lido ou está vazio."}
        #     )
        cv_text = "EXEMPLO DE TEXTO DO CURRÍCULO PARA TESTE"
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"status": "fail", "message": f"Erro ao ler PDF: {str(e)}"}
        )

    # 3) Enviar prompt para OpenAI
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
    except openai.error.AuthenticationError as e:
        return JSONResponse(
            status_code=401,
            content={"status": "fail", "message": "Chave de API OpenAI inválida ou expirada."}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "fail", "message": f"Erro ao enviar prompt para OpenAI: {str(e)}"}
        )

    # 4) Validar resposta OpenAI
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

    # Gerar PDF otimizado
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
