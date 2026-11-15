"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const links = [
  { href: "/", label: "Overview", exact: true },
  { href: "/employees", label: "AI Employees" },
  { href: "/departments", label: "Departments" },
  { href: "/tasks", label: "Tasks" },
  { href: "/projects", label: "Projects" },
];

export function Shell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return <main className="min-h-screen md:flex">
    <aside className="border-b border-[#1b2b40] bg-[#091525] p-5 md:sticky md:top-0 md:h-screen md:w-64 md:shrink-0 md:border-b-0 md:border-r">
      <Link href="/" className="text-lg font-bold tracking-wide">AIVANTA<span className="text-cyan-300"> OS</span></Link>
      <p className="mt-1 text-xs text-slate-400">Aivanta Labs · CEO workspace</p>
      <nav aria-label="Navigasi utama" className="mt-8 flex gap-2 overflow-x-auto md:flex-col">
        {links.map((link) => {
          const active = link.exact ? pathname === link.href : pathname.startsWith(link.href);
          return <Link key={link.href} href={link.href} className={`whitespace-nowrap rounded-lg px-3 py-2 text-sm transition ${active ? "bg-cyan-400/10 text-cyan-200" : "text-slate-400 hover:bg-white/5 hover:text-slate-100"}`}>{link.label}</Link>;
        })}
      </nav>
      <div className="mt-8 hidden rounded-xl border border-[#1b2b40] p-3 text-xs text-slate-400 md:block"><p className="font-semibold text-slate-200">AI gateway</p><p className="mt-2">Belum diaktifkan · Phase 3</p></div>
    </aside>
    <section className="mx-auto w-full max-w-7xl p-5 md:p-9">{children}</section>
  </main>;
}
