import React, { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function App() {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCvFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!jobDescription.trim()) {
      alert("Por favor, cole a descrição da vaga.");
      return;
    }

    setIsLoading(true);

    const formData = new FormData();
    if (cvFile) {
      formData.append("cv_file", cvFile);
    }
    formData.append("job_description", jobDescription);

    try {
      const response = await fetch(`${API_BASE_URL}/optimize`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        // tenta extrair mensagem de erro detalhada do JSON
        let errorMessage = "Erro ao otimizar CV";
        try {
          const errorData = await response.json();
          if (errorData.message) errorMessage = errorData.message;
        } catch {
          // erro ao tentar ler JSON, mantem mensagem genérica
        }
        alert(errorMessage);
        return;
      }

      // sucesso: resposta é PDF (blob)
      const blob = await response.blob();

      // cria URL temporário para download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "cv_otimizado.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      alert("CV otimizado gerado com sucesso!");
    } catch (error: any) {
      alert("Erro inesperado: " + (error?.message || error));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "auto", padding: 20 }}>
      <h1>Otimização de CV para ATS</h1>

      <div style={{ marginBottom: 16 }}>
        <label>
          Envie seu CV em PDF exportado do LinkedIn:
          <input type="file" accept="application/pdf" onChange={handleFileChange} />
        </label>
      </div>

      <div style={{ marginBottom: 16 }}>
        <label>
          Cole a descrição da vaga:
          <textarea
            rows={6}
            style={{ width: "100%" }}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Cole aqui o job description..."
          />
        </label>
      </div>

      <button onClick={handleSubmit} disabled={isLoading} style={{ padding: "8px 16px" }}>
        {isLoading ? "Otimizando..." : "Gerar CV Otimizado"}
      </button>
    </div>
  );
}
