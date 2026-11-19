"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Eye,
  EyeOff,
  Github,
  Loader2,
  ShieldCheck,
} from "lucide-react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui/button";
import { api } from "@/services/api";
import { email, password, registrationSchema } from "@/lib/validation";

export type AuthMode =
  "login" | "register" | "forgot-password" | "reset-password" | "verify-email";
const copy = {
  login: [
    "WELCOME BACK",
    "Back to your next chapter.",
    "Sign in to your CodeArena workspace.",
    "Sign in",
  ],
  register: [
    "WELCOME TO THE ARENA",
    "Great things start here.",
    "Create your account. Make your next move.",
    "Create account",
  ],
  "forgot-password": [
    "LET’S GET YOU BACK",
    "Forgot your password?",
    "We’ll email you a secure link to reset it.",
    "Send reset link",
  ],
  "reset-password": [
    "A FRESH START",
    "Set a new password.",
    "Choose a strong password you haven’t used before.",
    "Update password",
  ],
  "verify-email": [
    "ONE LAST STEP",
    "Make it official.",
    "Verify your email to unlock your workspace.",
    "Verify email",
  ],
};
export function AuthScreen({ mode }: { mode: AuthMode }) {
  const router = useRouter();
  const search = useSearchParams();
  const token = search.get("token");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [visible, setVisible] = useState(false);
  const providers = useQuery({
    queryKey: ["providers"],
    queryFn: () => api<{ github: boolean; email?: boolean }>("/auth/providers"),
  });
  const schema: z.ZodType<
    Record<string, string>,
    Record<string, string>
  > = mode === "register"
    ? registrationSchema
    : mode === "login"
      ? z.object({ email, password: z.string().min(1, "Enter your password.") })
      : mode === "reset-password"
        ? z.object({ password })
        : mode === "verify-email" && token
          ? z.object({})
          : z.object({ email });
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Record<string, string>>({
    resolver: zodResolver(schema),
    defaultValues: { user_type: "developer", institution: "" },
  });
  async function submit(values: Record<string, string>) {
    setError("");
    setNotice("");
    try {
      if (mode === "reset-password" && !token)
        throw new Error(
          "This link is missing its token. Request a new reset link.",
        );
      const path =
        mode === "verify-email" && !token ? "resend-verification" : mode;
      const payload =
        mode === "verify-email" && token
          ? { token }
          : mode === "reset-password"
            ? { ...values, token }
            : values;
      const result = await api<{ message?: string }>(`/auth/${path}`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (mode === "login") {
        router.replace("/workspace");
        router.refresh();
        return;
      }
      setNotice(
        mode === "register"
          ? "Check your inbox for a verification link. Once verified, you can sign in."
          : result.message || "Done.",
      );
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Unable to continue. Please retry.",
      );
    }
  }
  const showEmail =
    mode !== "reset-password" && !(mode === "verify-email" && token);
  function field(
    name: string,
    label: string,
    type = "text",
    placeholder = "",
    autoComplete = "",
  ) {
    return (
      <div className="field" key={name}>
        <label htmlFor={name}>{label}</label>
        <div className="input-wrap">
          <input
            id={name}
            {...register(name)}
            type={type === "password" && visible ? "text" : type}
            placeholder={placeholder}
            autoComplete={autoComplete}
            aria-invalid={Boolean(errors[name])}
            aria-describedby={errors[name] ? `${name}-error` : undefined}
          />
          {type === "password" && (
            <button
              className="password-toggle"
              type="button"
              onClick={() => setVisible(!visible)}
              aria-label={visible ? "Hide password" : "Show password"}
            >
              {visible ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          )}
        </div>
        {errors[name] && (
          <span className="field-error" id={`${name}-error`}>
            {String(errors[name]?.message)}
          </span>
        )}
      </div>
    );
  }
  const oauthError = search.get("error");
  const emailUnavailable =
    providers.data?.email === false &&
    (mode === "register" ||
      mode === "forgot-password" ||
      (mode === "verify-email" && !token));
  return (
    <div className="auth-layout">
      <aside className="auth-aside">
        <Brand />
        <div className="auth-manifesto">
          <span className="eyebrow">THE NEXT VERSION OF YOU</span>
          <h2>
            Curiosity.
            <br />
            Commitment.
            <br />
            <span>Possibility.</span>
          </h2>
          <p>
            Every developer has a next chapter.
            <br />
            This is where yours begins.
          </p>
          <div className="manifesto-code">
            <span className="syntax-muted">// a little better, every day</span>
            <br />
            <span className="syntax-violet">while</span> (curious) {"{"}
            <br />
            {"  "}learn();
            <br />
            {"  "}build();
            <br />
            {"  "}repeat();
            <br />
            {"}"}
          </div>
        </div>
        <div className="aside-footer">
          <ShieldCheck size={16} /> Your skills. Your identity. Your arena.
        </div>
      </aside>
      <main id="main" className="auth-main">
        <Link href="/" className="back-link">
          <ArrowLeft size={16} /> Back to CodeArena
        </Link>
        <div className="auth-form-shell">
          <span className="eyebrow">{copy[mode][0]}</span>
          <h1>{copy[mode][1]}</h1>
          <p className="muted">{copy[mode][2]}</p>
          {oauthError && (
            <div className="alert alert-error" role="alert">
              {oauthError === "existing-account"
                ? "An account already uses that email. Sign in with your password; automatic account linking is disabled."
                : "GitHub sign-in could not be completed. Please try again."}
            </div>
          )}
          {notice ? (
            <div className="success-state" role="status">
              <CheckCircle2 size={36} />
              <h2>
                {mode === "register" ? "Check your inbox." : "You’re all set."}
              </h2>
              <p>{notice}</p>
              <Button asChild>
                <Link href="/login">
                  Go to sign in <ArrowRight size={16} />
                </Link>
              </Button>
              {mode === "register" && (
                <Link href="/verify-email" className="text-link">
                  Need another verification email?
                </Link>
              )}
            </div>
          ) : (
            <>
              <form onSubmit={handleSubmit(submit)} noValidate>
                {emailUnavailable && (
                  <div className="alert alert-error" role="status">
                    Account email delivery is not configured on this deployment
                    yet. Registration and recovery will be available after email
                    setup is complete.
                  </div>
                )}
                {mode === "register" &&
                  field(
                    "full_name",
                    "Full name",
                    "text",
                    "Alex Morgan",
                    "name",
                  )}
                {showEmail &&
                  field(
                    "email",
                    "Email address",
                    "email",
                    "you@example.com",
                    "email",
                  )}
                {["login", "register", "reset-password"].includes(mode) && (
                  <>
                    {field(
                      "password",
                      mode === "reset-password" ? "New password" : "Password",
                      "password",
                      mode === "login"
                        ? "Enter your password"
                        : "At least 12 characters",
                      mode === "login" ? "current-password" : "new-password",
                    )}
                    {mode !== "login" && (
                      <p className="field-help">
                        12–128 characters, including a letter and a number.
                      </p>
                    )}
                  </>
                )}
                {mode === "register" && (
                  <>
                    <div className="field">
                      <label htmlFor="user_type">I’m joining as a</label>
                      <select id="user_type" {...register("user_type")}>
                        <option value="developer">Developer</option>
                        <option value="student">Student</option>
                        <option value="candidate">Candidate</option>
                      </select>
                    </div>
                    {field(
                      "country",
                      "Country",
                      "text",
                      "India",
                      "country-name",
                    )}
                    {field(
                      "institution",
                      "Institution or company (optional)",
                      "text",
                      "Where you learn or build",
                      "organization",
                    )}
                  </>
                )}
                {mode === "login" && (
                  <div className="form-aux">
                    <span>Let’s pick up where you left off.</span>
                    <Link href="/forgot-password">Forgot password?</Link>
                  </div>
                )}
                {mode === "verify-email" && token && (
                  <div className="verify-note">
                    <ShieldCheck size={28} />
                    <p>
                      Confirm that this email address belongs to you. The link
                      can only be used once.
                    </p>
                  </div>
                )}
                {error && (
                  <div className="alert alert-error" role="alert">
                    {error}
                  </div>
                )}
                <Button
                  className="full-width"
                  type="submit"
                  disabled={isSubmitting || emailUnavailable}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="spin" size={17} /> Working…
                    </>
                  ) : (
                    <>
                      {mode === "verify-email" && !token
                        ? "Send verification email"
                        : copy[mode][3]}{" "}
                      <ArrowRight size={17} />
                    </>
                  )}
                </Button>
              </form>
              {["login", "register"].includes(mode) && (
                <>
                  <div className="divider">
                    <span>or continue with</span>
                  </div>
                  {providers.data?.github ? (
                    <Button variant="outline" asChild className="full-width">
                      <a href="/api/v1/auth/github">
                        <Github size={18} /> GitHub
                      </a>
                    </Button>
                  ) : (
                    <p className="provider-note">
                      <Github size={16} /> GitHub sign-in awaits provider
                      configuration.
                    </p>
                  )}
                  <p className="auth-switch">
                    {mode === "login"
                      ? "New to CodeArena?"
                      : "Already have an account?"}{" "}
                    <Link href={mode === "login" ? "/register" : "/login"}>
                      {mode === "login" ? "Create an account" : "Sign in"}
                    </Link>
                  </p>
                  {mode === "login" && (
                    <Link className="text-link small" href="/verify-email">
                      Resend verification email
                    </Link>
                  )}
                </>
              )}
            </>
          )}
        </div>
        <div className="auth-footnote">
          <ShieldCheck size={14} /> Secure by design. Built for developers.
        </div>
      </main>
    </div>
  );
}
