import { Suspense } from "react";
import { Workspace } from "@/features/workspace";
export default function WorkspacePage() {
  return (
    <Suspense
      fallback={
        <main id="main" className="loading-state">
          Opening your workspace…
        </main>
      }
    >
      <Workspace />
    </Suspense>
  );
}
