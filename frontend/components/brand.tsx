import Link from "next/link";
import { Terminal } from "lucide-react";
export function Brand() {
  return (
    <Link href="/" className="brand" aria-label="CodeArena home">
      <span className="brand-icon">
        <Terminal size={21} strokeWidth={2.4} />
      </span>
      code<span className="brand-accent">arena</span>
      <span className="brand-dot">.</span>
    </Link>
  );
}
