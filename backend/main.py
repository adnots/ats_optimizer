from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
import io

app = FastAPI()

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, troque por origem específica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota raiz para verificação
@app.get("/")
def read_root():
    return {"message": "API de Otimização de CV está rodando!"}

# Rota principal de otimização
@app.post("/optimize")
async def optimize_cv(cv_file: UploadFile, job_description: str = Form(...)):
    contents = await cv_file.read()
    pdf_reader = PdfReader(io.BytesIO(contents))
    text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

    # Simula otimização
    optimized = (
        f"CV original (primeiros 500 caracteres):\n{text[:500]}...\n\n"
        f"Job Description (primeiros 300 caracteres):\n{job_description[:300]}...\n\n"
        "CV otimizado: (exemplo)"
    )
    return JSONResponse({"optimized_cv": optimized})
