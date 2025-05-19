import React, { useState } from "react";

export default function App() {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [optimizedCV, setOptimizedCV] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCvFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!cvFile || !jobDescription.trim()) {
      alert("Por favor, envie o PDF do CV e cole a descrição da vaga.");
      return;
    }

    setIsLoading(true);

    const formData = new FormData();
    formData.append("cv_file", cvFile);
    formData.append("job_description", jobDescription);

    try {
      const response = await fetch("http://localhost:8000/optimize", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Erro ao otimizar CV");

      const data = await response.json();
      setOptimizedCV(data.optimized_cv);
    } catch (error) {
      console.error(error);
      alert("Erro ao gerar o CV otimizado.");
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

      {optimizedCV && (
        <div style={{ marginTop: 24, whiteSpace: "pre-wrap", background: "#f5f5f5", padding: 16, borderRadius: 8 }}>
          <h2>Resultado:</h2>
          <pre>{optimizedCV}</pre>
        </div>
      )}
    </div>
  );
}
