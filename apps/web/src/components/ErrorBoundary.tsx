import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error in UI:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 m-4 bg-rose-950/40 border border-rose-800 rounded-xl text-rose-200">
          <h2 className="text-lg font-semibold mb-2">GIS Component Error</h2>
          <p className="text-sm text-rose-300 font-mono mb-4">
            {this.state.error?.message || 'An unexpected rendering error occurred.'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="px-4 py-2 bg-rose-700 hover:bg-rose-600 rounded text-xs font-semibold text-white transition-colors"
          >
            Retry Component
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
