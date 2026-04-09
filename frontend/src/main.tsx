import { CopilotKitProvider, HttpAgent } from '@copilotkit/react-core/v2';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import '@copilotkit/react-ui/v2/styles.css';
import './index.css';
import App from './App.tsx';

const AGENT_URL = import.meta.env.VITE_AGENT_URL;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <CopilotKitProvider
      selfManagedAgents={{
        default: new HttpAgent({
          url: AGENT_URL,
        }),
      }}
    >
      <App />
    </CopilotKitProvider>
  </StrictMode>,
);
