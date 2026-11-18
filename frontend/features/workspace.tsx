"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  ArrowUpRight,
  Fingerprint,
  LayoutDashboard,
  Loader2,
  LogOut,
  Monitor,
  ShieldCheck,
  Sparkles,
  UserRound,
} from "lucide-react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui/button";
import { api, ApiError } from "@/services/api";
import type { User, Session } from "@/types/account";

export function Workspace() {
  const router = useRouter();
  const search = useSearchParams();
  const view = search.get("view") || "overview";
  const client = useQueryClient();
  const account = useQuery({
    queryKey: ["me"],
    queryFn: () => api<User>("/users/me"),
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (account.error instanceof ApiError && account.error.status === 401)
      router.replace("/login");
  }, [account.error, router]);
  async function logout() {
    setBusy(true);
    setError("");
    try {
      await api("/auth/logout", { method: "POST" });
      client.clear();
      router.replace("/login");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (account.isPending)
    return (
      <main id="main" className="loading-state" aria-busy="true">
        <Loader2 className="spin" />
        <p>Opening your workspace…</p>
      </main>
    );
  if (!account.data)
    return (
      <main id="main" className="loading-state">
        <h1>Unable to open your workspace.</h1>
        <p>{account.error?.message}</p>
        <Button onClick={() => account.refetch()}>Try again</Button>
        <Link href="/login" className="text-link">
          Go to sign in
        </Link>
      </main>
    );
  const user = account.data;
  return (
    <div className="workspace">
      <aside className="workspace-sidebar">
        <Brand />
        <span className="eyebrow">YOUR WORKSPACE</span>
        <nav className="workspace-nav" aria-label="Workspace navigation">
          {[
            ["overview", "Overview", LayoutDashboard],
            ["profile", "My profile", UserRound],
            ["security", "Security", ShieldCheck],
          ].map(([key, label, Icon]) => {
            const Symbol = Icon as typeof LayoutDashboard;
            return (
              <Link
                key={String(key)}
                className={view === key ? "selected" : ""}
                href={`/workspace?view=${key}`}
                aria-current={view === key ? "page" : undefined}
              >
                <Symbol size={17} />
                {String(label)}
              </Link>
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <Button variant="ghost" onClick={logout} disabled={busy}>
            <LogOut size={16} /> Sign out
          </Button>
          <p>
            FOUNDATION RELEASE · v0.1
            <br />
            Your next chapter starts here.
          </p>
        </div>
      </aside>
      <main id="main" className="workspace-main">
        <header className="workspace-header">
          <span>
            Workspace / <span className="role-label">{view}</span>
          </span>
          <div className="account-chip">
            <span className="avatar">
              {user.full_name
                .split(" ")
                .map((w) => w[0])
                .slice(0, 2)
                .join("")}
            </span>
            {user.full_name}
            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              disabled={busy}
              aria-label="Sign out"
            >
              <LogOut size={15} />
            </Button>
          </div>
        </header>
        <div className="workspace-content">
          {error && (
            <div className="alert alert-error" role="alert">
              {error}
            </div>
          )}
          {view === "profile" ? (
            <Profile user={user} />
          ) : view === "security" ? (
            <Security />
          ) : (
            <>
              <span className="eyebrow">YOUR DEVELOPER JOURNEY</span>
              <h1>
                Welcome{user.onboarded ? " back" : ""},{" "}
                {user.full_name.split(" ")[0]}.
              </h1>
              <p className="muted">
                A little curiosity. A little commitment. A whole lot of
                possibility.
              </p>
              {!user.onboarded && (
                <section className="welcome-banner">
                  <div>
                    <h2>First, make yourself at home.</h2>
                    <p>
                      Your account is verified. Add a little about yourself to
                      complete your developer profile.
                    </p>
                  </div>
                  <Button asChild>
                    <Link href="/workspace?view=profile">
                      Complete your profile <ArrowRight size={16} />
                    </Link>
                  </Button>
                </section>
              )}
              <div className="workspace-cards">
                <section className="panel">
                  <Fingerprint className="panel-icon" size={26} />
                  <h2>Your identity, verified.</h2>
                  <p>
                    This is your account foundation. Keep your details current
                    as your CodeArena journey grows.
                  </p>
                  <dl className="detail-list">
                    <div>
                      <dt>Account type</dt>
                      <dd className="role-label">{user.role}</dd>
                    </div>
                    <div>
                      <dt>Email status</dt>
                      <dd className="syntax-green">Verified</dd>
                    </div>
                    <div>
                      <dt>Country</dt>
                      <dd>{user.country}</dd>
                    </div>
                    <div>
                      <dt>Joined</dt>
                      <dd>
                        {new Date(user.created_at).toLocaleDateString(
                          undefined,
                          { month: "short", day: "numeric", year: "numeric" },
                        )}
                      </dd>
                    </div>
                  </dl>
                  <Link href="/workspace?view=profile" className="text-link">
                    Edit your profile <ArrowUpRight size={15} />
                  </Link>
                </section>
                <section className="panel">
                  <ShieldCheck className="panel-icon" size={26} />
                  <h2>A workspace you can trust.</h2>
                  <p>
                    View your active sessions, revoke access on another device,
                    or renew your current session. You’re in control.
                  </p>
                  <Link href="/workspace?view=security" className="text-link">
                    Manage account security <ArrowUpRight size={15} />
                  </Link>
                </section>
              </div>
              <div className="roadmap-note">
                <Sparkles size={19} />
                <p>
                  The arena is taking shape. Coding challenges, competitions and
                  performance insights arrive in later milestones.
                  <br />
                  <Link href="/#roadmap" className="text-link">
                    Explore the roadmap <ArrowUpRight size={13} />
                  </Link>
                </p>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

function Profile({ user }: { user: User }) {
  const client = useQueryClient();
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    const data = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const updated = await api<User>("/users/me/profile", {
        method: "PATCH",
        body: JSON.stringify(data),
      });
      client.setQueryData(["me"], updated);
      setMessage("Profile saved. You’re ready for your next chapter.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="workspace-heading">
        <span className="eyebrow">MAKE IT YOURS</span>
        <h1>Your developer profile.</h1>
        <p>Tell us a little about the person behind the code.</p>
      </div>
      <form className="profile-form" onSubmit={save}>
        <div className="panel">
          {[
            ["full_name", "Full name", user.full_name, 120],
            ["country", "Country", user.country, 80],
            [
              "institution",
              "Institution or company (optional)",
              user.institution,
              160,
            ],
          ].map(([name, label, value, max]) => (
            <div className="field" key={String(name)}>
              <label htmlFor={String(name)}>{label}</label>
              <input
                id={String(name)}
                name={String(name)}
                defaultValue={String(value)}
                required={name !== "institution"}
                minLength={name === "institution" ? 0 : 2}
                maxLength={Number(max)}
              />
            </div>
          ))}
          <div className="field">
            <label htmlFor="bio">About you (optional)</label>
            <textarea
              id="bio"
              name="bio"
              defaultValue={user.bio}
              maxLength={500}
              rows={4}
              placeholder="What are you curious about? What do you want to build?"
            />
          </div>
          <p className="field-help">
            Your email and role are managed separately from profile details.
          </p>
          {error && (
            <div className="alert alert-error" role="alert">
              {error}
            </div>
          )}
          {message && (
            <div className="alert alert-success" role="status">
              {message}
            </div>
          )}
          <Button disabled={busy}>
            {busy ? "Saving…" : "Save profile"}
            <ArrowRight size={16} />
          </Button>
        </div>
      </form>
    </>
  );
}

function Security() {
  const client = useQueryClient();
  const router = useRouter();
  const sessions = useQuery({
    queryKey: ["sessions"],
    queryFn: () => api<Session[]>("/auth/sessions"),
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  async function act(path: string, method: string, current = false) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await api(path, { method });
      if (current) {
        client.clear();
        router.replace("/login");
      } else {
        await client.invalidateQueries({ queryKey: ["sessions"] });
        setMessage(
          method === "POST"
            ? "Your session has been renewed."
            : "Session access revoked.",
        );
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="workspace-heading">
        <span className="eyebrow">STAY IN CONTROL</span>
        <h1>Account security.</h1>
        <p>Manage the devices that have access to your workspace.</p>
      </div>
      <section className="panel">
        <h2>Active sessions</h2>
        <p>
          Sessions expire after one hour. Renew your current session here, or
          revoke a device’s access immediately.
        </p>
        {sessions.isPending && (
          <div className="skeleton" aria-label="Loading sessions" />
        )}
        {sessions.error && (
          <div className="alert alert-error" role="alert">
            {sessions.error.message}
            <Button variant="ghost" onClick={() => sessions.refetch()}>
              Retry
            </Button>
          </div>
        )}
        <div className="session-list">
          {sessions.data?.map((s) => (
            <div className="session-item" key={s.id}>
              <Monitor size={19} />
              <div className="session-info">
                <h3>
                  {s.current ? "This browser" : "Browser session"}
                  {s.current && (
                    <span className="status available">CURRENT</span>
                  )}
                </h3>
                <p>{s.user_agent || "Browser details unavailable"}</p>
                <p>Expires {new Date(s.expires_at).toLocaleString()}</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                disabled={busy}
                onClick={() =>
                  act(`/auth/sessions/${s.id}`, "DELETE", s.current)
                }
              >
                Revoke{s.current ? " & sign out" : ""}
              </Button>
            </div>
          ))}
        </div>
        {error && (
          <div className="alert alert-error" role="alert">
            {error}
          </div>
        )}
        {message && (
          <div className="alert alert-success" role="status">
            {message}
          </div>
        )}
        <div className="security-toolbar">
          <Button
            variant="outline"
            disabled={busy}
            onClick={() => act("/auth/refresh", "POST")}
          >
            Renew current session
          </Button>
          <Button variant="ghost" asChild>
            <Link href="/forgot-password">
              Reset password <ArrowUpRight size={15} />
            </Link>
          </Button>
        </div>
      </section>
    </>
  );
}
