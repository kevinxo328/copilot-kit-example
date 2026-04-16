import { CopilotChat } from '@copilotkit/react-core/v2';

export default function Page() {
  return (
    <main>
      <CopilotChat agentId="default" className="min-h-dvh" />
    </main>
  );
}
