export default function Chat() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-sage-200 bg-cream-50 px-4 py-3">
        <div className="mx-auto flex max-w-2xl items-center justify-between">
          <h1 className="text-lg font-semibold text-sage-800">人格织梦者</h1>
          <span className="rounded-full bg-sage-100 px-3 py-1 text-xs text-sage-600">
            正在建立连接...
          </span>
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center">
        <p className="text-sage-400">对话界面即将上线</p>
      </main>

      <footer className="border-t border-sage-200 bg-cream-50 px-4 py-3">
        <div className="mx-auto flex max-w-2xl">
          <input
            type="text"
            placeholder="输入你的想法..."
            disabled
            className="flex-1 rounded-xl border border-sage-200 bg-white px-4 py-3 text-sage-700 placeholder-sage-300"
          />
        </div>
      </footer>
    </div>
  );
}
