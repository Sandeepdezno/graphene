import { useRef, useState } from "react";
import { api } from "../../shared/api-client";

type DropzoneProps = {
  onJobStarted: (jobId: string) => void;
};

function errorDetail(error: unknown): string {
  const detail = (error as { detail?: unknown } | undefined)?.detail;
  return typeof detail === "string" ? detail : "Upload failed. Please try again.";
}

export function Dropzone({ onJobStarted }: DropzoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File): Promise<void> {
    setError(null);
    if (!file.name.toLowerCase().endsWith(".xlsx")) {
      setError("Only .xlsx workbooks are accepted.");
      return;
    }
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    const { data, error: apiError } = await api.POST("/api/v1/import/excel", {
      body: form as unknown as { file: string },
    });
    setUploading(false);
    if (apiError || !data) {
      setError(errorDetail(apiError));
      return;
    }
    onJobStarted(data.job_id);
  }

  function onDrop(event: React.DragEvent<HTMLButtonElement>): void {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files[0];
    if (file) void handleFile(file);
  }

  return (
    <div className="flex h-full w-full items-center justify-center p-8">
      <div className="w-full max-w-xl">
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={[
            "flex w-full flex-col items-center gap-4 rounded-2xl border-2 border-dashed px-8 py-16 text-center transition-colors",
            dragging
              ? "border-accent bg-surface-raised"
              : "border-hairline bg-surface hover:border-accent",
          ].join(" ")}
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.4"
            className={dragging ? "h-12 w-12 text-accent" : "h-12 w-12 text-muted"}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V4m0 0L8 8m4-4l4 4" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 15v3.5A1.5 1.5 0 005.5 20h13a1.5 1.5 0 001.5-1.5V15" />
          </svg>
          <div className="space-y-1">
            <p className="text-base font-medium text-ink">
              {uploading ? "Uploading…" : "Drop your SAP workbook here"}
            </p>
            <p className="text-sm text-muted">
              or <span className="text-accent">click to browse</span> · .xlsx only
            </p>
          </div>
        </button>

        <input
          ref={inputRef}
          type="file"
          accept=".xlsx"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void handleFile(file);
            e.target.value = "";
          }}
        />

        {error && (
          <div className="mt-4 rounded-lg border border-risk-high bg-surface-raised px-4 py-3">
            <p className="text-sm text-risk-high">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
