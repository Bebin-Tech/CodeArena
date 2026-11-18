import { JSDOM } from "jsdom";
import { test } from "node:test";
import assert from "node:assert/strict";
import React from "react";
import { registrationSchema, password } from "../lib/validation";

const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "http://localhost/",
});
Object.defineProperty(globalThis, "window", {
  value: dom.window,
  configurable: true,
});
Object.defineProperty(globalThis, "document", {
  value: dom.window.document,
  configurable: true,
});
Object.defineProperty(globalThis, "navigator", {
  value: dom.window.navigator,
  configurable: true,
});
Object.assign(globalThis, {
  self: dom.window,
  HTMLElement: dom.window.HTMLElement,
  MutationObserver: dom.window.MutationObserver,
});

test("registration validation rejects weak passwords and privileged roles", () => {
  const valid = {
    full_name: "Arena Developer",
    email: "dev@example.com",
    country: "India",
    institution: "",
    user_type: "developer",
    password: "Valid-password-123",
  };
  assert.equal(registrationSchema.safeParse(valid).success, true);
  assert.equal(
    registrationSchema.safeParse({ ...valid, user_type: "super_admin" })
      .success,
    false,
  );
  assert.equal(
    registrationSchema.safeParse({ ...valid, email: "invalid" }).success,
    false,
  );
  assert.equal(password.safeParse("longbutnonumbers").success, false);
  assert.equal(password.safeParse("short1").success, false);
});

test("button prevents interaction while disabled and supports a semantic link", async () => {
  const { render, fireEvent, cleanup } = await import("@testing-library/react");
  const { Button } = await import("../components/ui/button");
  let clicks = 0;
  const view = render(
    <Button disabled onClick={() => clicks++}>
      Saving profile
    </Button>,
  );
  const button = view.getByRole("button", { name: "Saving profile" });
  fireEvent.click(button);
  assert.equal(clicks, 0);
  cleanup();
  const link = render(
    <Button asChild variant="outline">
      <a href="/register">Join the arena</a>
    </Button>,
  );
  assert.equal(
    link.getByRole("link", { name: "Join the arena" }).getAttribute("href"),
    "/register",
  );
  cleanup();
});

test("account form exposes validation and accessible password visibility", async () => {
  const { render, fireEvent, waitFor, cleanup } =
    await import("@testing-library/react");
  const { QueryClient, QueryClientProvider } =
    await import("@tanstack/react-query");
  const { AppRouterContext } =
    await import("next/dist/shared/lib/app-router-context.shared-runtime");
  const { SearchParamsContext } =
    await import("next/dist/shared/lib/hooks-client-context.shared-runtime");
  const { AuthScreen } = await import("../features/auth-screen");
  const previousFetch = globalThis.fetch;
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ github: false }), { status: 200 });
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  const router = {
    bfcacheId: "test",
    back() {},
    forward() {},
    refresh() {},
    push() {},
    replace() {},
    prefetch: async () => {},
    hmrRefresh() {},
  };
  try {
    const view = render(
      <AppRouterContext.Provider value={router}>
        <SearchParamsContext.Provider value={new URLSearchParams()}>
          <QueryClientProvider client={queryClient}>
            <AuthScreen mode="register" />
          </QueryClientProvider>
        </SearchParamsContext.Provider>
      </AppRouterContext.Provider>,
    );
    fireEvent.click(view.getByRole("button", { name: "Create account" }));
    await waitFor(() => assert.ok(view.getByText("Enter your full name.")));
    assert.equal(
      view.getByLabelText("Full name").getAttribute("aria-invalid"),
      "true",
    );
    assert.equal(
      view.getByLabelText("Password", { exact: true }).getAttribute("type"),
      "password",
    );
    fireEvent.click(view.getByRole("button", { name: "Show password" }));
    assert.equal(
      view.getByLabelText("Password", { exact: true }).getAttribute("type"),
      "text",
    );
    assert.ok(view.getByRole("button", { name: "Hide password" }));
  } finally {
    cleanup();
    queryClient.clear();
    globalThis.fetch = previousFetch;
  }
});
