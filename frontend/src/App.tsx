import { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Domínio frontend configurado: 
// https://ats-optimizer-2.onrender.com

export default function App() {
  const [cvText, setCvText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!cvText.trim() || !jobDescription.trim()) {
      alert("Por favor, preencha o texto do CV e a descrição da vaga.");
      return;
    }

    setIsLoading(true);

    const formData = new FormData();
    formData.append("cv_text", cvText);
    formData.append("job_description", jobDescription);

    try {
      const response = await fetch(`${API_BASE_URL}/optimize`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = "Erro ao otimizar CV.";
        try {
          const errorData = await response.json();
          if (errorData.message) errorMessage = errorData.message;
        } catch {
          // Falha ao ler JSON — mantém mensagem genérica
        }
        alert(errorMessage);
        return;
      }

      const blob = await response.blob();
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
          Cole o texto do seu CV:
          <textarea
            rows={8}
            style={{ width: "100%", marginTop: 8 }}
            value={cvText}
            onChange={(e) => setCvText(e.target.value)}
            placeholder="Cole aqui o texto do seu currículo..."
          />
        </label>
      </div>

      <div style={{ marginBottom: 16 }}>
        <label>
          Cole a descrição da vaga:
          <textarea
            rows={6}
            style={{ width: "100%", marginTop: 8 }}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Cole aqui o job description..."
          />
        </label>
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading}
        style={{
          padding: "10px 20px",
          backgroundColor: isLoading ? "#ccc" : "#0070f3",
          color: "#fff",
          border: "none",
          borderRadius: 4,
          cursor: isLoading ? "not-allowed" : "pointer",
        }}
      >
        {isLoading ? "Otimizando..." : "Gerar CV Otimizado"}
      </button>
    </div>
  );
}
