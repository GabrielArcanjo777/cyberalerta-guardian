import Link from 'next/link'

export default function NotFound(){
  return (
    <section className="mx-auto max-w-3xl rounded-lg border border-slate-200 bg-white p-8 text-center shadow-[0_14px_36px_rgba(15,23,42,0.07)]">
      <div className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">404</div>
      <h1 className="mt-3 text-3xl font-black tracking-tight text-slate-950">Pagina nao encontrada</h1>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-600">
        A rota solicitada nao existe nesta demo do CyberAlerta Guardian.
      </p>
      <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
        <Link
          href="/"
          className="inline-flex min-h-11 items-center justify-center rounded-lg bg-slate-800 px-5 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2"
        >
          Voltar para Home
        </Link>
        <Link
          href="/before-pix"
          className="inline-flex min-h-11 items-center justify-center rounded-lg border border-slate-200 bg-white px-5 py-3 text-sm font-bold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:ring-offset-2"
        >
          Abrir Before Pix
        </Link>
      </div>
    </section>
  )
}
