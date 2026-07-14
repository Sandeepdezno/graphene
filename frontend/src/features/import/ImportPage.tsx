import { useState } from "react";
import { Dropzone } from "./Dropzone";
import { Processing } from "./Processing";

export function ImportPage() {
  const [jobId, setJobId] = useState<string | null>(null);

  if (jobId) {
    return <Processing jobId={jobId} onRetry={() => setJobId(null)} />;
  }
  return <Dropzone onJobStarted={setJobId} />;
}
