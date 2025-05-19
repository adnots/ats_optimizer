from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from fpdf import FPDF
import io
import os
import openai

# Carrega variáveis de ambiente do .env-
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Instância do FastAPI
app = FastAPI()

# Configuração de CORS (libera requisições de qualquer origem)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API de Otimização de CV com IA está ativa."}

@app.post("/optimize")
async def optimize_cv(cv_file: UploadFile, job_description: str = Form(...)):
    try:
        # Leitura do conteúdo do arquivo PDF enviado
        contents = await cv_file.read()
        pdf_reader = PdfReader(io.BytesIO(contents))
        cv_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

        # Monta prompt para otimização via OpenAI
        prompt = f"""
Você é um especialista em RH com foco em currículos otimizados para ATS (Applicant Tracking Systems).
Recebeu o seguinte CV:

{cv_text[:2000]}

E a seguinte descrição de vaga:

{job_description[:1500]}

Com base nisso, reescreva e otimize o CV, adaptando-o para essa vaga, destacando os pontos relevantes.
Não invente informações, apenas reorganize, ajuste a linguagem e destaque habilidades e experiências alinhadas.
        """

        # Chamada à OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        optimized_text = response["choices"][0]["message"]["content"]

        # Geração do PDF otimizado
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

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
