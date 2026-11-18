import Link from "next/link";
export default function NotFound() {
  return (
    <main id="main" className="loading-state">
      <h1>That page isn’t in the arena.</h1>
      <Link className="text-link" href="/">
        Return home
      </Link>
    </main>
  );
}
