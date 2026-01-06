/**
 * Agent Tester Component
 *
 * A simple UI to test the agent system. Drop this into any page to test.
 *
 * Copy to: spokestack/src/components/agents/AgentTester.tsx
 *
 * Usage:
 *   import { AgentTester } from '@/components/agents/AgentTester';
 *   <AgentTester />
 */

'use client';

import { useState, useEffect } from 'react';

interface Issue {
  id: string;
  title: string;
  status: string;
  jobId?: string;
}

interface JobStatus {
  id: string;
  status: string;
  job?: {
    id: string;
    agentType: string;
    status: string;
    logs: Array<{ level: string; message: string; timestamp: string }>;
    result?: any;
    error?: string;
  };
}

export function AgentTester() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState<'BUG' | 'FEATURE' | 'TASK'>('BUG');
  const [module, setModule] = useState('');
  const [priority, setPriority] = useState<'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'>('MEDIUM');

  const [submitting, setSubmitting] = useState(false);
  const [currentIssue, setCurrentIssue] = useState<Issue | null>(null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll for status updates
  useEffect(() => {
    if (!currentIssue?.id) return;

    const pollStatus = async () => {
      try {
        const res = await fetch(`/api/agents/${currentIssue.id}`);
        if (res.ok) {
          const data = await res.json();
          setStatus(data);

          // Stop polling if completed or failed
          if (['COMPLETED', 'FAILED', 'CANCELLED'].includes(data.status)) {
            return;
          }
        }
      } catch (err) {
        console.error('Status poll error:', err);
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [currentIssue?.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    setCurrentIssue(null);
    setStatus(null);

    try {
      const res = await fetch('/api/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type,
          title,
          description,
          priority,
          context: module ? { module } : {},
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Failed to submit');
      }

      setCurrentIssue({
        id: data.id,
        title,
        status: data.status,
        jobId: data.jobId,
      });

      // Clear form
      setTitle('');
      setDescription('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>🤖 Agent System Tester</h2>

      {/* Submit Form */}
      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.row}>
          <label style={styles.label}>
            Type
            <select
              value={type}
              onChange={(e) => setType(e.target.value as any)}
              style={styles.select}
            >
              <option value="BUG">Bug</option>
              <option value="FEATURE">Feature</option>
              <option value="TASK">Task</option>
            </select>
          </label>

          <label style={styles.label}>
            Priority
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as any)}
              style={styles.select}
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </label>

          <label style={styles.label}>
            Module (optional)
            <select
              value={module}
              onChange={(e) => setModule(e.target.value)}
              style={styles.select}
            >
              <option value="">Auto-detect</option>
              <option value="briefs">Briefs</option>
              <option value="time">Time Tracking</option>
              <option value="crm">CRM</option>
              <option value="studio">Studio</option>
              <option value="lms">LMS</option>
              <option value="boards">Boards</option>
              <option value="analytics">Analytics</option>
            </select>
          </label>
        </div>

        <label style={styles.label}>
          Title
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Brief title of the issue"
            required
            style={styles.input}
          />
        </label>

        <label style={styles.label}>
          Description
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the issue in detail..."
            required
            rows={4}
            style={styles.textarea}
          />
        </label>

        <button
          type="submit"
          disabled={submitting}
          style={{
            ...styles.button,
            opacity: submitting ? 0.7 : 1,
          }}
        >
          {submitting ? '⏳ Submitting...' : '🚀 Submit to Agent'}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div style={styles.error}>
          ❌ {error}
        </div>
      )}

      {/* Status Display */}
      {currentIssue && (
        <div style={styles.statusContainer}>
          <h3 style={styles.statusHeader}>
            Issue: {currentIssue.title}
          </h3>

          <div style={styles.statusBadge}>
            {getStatusEmoji(status?.status || currentIssue.status)}{' '}
            {status?.status || currentIssue.status}
          </div>

          {status?.job && (
            <div style={styles.jobInfo}>
              <p><strong>Agent:</strong> {status.job.agentType}</p>
              <p><strong>Job Status:</strong> {status.job.status}</p>

              {/* Logs */}
              {status.job.logs && status.job.logs.length > 0 && (
                <div style={styles.logs}>
                  <strong>Recent Logs:</strong>
                  <div style={styles.logList}>
                    {status.job.logs.slice(0, 10).map((log, i) => (
                      <div key={i} style={styles.logEntry}>
                        <span style={styles.logLevel}>{log.level}</span>
                        <span style={styles.logMessage}>{log.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Result */}
              {status.job.result && (
                <div style={styles.result}>
                  <strong>Result:</strong>
                  <pre style={styles.resultPre}>
                    {JSON.stringify(status.job.result, null, 2)}
                  </pre>
                </div>
              )}

              {/* Error */}
              {status.job.error && (
                <div style={styles.jobError}>
                  <strong>Error:</strong> {status.job.error}
                </div>
              )}
            </div>
          )}

          {/* Feedback Form (show when completed) */}
          {status?.status === 'COMPLETED' && status.job && (
            <FeedbackForm jobId={status.job.id} />
          )}
        </div>
      )}

      {/* Health Check */}
      <HealthCheck />
    </div>
  );
}

// ============================================
// FEEDBACK FORM
// ============================================

function FeedbackForm({ jobId }: { jobId: string }) {
  const [rating, setRating] = useState(0);
  const [outcome, setOutcome] = useState('');
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!rating || !outcome) return;

    setSubmitting(true);
    try {
      const res = await fetch('/api/agents/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jobId,
          rating,
          outcome,
          comment: comment || undefined,
        }),
      });

      if (res.ok) {
        setSubmitted(true);
      }
    } catch (err) {
      console.error('Feedback error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div style={styles.feedbackSuccess}>
        ✅ Thanks for your feedback!
      </div>
    );
  }

  return (
    <div style={styles.feedbackForm}>
      <h4>How did the agent do?</h4>

      {/* Rating */}
      <div style={styles.ratingRow}>
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => setRating(star)}
            style={{
              ...styles.starButton,
              color: star <= rating ? '#fbbf24' : '#d1d5db',
            }}
          >
            ★
          </button>
        ))}
      </div>

      {/* Outcome */}
      <div style={styles.outcomeRow}>
        {[
          { value: 'SOLVED', label: '✅ Solved' },
          { value: 'PARTIAL', label: '🟡 Partial' },
          { value: 'NOT_SOLVED', label: '❌ Not Solved' },
          { value: 'MADE_WORSE', label: '💥 Made Worse' },
        ].map((opt) => (
          <button
            key={opt.value}
            onClick={() => setOutcome(opt.value)}
            style={{
              ...styles.outcomeButton,
              backgroundColor: outcome === opt.value ? '#3b82f6' : '#e5e7eb',
              color: outcome === opt.value ? 'white' : 'black',
            }}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Comment */}
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Any additional feedback? (optional)"
        rows={2}
        style={styles.feedbackTextarea}
      />

      <button
        onClick={handleSubmit}
        disabled={!rating || !outcome || submitting}
        style={{
          ...styles.feedbackSubmit,
          opacity: !rating || !outcome ? 0.5 : 1,
        }}
      >
        {submitting ? 'Submitting...' : 'Submit Feedback'}
      </button>
    </div>
  );
}

// ============================================
// HEALTH CHECK
// ============================================

function HealthCheck() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetch('/api/agents/health')
      .then((res) => res.json())
      .then(setHealth)
      .catch(console.error);
  }, []);

  if (!health) return null;

  return (
    <div style={styles.healthContainer}>
      <h4>System Health</h4>
      <div style={styles.healthStatus}>
        <span
          style={{
            ...styles.healthDot,
            backgroundColor:
              health.status === 'healthy'
                ? '#22c55e'
                : health.status === 'degraded'
                ? '#f59e0b'
                : '#ef4444',
          }}
        />
        {health.status} • v{health.version?.version}
      </div>
      <div style={styles.healthChecks}>
        {Object.entries(health.checks || {}).map(([key, value]) => (
          <span key={key} style={styles.healthCheck}>
            {value ? '✅' : '❌'} {key}
          </span>
        ))}
      </div>
      {health.jobs && (
        <div style={styles.healthStats}>
          Jobs: {health.jobs.running} running, {health.jobs.pending} pending,{' '}
          {health.jobs.completedToday} completed today
        </div>
      )}
    </div>
  );
}

// ============================================
// HELPERS
// ============================================

function getStatusEmoji(status: string): string {
  const emojis: Record<string, string> = {
    PENDING: '⏳',
    QUEUED: '📋',
    PROCESSING: '⚙️',
    REVIEW: '👀',
    COMPLETED: '✅',
    FAILED: '❌',
    CANCELLED: '🚫',
  };
  return emojis[status] || '❓';
}

// ============================================
// STYLES
// ============================================

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: 700,
    margin: '0 auto',
    padding: 24,
    fontFamily: 'system-ui, sans-serif',
  },
  header: {
    marginBottom: 24,
    fontSize: 24,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
    marginBottom: 24,
  },
  row: {
    display: 'flex',
    gap: 16,
  },
  label: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
    fontSize: 14,
    fontWeight: 500,
    flex: 1,
  },
  input: {
    padding: '8px 12px',
    borderRadius: 6,
    border: '1px solid #d1d5db',
    fontSize: 14,
  },
  select: {
    padding: '8px 12px',
    borderRadius: 6,
    border: '1px solid #d1d5db',
    fontSize: 14,
  },
  textarea: {
    padding: '8px 12px',
    borderRadius: 6,
    border: '1px solid #d1d5db',
    fontSize: 14,
    resize: 'vertical',
  },
  button: {
    padding: '12px 24px',
    borderRadius: 6,
    border: 'none',
    backgroundColor: '#3b82f6',
    color: 'white',
    fontSize: 16,
    fontWeight: 600,
    cursor: 'pointer',
  },
  error: {
    padding: 12,
    borderRadius: 6,
    backgroundColor: '#fef2f2',
    color: '#dc2626',
    marginBottom: 16,
  },
  statusContainer: {
    padding: 16,
    borderRadius: 8,
    border: '1px solid #e5e7eb',
    marginBottom: 24,
  },
  statusHeader: {
    margin: '0 0 12px 0',
    fontSize: 18,
  },
  statusBadge: {
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: 9999,
    backgroundColor: '#f3f4f6',
    fontSize: 14,
    fontWeight: 500,
    marginBottom: 16,
  },
  jobInfo: {
    fontSize: 14,
  },
  logs: {
    marginTop: 12,
  },
  logList: {
    marginTop: 8,
    maxHeight: 200,
    overflow: 'auto',
    backgroundColor: '#f9fafb',
    borderRadius: 6,
    padding: 8,
  },
  logEntry: {
    display: 'flex',
    gap: 8,
    fontSize: 12,
    fontFamily: 'monospace',
    padding: '2px 0',
  },
  logLevel: {
    fontWeight: 600,
    minWidth: 50,
  },
  logMessage: {
    color: '#4b5563',
  },
  result: {
    marginTop: 12,
  },
  resultPre: {
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 6,
    fontSize: 12,
    overflow: 'auto',
    maxHeight: 200,
  },
  jobError: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#fef2f2',
    borderRadius: 6,
    color: '#dc2626',
  },
  feedbackForm: {
    marginTop: 16,
    padding: 16,
    backgroundColor: '#f9fafb',
    borderRadius: 8,
  },
  ratingRow: {
    display: 'flex',
    gap: 4,
    marginBottom: 12,
  },
  starButton: {
    background: 'none',
    border: 'none',
    fontSize: 28,
    cursor: 'pointer',
  },
  outcomeRow: {
    display: 'flex',
    gap: 8,
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  outcomeButton: {
    padding: '6px 12px',
    borderRadius: 6,
    border: 'none',
    cursor: 'pointer',
    fontSize: 12,
  },
  feedbackTextarea: {
    width: '100%',
    padding: 8,
    borderRadius: 6,
    border: '1px solid #d1d5db',
    marginBottom: 12,
    fontSize: 14,
    resize: 'vertical',
  },
  feedbackSubmit: {
    padding: '8px 16px',
    borderRadius: 6,
    border: 'none',
    backgroundColor: '#22c55e',
    color: 'white',
    cursor: 'pointer',
    fontSize: 14,
  },
  feedbackSuccess: {
    marginTop: 16,
    padding: 12,
    backgroundColor: '#f0fdf4',
    borderRadius: 6,
    color: '#16a34a',
  },
  healthContainer: {
    padding: 16,
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    fontSize: 14,
  },
  healthStatus: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  healthDot: {
    width: 10,
    height: 10,
    borderRadius: '50%',
  },
  healthChecks: {
    display: 'flex',
    gap: 12,
    marginBottom: 8,
  },
  healthCheck: {
    fontSize: 12,
  },
  healthStats: {
    fontSize: 12,
    color: '#6b7280',
  },
};

export default AgentTester;
