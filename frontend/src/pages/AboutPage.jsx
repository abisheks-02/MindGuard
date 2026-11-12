export default function AboutPage() {
  return (
    <div className="card max-w-3xl mx-auto flex flex-col gap-6 p-8">
      <h1 className="text-2xl font-bold text-navy">About MindGuard</h1>
      <p className="text-slate-700 leading-relaxed">
        MindGuard is a full-stack, production-ready mental health risk detection and support platform 
        specifically built for Tamil-English code-mixed social media text.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
          <h2 className="font-semibold text-teal mb-2">AI Severity Detection</h2>
          <p className="text-sm text-slate-600">
            Powered by a fine-tuned MuRIL model with SHAP token-level explainability to ensure transparent AI decisions.
          </p>
        </div>
        
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
          <h2 className="font-semibold text-teal mb-2">CBT Chatbot</h2>
          <p className="text-sm text-slate-600">
            Uses Llama-3.2-3B-Instruct to provide empathetic, auto-generated Cognitive Behavioral Therapy support in code-mixed language.
          </p>
        </div>
        
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
          <h2 className="font-semibold text-teal mb-2">Professional Escalation</h2>
          <p className="text-sm text-slate-600">
            Automatically routes severe cases to verified Tamil Nadu helplines (iCall, SNEHI, Vandrevala, NIMHANS).
          </p>
        </div>
        
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
          <h2 className="font-semibold text-teal mb-2">Mood Tracking</h2>
          <p className="text-sm text-slate-600">
            Persists a 7-day mood history and uses AI to generate a personalized weekly wellness plan.
          </p>
        </div>
      </div>
    </div>
  );
}
