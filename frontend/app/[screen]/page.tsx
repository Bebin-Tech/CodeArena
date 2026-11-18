import { Suspense } from "react";
import { notFound } from "next/navigation";
import { AuthScreen, type AuthMode } from "@/features/auth-screen";
const screens = [
  "login",
  "register",
  "forgot-password",
  "reset-password",
  "verify-email",
];
export default async function AccountPage({
  params,
}: {
  params: Promise<{ screen: string }>;
}) {
  const { screen } = await params;
  if (!screens.includes(screen)) notFound();
  return (
    <Suspense
      fallback={
        <main id="main" className="loading-state" aria-busy="true">
          Preparing your workspace…
        </main>
      }
    >
      <AuthScreen mode={screen as AuthMode} />
    </Suspense>
  );
}
