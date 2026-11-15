"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type DashboardStats } from "@/lib/api";
import { Notice, PageHeader, Panel } from "@/components/ui";

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [company, setCompany] = useState<{ company_name: string; product_name: string; tagline: string; founder_role: string; industry: string; market: string; business_model: string } | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([
      api<DashboardStats>("/dashboard/stats"),
      api<typeof company>("/company"),
    ]).then(([dashboard, config]) => { setStats(dashboard); setCompany(config); }).catch((e: unknown) => setError(e instanceof Error ? e.message : "Gagal memuat overview."));
  }, []);
  const cards = stats ? [
    ["AI Employees", String(stats.total_employees), `${stats.active_employees} active`],
    ["Departments", String(stats.total_departments), "terdaftar di database"],
    ["Tasks", String(stats.total_tasks), `${stats.completed_tasks} completed`],
    ["Ongoing Projects", String(stats.ongoing_projects), "status active"],
  ] : [];
  return <>
    <PageHeader title="Company overview" description={company?.tagline ?? "Ringkasan operasional Aivanta Labs."} />
    {error && <div className="mt-6"><Notice error>{error}</Notice></div>}
    {!stats && !error && <div className="mt-6"><Notice>Memuat statistik dari API...</Notice></div>}
    <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{cards.map(([title, value, detail]) => <article key={title} className="rounded-2xl border border-[#1b2b40] bg-[#0d1a2b] p-5"><p className="text-sm text-slate-400">{title}</p><p className="mt-3 text-3xl font-semibold">{value}</p><p className="mt-2 text-xs text-slate-500">{detail}</p></article>)}</div>
    <nav aria-label="Workforce" className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">{[["AI Employees", "/employees"], ["Departments", "/departments"], ["Tasks", "/tasks"], ["Projects", "/projects"]].map(([label, href]) => <Link key={href} href={href} className="rounded-xl border border-[#1b2b40] bg-[#0d1a2b] px-4 py-3 text-sm text-cyan-200 hover:border-cyan-500/50">Kelola {label} →</Link>)}</nav>
    <div className="mt-5 grid gap-5 xl:grid-cols-[1.5fr_1fr]">
      <Panel><h2 className="font-semibold">Company profile</h2><p className="mt-1 text-sm text-slate-400">Informasi workspace tersimpan</p>{company ? <dl className="mt-6 space-y-4 text-sm">{[["Company", company.company_name], ["Product", company.product_name], ["Founder", company.founder_role], ["Industry", company.industry], ["Market", company.market], ["Business model", company.business_model]].map(([label, value]) => <div key={label} className="flex justify-between gap-4 border-b border-[#1b2b40] pb-3 last:border-0"><dt className="text-slate-400">{label}</dt><dd className="text-right text-slate-200">{value}</dd></div>)}</dl> : <p className="mt-5 text-sm text-slate-500">Memuat company profile...</p>}</Panel>
      <Panel><div className="flex items-center justify-between"><div><h2 className="font-semibold">Data status</h2><p className="mt-1 text-sm text-slate-400">Angka hanya tampil dari database.</p></div><span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">API-backed</span></div><div className="mt-6 space-y-4"><Check label="Backend API" detail="Data workforce dimuat dari FastAPI" /><Check label="SQLite database" detail="Statistik diperoleh dari data tersimpan" /><Check label="AI Gateway" detail="Belum diaktifkan; bukan bagian Phase 2" off /></div></Panel>
    </div>
    <p className="mt-8 text-xs text-slate-500">{company?.product_name ?? "Aivanta OS"} · Workforce Management · Tidak ada angka placeholder.</p>
  </>;
}
function Check({ label, detail, off = false }: { label: string; detail: string; off?: boolean }) { return <div className="flex justify-between gap-3 border-b border-[#1b2b40] pb-4 last:border-0 last:pb-0"><div><p className="text-sm font-medium">{label}</p><p className="mt-1 text-xs text-slate-400">{detail}</p></div><span className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${off ? "bg-slate-600" : "bg-emerald-400"}`} /></div>; }
