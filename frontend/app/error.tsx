"use client";
import { Button } from "@/components/ui/button";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main id="main" className="loading-state">
      <h1>Something interrupted your session.</h1>
      <p>Try loading this page again.</p>
      <Button onClick={reset}>Try again</Button>
    </main>
  );
}
