import { useParams } from "react-router-dom";

export default function Report() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <h1 className="mb-4 text-2xl font-bold text-sage-800">人格分析报告</h1>
      <p className="text-sage-400">报告 ID: {id}</p>
      <p className="mt-4 text-sage-400">报告功能即将上线</p>
    </div>
  );
}
