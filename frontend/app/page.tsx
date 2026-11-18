import Link from "next/link";
import {
  ArrowRight,
  ArrowUpRight,
  Braces,
  Check,
  Code2,
  Fingerprint,
  Github,
  Layers3,
  ShieldCheck,
  Sparkles,
  Terminal,
  Trophy,
} from "lucide-react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui/button";
export default function Home() {
  return (
    <div className="site">
      <header className="site-header">
        <Brand />
        <nav aria-label="Main navigation">
          <a href="#the-arena">The platform</a>
          <a href="#roadmap">What’s next</a>
          <Link href="/login">Sign in</Link>
          <Button asChild size="sm">
            <Link href="/register">
              Join the arena <ArrowUpRight size={16} />
            </Link>
          </Button>
        </nav>
      </header>
      <main id="main">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="live-dot" /> YOUR NEXT CHAPTER IN CODE
            </div>
            <h1>
              Built for the
              <br />
              way you <span>think.</span>
            </h1>
            <p className="hero-subtitle">Compete. Code. Prove your skills.</p>
            <p className="hero-description">
              A home for the problems you can’t stop thinking about. Build your
              developer identity today. Your arena is taking shape.
            </p>
            <div className="hero-actions">
              <Button asChild>
                <Link href="/register">
                  Create your account <ArrowRight size={18} />
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <a href="#the-arena">Explore CodeArena</a>
              </Button>
            </div>
            <div className="hero-note">
              <ShieldCheck size={15} /> Free account. Built around your
              progress.
            </div>
          </div>
          <div
            className="hero-visual"
            aria-label="Illustrative Python code, not a live editor"
          >
            <div className="orbital orbital-one" />
            <div className="orbital orbital-two" />
            <div className="code-window">
              <div className="window-top">
                <div className="window-dots">
                  <i />
                  <i />
                  <i />
                </div>
                <span>your_next_challenge.py</span>
                <Code2 size={15} />
              </div>
              <div className="code-tab">
                <span>
                  <span className="python-dot" /> solution.py
                </span>
                <span>PYTHON 3</span>
              </div>
              <div className="code-body">
                <div className="line-numbers">
                  1<br />2<br />3<br />4<br />5<br />6<br />7<br />8<br />9
                  <br />
                  10
                </div>
                <pre>
                  <code>
                    <span className="syntax-muted">
                      # Every great solution starts here.
                    </span>
                    {"\n\n"}
                    <span className="syntax-violet">def</span>{" "}
                    <span className="syntax-blue">find_your_edge</span>(skills):
                    {"\n"}
                    {"    "}mindset ={" "}
                    <span className="syntax-green">"keep building"</span>
                    {"\n\n"}
                    {"    "}
                    <span className="syntax-violet">for</span> challenge{" "}
                    <span className="syntax-violet">in</span> skills:{"\n"}
                    {"        "}learn(challenge){"\n"}
                    {"        "}grow(){"\n\n"}
                    {"    "}
                    <span className="syntax-violet">return</span>{" "}
                    your_next_chapter
                    <span className="cursor" />
                  </code>
                </pre>
              </div>
              <div className="terminal-row">
                <Terminal size={14} />
                <span>
                  Ready for what’s next<span className="syntax-green">_</span>
                </span>
                <span className="illustration-label">ILLUSTRATION</span>
              </div>
            </div>
            <div className="floating-tag">
              <span className="tag-icon">
                <Braces size={20} />
              </span>
              <div>
                Your potential<span>Without limits.</span>
              </div>
              <ArrowUpRight size={18} />
            </div>
            <div className="visual-caption">
              THINK CLEARLY. BUILD BOLDLY. KEEP GOING.
            </div>
          </div>
        </section>
        <section id="the-arena" className="platform-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">
                ONE IDENTITY. ENDLESS POSSIBILITY.
              </span>
              <h2>Make room for your next level.</h2>
            </div>
            <p>
              A foundation for developers,
              <br />
              and the teams that believe in them.
            </p>
          </div>
          <div className="feature-grid">
            <article className="feature-card">
              <div className="feature-icon">
                <Fingerprint />
              </div>
              <span className="status available">
                <Check size={12} /> AVAILABLE NOW
              </span>
              <h3>Your developer identity</h3>
              <p>
                Create a verified account, shape your profile, and manage your
                sessions in one secure workspace.
              </p>
              <Link href="/register">
                Make it yours <ArrowUpRight size={16} />
              </Link>
            </article>
            <article className="feature-card">
              <div className="feature-icon blue">
                <Code2 />
              </div>
              <span className="status">MILESTONE 3</span>
              <h3>Arena & Code Studio</h3>
              <p>
                A focused coding environment, thoughtful challenges, and
                isolated evaluation. Next on the roadmap.
              </p>
              <a href="#roadmap">
                View the roadmap <ArrowUpRight size={16} />
              </a>
            </article>
            <article className="feature-card">
              <div className="feature-icon amber">
                <Trophy />
              </div>
              <span className="status">MILESTONE 5</span>
              <h3>Competition with purpose</h3>
              <p>
                Live standings, meaningful challenges, and a chance to measure
                the progress you’ve earned.
              </p>
              <a href="#roadmap">
                See what’s ahead <ArrowUpRight size={16} />
              </a>
            </article>
          </div>
        </section>
        <section id="roadmap" className="roadmap">
          <div>
            <span className="eyebrow">BUILT WITH INTENTION</span>
            <h2>
              A strong foundation.
              <br />
              An ambitious roadmap.
            </h2>
            <p>
              We’re building CodeArena in tested milestones.
              <br />
              Here’s exactly where things stand.
            </p>
          </div>
          <ol>
            <li className="active">
              <span>01</span>
              <div>
                <h3>Identity & foundations</h3>
                <p>Accounts, verification, profiles and session security.</p>
              </div>
              <span className="status available">CURRENT RELEASE</span>
            </li>
            <li>
              <span>02</span>
              <div>
                <h3>Developer workspaces</h3>
                <p>Organizations, permissions and real progress insights.</p>
              </div>
              <Layers3 size={19} />
            </li>
            <li>
              <span>03—05</span>
              <div>
                <h3>Practice. Compete. Progress.</h3>
                <p>Code Studio, secure evaluation and competitions.</p>
              </div>
              <Trophy size={19} />
            </li>
            <li>
              <span>06—09</span>
              <div>
                <h3>Intelligence & opportunity</h3>
                <p>AI, collaboration, hiring and institutional tools.</p>
              </div>
              <Sparkles size={19} />
            </li>
          </ol>
        </section>
        <section className="bottom-cta">
          <span className="eyebrow">YOUR STORY STARTS WITH A COMMIT.</span>
          <h2>
            Bring your curiosity.
            <br />
            We’ll build the arena.
          </h2>
          <Button asChild>
            <Link href="/register">
              Get started <ArrowRight size={18} />
            </Link>
          </Button>
        </section>
      </main>
      <footer className="site-footer">
        <Brand />
        <span>Compete. Code. Prove Your Skills.</span>
        <span>© {new Date().getFullYear()} CodeArena</span>
      </footer>
    </div>
  );
}
